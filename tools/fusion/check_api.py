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
- Types only flow from what the script gets from the API. Give helper
  functions annotated parameters (def extent(view: "adsk.drawing.DrawingView"))
  to have their bodies checked too.

Needs mypy (python3 -m pip install mypy into a virtual environment in your
session folder, then run this with that environment's python). Exit 0 clean,
1 name errors found, 2 can't run (no Fusion install or no mypy).
"""

import argparse
import ast
import glob
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
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


def run_mypy(scripts, defs_dir, python=sys.executable):
    env = dict(os.environ, MYPYPATH=defs_dir)
    cache = os.path.join(defs_dir, ".mypy_cache")
    cmd = [python, "-m", "mypy", "--check-untyped-defs", "--follow-imports=silent",
           "--no-error-summary", "--show-error-codes", "--cache-dir", cache,
           "--allow-redefinition", "--no-incremental"] + list(scripts)
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if "No module named mypy" in p.stderr:
        raise RuntimeError("mypy isn't installed for %s" % python)
    wanted = []
    for line in p.stdout.splitlines():
        m = re.search(r"\[([\w-]+)\]\s*$", line)
        if m and m.group(1) in CODES and any(line.startswith(s + ":") for s in scripts):
            wanted.append(line)
    return wanted


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
