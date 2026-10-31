#!/usr/bin/env python3
"""Check a Fusion script's API names offline, against this Mac's own Fusion.

    python3 tools/fusion/check_api.py my_drawing_script.py [more.py ...]

A wrong API name only shows when the script runs inside Fusion, and every
failed run costs a turn in the shared Fusion queue. This reads Fusion's own
Python API files from its install (nothing is sent to Fusion, Fusion need not
run) and type-checks the scripts with mypy:

- Fusion ships two sets of files: the definitions for code completion
  (packages/adsk/defs) and the real wrapper (packages/adsk/*.py). The
  definitions leave out members that work but are "not officially supported"
  (for example Drawing.sheets), so this adds every member the wrapper has to
  a copy of the definitions first.
- It reports only name errors in the given scripts: an attribute or method
  that doesn't exist (attr-defined), a call with the wrong arguments
  (call-arg), an unknown name (name-defined).
- Types flow from what the script gets from the API. A helper function whose
  parameters have no types gets them from the calls to it in the same script
  (a helper called from a helper too), so its body is checked without adding
  types. A helper nobody calls with a known API object stays unchecked on its
  parameters; annotate those (def extent(view: "adsk.drawing.View")).

Needs mypy (python3 -m pip install mypy into a virtual environment in your
session folder, then run this with that environment's python). Exit 0 clean,
1 name errors found, 2 can't run (no Fusion install or no mypy).
"""

import argparse
import ast
import glob
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tokenize
import uuid
import warnings

INSTALL_GLOB = os.path.expanduser(
    "~/Library/Application Support/Autodesk/webdeploy/production/*/Autodesk Fusion.app/"
    "Contents/Api/Python/packages/adsk")
MODULES = ("core", "fusion", "drawing", "cam")
CODES = ("attr-defined", "call-arg", "name-defined")

CLASS_RE = re.compile(r"^class (\w+)\((.*)\):")
DEF_RE = re.compile(r"^    def (\w+)\((.*?)\)\s*->\s*\"([^\"]+)\"\s*:")
PROP_RE = re.compile(r"^(\w+)\.(\w+) = property\((\w+)\._get_\w+(\s*,\s*\w+\._set_\w+)?")
CONST_RE = re.compile(r"^    (\w+) = _\w+\.\w+$")


def find_install(pattern=INSTALL_GLOB):
    """The newest install that has both the wrapper and the definitions."""
    found = [p for p in glob.glob(pattern)
             if os.path.isfile(os.path.join(p, "drawing.py"))
             and os.path.isdir(os.path.join(p, "defs", "adsk"))]
    return max(found, key=lambda p: os.path.getmtime(os.path.join(p, "drawing.py"))) if found else None


def wrapper_members(path):
    """{class: {"bases": str, "props": {name: (type, settable)}, "methods": {name: type},
    "consts": set}} from one wrapper module."""
    classes, cur, getters = {}, None, {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = CLASS_RE.match(line)
            if m:
                cur = m.group(1)
                classes[cur] = {"bases": m.group(2), "props": {}, "methods": {}, "consts": set(),
                                "getters": {}}
                getters = classes[cur]["getters"]
                continue
            if not line.strip():
                continue
            if not line[0].isspace():              # top level: the class body is over
                cur = None
                p = PROP_RE.match(line)
                if p and p.group(1) in classes:
                    c = classes[p.group(1)]
                    c["props"][p.group(2)] = (c["getters"].get("_get_" + p.group(2), "object"),
                                              bool(p.group(4)))
                continue
            if cur is None:
                continue
            d = DEF_RE.match(line)
            if d:
                name, typ = d.group(1), d.group(3)
                if name.startswith(("_get_", "_set_")):
                    getters[name] = typ
                elif not name.startswith("_"):
                    classes[cur]["methods"][name] = typ
                continue
            k = CONST_RE.match(line.rstrip("\n"))
            if k:
                classes[cur]["consts"].add(k.group(1))
    return classes


def stub_members(src):
    """{class: (set of member names, end line)} from a definitions module."""
    out = {}
    with warnings.catch_warnings():          # the definitions have stray backslashes in docstrings
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            names = set()
            for b in node.body:
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(b.name)
                elif isinstance(b, ast.Assign):
                    names.update(t.id for t in b.targets if isinstance(t, ast.Name))
                elif isinstance(b, ast.AnnAssign) and isinstance(b.target, ast.Name):
                    names.add(b.target.id)
            out[node.name] = (names, node.end_lineno)
    return out


def _ann(typ):
    t = typ.strip()
    if t in ("void", ""):
        return "None"
    return '"%s"' % t if t.startswith("adsk.") else ('"%s"' % t if re.match(r"^[\w.\[\], ]+$", t) else "Any")


def complete_definitions(install, out_dir):
    """Copy the definitions to out_dir/adsk with every wrapper member added.
    Returns how many members were added."""
    dst = os.path.join(out_dir, "adsk")
    shutil.copytree(os.path.join(install, "defs", "adsk"), dst)
    added = 0
    for mod in MODULES:
        wpath, spath = os.path.join(install, mod + ".py"), os.path.join(dst, mod + ".py")
        if not (os.path.isfile(wpath) and os.path.isfile(spath)):
            continue
        with open(spath, encoding="utf-8") as fh:
            src = fh.read()
        have = stub_members(src)
        lines = src.splitlines()
        inserts, new_classes = [], []
        for cls, w in wrapper_members(wpath).items():
            if cls.startswith("_"):
                continue
            extra = []
            names = have.get(cls, (set(), None))[0]
            for name, (typ, settable) in sorted(w["props"].items()):
                if name not in names:
                    extra.append("    @property\n    def %s(self) -> %s: ..." % (name, _ann(typ)))
                    if settable:
                        extra.append("    @%s.setter\n    def %s(self, value: Any) -> None: ..." % (name, name))
            for name, typ in sorted(w["methods"].items()):
                if name not in names and name not in w["props"]:
                    extra.append("    @staticmethod\n    def %s(*args: Any, **kwargs: Any) -> %s: ..." % (name, _ann(typ)))
            for name in sorted(w["consts"]):
                if name not in names:
                    extra.append("    %s: int = 0" % name)
            if not extra:
                continue
            added += len(extra)
            if cls in have:
                inserts.append((have[cls][1], extra))
            else:
                base = w["bases"] if w["bases"] and w["bases"] != "object" else "object"
                new_classes.append("class %s(%s):\n%s" % (cls, base, "\n".join(extra)))
        for end, extra in sorted(inserts, reverse=True):
            lines[end:end] = ["    # added from Fusion's wrapper (works, not in the definitions)"] + extra
        head = "from typing import Any\nimport adsk.core\nimport adsk.fusion\nimport adsk.drawing\n"
        body = "\n".join(lines)
        # after the __future__ import, which must stay first
        fut = "from __future__ import annotations\n"
        body = body.replace(fut, fut + head, 1) if fut in body else head + body
        if new_classes:
            body += "\n\n" + "\n\n".join(new_classes) + "\n"
        with open(spath, "w", encoding="utf-8") as fh:
            fh.write(body)
    return added


def _signature_colons(source):
    """{def line: (line, column) of the colon that ends its signature}."""
    out, toks = {}, list(tokenize.generate_tokens(io.StringIO(source).readline))
    for i, t in enumerate(toks):
        if t.type == tokenize.NAME and t.string == "def":
            depth, opened = 0, False
            for u in toks[i + 1:]:
                if u.type == tokenize.OP and u.string in "([{":
                    depth, opened = depth + 1, True
                elif u.type == tokenize.OP and u.string in ")]}":
                    depth -= 1
                elif u.type == tokenize.OP and u.string == ":" and depth == 0 and opened:
                    out[t.start[0]] = u.start
                    break
    return out


def annotate(source, params, returns=None):
    """The source with the found types put in as string annotations: parameter
    types {(def line, name): type} and return types {def line: type}. Every line
    stays where it was, so error lines match the original."""
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    returns = returns or {}
    colons = _signature_colons(source) if returns else {}
    edits = {}

    def at(row, char_col, text):
        edits.setdefault(row - 1, []).append((char_col, text))

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        a = node.args
        for arg in a.posonlyargs + a.args + a.kwonlyargs:
            t = params.get((node.lineno, arg.arg))
            if t and arg.annotation is None:
                b = lines[arg.lineno - 1].encode("utf-8")      # ast columns count UTF-8 bytes
                at(arg.lineno, len(b[:arg.end_col_offset].decode("utf-8")), ': "%s"' % t)
        t = returns.get(node.lineno)
        if t and node.returns is None and node.lineno in colons:
            row, col = colons[node.lineno]
            at(row, col, ' -> "%s"' % t)
    for i, ins in edits.items():
        line = lines[i]
        for col, text in sorted(ins, reverse=True):
            line = line[:col] + text + line[col:]
        lines[i] = line
    out = "".join(lines)
    if edits:
        out += ("" if out.endswith("\n") else "\n") + \
            "import adsk.core, adsk.fusion, adsk.drawing  # added by check_api for the types it put in\n"
    return out


def _build(path, defs_dir, module):
    """One mypy build of the script as `module`. The name must be new every time:
    the cache would otherwise hand back an earlier result for the same name."""
    from mypy import build
    from mypy.modulefinder import BuildSource
    from mypy.options import Options
    o = Options()
    o.check_untyped_defs = True
    o.follow_imports = "silent"
    o.mypy_path = [defs_dir, os.path.dirname(os.path.abspath(__file__))]   # fusion_folder and friends
    o.export_types = True
    o.incremental = True
    o.cache_dir = os.path.join(defs_dir, ".mypy_cache")
    o.allow_redefinition = True
    o.hide_error_codes = False
    o.preserve_asts = True
    return build.build(sources=[BuildSource(path, module)], options=o)


def _type_name(t, in_tuple=False):
    """'adsk.drawing.Sheet' (or 'A | B', or a tuple of them) for a Fusion API
    type, else None. Plain numbers and text are kept only inside a tuple."""
    from mypy.types import Instance, NoneType, TupleType, UnionType, get_proper_type
    p = get_proper_type(t)
    if isinstance(p, Instance):
        if p.type.fullname.startswith("adsk."):
            return p.type.fullname
        if in_tuple and p.type.fullname in ("builtins.int", "builtins.float", "builtins.str", "builtins.bool"):
            return p.type.fullname.split(".")[1]
        return None
    if isinstance(p, TupleType) and not in_tuple:
        names = [_type_name(i, True) for i in p.items]
        if names and all(names) and any(n.startswith("adsk.") for n in names):
            return "tuple[%s]" % ", ".join(names)
        return None
    if isinstance(p, UnionType):
        items = [get_proper_type(i) for i in p.items]
        names = [_type_name(i, in_tuple) for i in items if not isinstance(i, NoneType)]
        if names and all(names):
            return " | ".join(sorted(set(n for x in names for n in x.split(" | "))))
    return None


def infer_parameters(result, path, module):
    """{(def line, parameter name): type} for the script's own functions whose
    parameters have no annotation, from the types mypy sees at the calls to
    them in the same script."""
    from mypy.nodes import ARG_NAMED, ARG_OPT, ARG_POS, CallExpr, FuncDef, NameExpr
    from mypy.traverser import TraverserVisitor
    state = result.graph.get(module)
    tree = state.tree if state is not None else None
    if tree is None:
        return {}
    calls = []

    class Calls(TraverserVisitor):
        def visit_call_expr(self, e: CallExpr) -> None:
            calls.append(e)
            super().visit_call_expr(e)

    tree.accept(Calls())
    found = {}
    for e in calls:
        fn = e.callee.node if isinstance(e.callee, NameExpr) else None
        if not isinstance(fn, FuncDef) or not fn.fullname.startswith(module + "."):
            continue
        params = list(fn.arguments)
        if params and params[0].variable.name in ("self", "cls"):
            params = params[1:]
        positional = [p for p in params if p.kind in (ARG_POS, ARG_OPT)]
        for i, (arg, kind, name) in enumerate(zip(e.args, e.arg_kinds, e.arg_names)):
            if kind == ARG_POS and i < len(positional):
                param = positional[i]
            elif kind == ARG_NAMED:
                param = next((p for p in params if p.variable.name == name), None)
            else:
                break                                 # *args or **kwargs: stop guessing
            if param is None or param.type_annotation is not None:
                continue
            t = result.types.get(arg)
            n = _type_name(t) if t is not None else None
            if n:
                found.setdefault((fn.line, param.variable.name), set()).update(n.split(" | "))
    return {k: " | ".join(sorted(v)) for k, v in found.items()}


def infer_returns(result, module):
    """{def line: type} for the script's own functions with no return
    annotation, when every value they return is a known API type (or a tuple
    with one): mypy treats what an untyped function returns as unknown."""
    from mypy.nodes import FuncDef, LambdaExpr, ReturnStmt
    from mypy.traverser import TraverserVisitor
    state = result.graph.get(module)
    tree = state.tree if state is not None else None
    if tree is None:
        return {}
    found = {}

    class Returns(TraverserVisitor):
        def __init__(self):
            super().__init__()
            self.stack = []

        def visit_func_def(self, fn: FuncDef) -> None:
            self.stack.append((fn, []))
            super().visit_func_def(fn)
            fn_, rets = self.stack.pop()
            if fn.unanalyzed_type is not None and getattr(fn.unanalyzed_type, "ret_type", None) is not None \
                    and type(fn.unanalyzed_type.ret_type).__name__ != "AnyType":
                return                                  # it has a return annotation
            names, optional = set(), False
            for r in rets:
                if r.expr is None or type(r.expr).__name__ == "NameExpr" and r.expr.name == "None":
                    optional = True
                    continue
                t = result.types.get(r.expr)
                n = _type_name(t) if t is not None else None
                if not n:
                    return                              # an unknown return: leave it
                names.add(n)
            if names:
                found[fn.line] = " | ".join(sorted(names)) + (" | None" if optional else "")

        def visit_lambda_expr(self, e: LambdaExpr) -> None:
            pass                                        # their returns aren't the function's

        def visit_return_stmt(self, r: ReturnStmt) -> None:
            if self.stack:
                self.stack[-1][1].append(r)
            super().visit_return_stmt(r)

    tree.accept(Returns())
    return found


IGNORED = ('Name "SCRIPT_ARGS" is not defined',)   # put in by run_script.py at run time


def check_script(path, defs_dir, rounds=8):
    """Name errors in one script, after giving its untyped helpers the
    parameter types of their calls and the return types of their returns,
    repeated so the types travel along a chain of helpers."""
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    n_lines = src.count("\n") + 1
    with tempfile.TemporaryDirectory(prefix="check-api-") as d:
        tmp = os.path.join(d, os.path.basename(path))
        params, rets, cur = {}, {}, src
        for _ in range(rounds + 1):
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.write(cur)
            module = "check_api_target_%s" % uuid.uuid4().hex[:12]
            result = _build(tmp, defs_dir, module)
            new_p = {k: v for k, v in infer_parameters(result, tmp, module).items() if k not in params}
            new_r = {k: v for k, v in infer_returns(result, module).items() if k not in rets}
            if not new_p and not new_r:
                break
            params.update(new_p)
            rets.update(new_r)
            cur = annotate(src, params, rets)
        out = []
        for line in result.errors:
            m = re.match(r"^(.*?):(\d+): error: (.*?)\s+\[([\w-]+)\]\s*$", line)
            if not m or m.group(1) != tmp or m.group(4) not in CODES or int(m.group(2)) > n_lines:
                continue
            if any(x in m.group(3) for x in IGNORED):
                continue
            out.append("%s:%s: error: %s  [%s]" % (path, m.group(2), m.group(3), m.group(4)))
    return out, (params, rets)


def run_mypy(scripts, defs_dir, python=None):
    """Name errors in all the scripts (one mypy build per script and round)."""
    try:
        import mypy  # noqa: F401
    except ImportError:
        raise RuntimeError("mypy isn't installed for %s" % sys.executable)
    errors = []
    for s in scripts:
        errs, _found = check_script(s, defs_dir)
        errors.extend(errs)
    return errors


def defs_cache(install):
    """A completed copy of the definitions, made once per Fusion install."""
    stamp = hashlib.sha1(("%s %s" % (install, os.path.getmtime(os.path.join(install, "drawing.py"))))
                         .encode()).hexdigest()[:12]
    root = os.path.join(tempfile.gettempdir(), "fusion-api-defs-" + stamp)
    if not os.path.isdir(os.path.join(root, "adsk")):
        tmp = root + ".tmp%d" % os.getpid()
        shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp)
        complete_definitions(install, tmp)
        try:
            os.rename(tmp, root)
        except OSError:
            shutil.rmtree(tmp, ignore_errors=True)    # made by another run meanwhile
    return root


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check Fusion scripts' API names offline (see the module help).")
    ap.add_argument("scripts", nargs="+")
    ap.add_argument("--install", default=None, help="Fusion's packages/adsk folder (found by default)")
    opts = ap.parse_args(argv)
    install = opts.install or find_install()
    if not install:
        print("check_api: no Fusion install found (%s)" % INSTALL_GLOB, file=sys.stderr)
        return 2
    missing = [s for s in opts.scripts if not os.path.isfile(s)]
    if missing:
        print("check_api: no such file: %s" % ", ".join(missing), file=sys.stderr)
        return 2
    scripts = [os.path.relpath(s) for s in opts.scripts]
    try:
        errors = run_mypy(scripts, defs_cache(install))
    except RuntimeError as e:
        print("check_api: %s; install it into a virtual environment and run this with its python"
              % e, file=sys.stderr)
        return 2
    for line in errors:
        print(line)
    print("check_api: %d name error(s) in %d script(s), against %s" % (
        len(errors), len(scripts), install.split("/production/")[-1].split("/")[0][:12]))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
