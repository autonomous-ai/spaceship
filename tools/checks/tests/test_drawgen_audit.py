"""The generator sheet audit (the Lead's ask, 2026-11-01; Reviewer 14 on #380): every committed generator sheet read
back and redrawn with the code in the tree. The drawing itself needs drawgen's own environment (OCC), so these tests
drive the audit's logic with stand-ins; the real run is tools/checks/drawgen_audit.sh."""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import drawgen_audit as da  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def _sheets(tmp_path, names):
    d = tmp_path / "v2/02-Drawings/base"
    d.mkdir(parents=True)
    paths = []
    for n in names:
        p = d / n
        p.write_bytes(("drawn %s" % n).encode())
        paths.append(str(p))
    return paths


def test_only_the_generators_sheets_are_audited(tmp_path):
    paths = _sheets(tmp_path, ["111103_P01_A_DWG.pdf", "111106_P01_B_DWG.pdf", "notes.pdf"])
    got = da.find_sheets(str(tmp_path / "v2/02-Drawings"), lambda p: "111106" not in p)
    assert got == [paths[0]]                              # a Fusion sheet and a non-drawing PDF are left out


def test_each_sheet_is_read_back_and_redrawn_and_the_reason_is_given(tmp_path):
    names = ["110101_P01_SAME_DWG.pdf", "111101_P01_FAILS_DWG.pdf", "111103_P01_SOURCES_DWG.pdf",
             "111106_P01_CODE_DWG.pdf", "111301_P01_REFUSED_DWG.pdf", "111999_P01_GONE_DWG.pdf",
             "100000_P04_POD_DWG.pdf"]
    paths = _sheets(tmp_path, names)
    kinds = {"110101": "assembly", "111101": "part", "111103": "part", "111106": "part", "111301": "part",
             "100000": "pod"}

    def readback(path, kind):
        return ["hole H03 is 0.20 mm off its STEP position"] if "FAILS" in path else []

    def redraw(pn, kind, out):
        if pn == "111301":
            raise RuntimeError("111301: its parts list gives the material as aluminium")
        src = next(p for p in paths if os.path.basename(p).startswith(pn))
        new = os.path.join(out, os.path.basename(src))
        data = open(src, "rb").read()
        with open(new, "wb") as fh:                       # the same bytes, except where the sheet is out of date
            fh.write(data if pn in ("110101", "111101") else data + b" (redrawn)")
        return new

    def stale_of(path):
        return ["v2/03-Manufacturing/base/111103_P01_X_STEP.step changed"] if ("SOURCES" in path or "POD" in path) else []

    res = {r["pn"]: r for r in da.audit(paths, kinds.get, readback, redraw, stale_of)}
    assert res["110101"]["redraw"] == "same" and not res["110101"]["readback"] and not da.bad(res["110101"])
    assert res["111101"]["readback"] and res["111101"]["redraw"] == "same" and da.bad(res["111101"])
    assert res["111103"]["redraw"] == "differs" and res["111103"]["why"] == [
        "v2/03-Manufacturing/base/111103_P01_X_STEP.step changed"]
    assert res["111106"]["redraw"] == "differs" and "generator's code" in res["111106"]["why"][0]
    assert res["111301"]["redraw"] == "not drawn" and "material" in res["111301"]["why"][0]
    assert res["111999"]["redraw"] == "no entry" and res["111999"]["kind"] is None
    # the GA only warns (the Lead's ruling): out of date, but not a failure
    assert res["100000"]["redraw"] == "differs" and da.off(res["100000"]) and not da.bad(res["100000"])
    lines, summary = da.report(list(res.values()))
    assert summary == ("6 generator sheets: 1 read back and redraw the same; 1 fail the read-back; 2 no longer "
                       "redraw byte for byte (1 by the generator's code, 1 with changed sources); 2 can't be drawn "
                       "again; the GA is out of date (a warning: it is redrawn at checkpoints)")
    assert any(l.startswith("warning (the GA is redrawn at checkpoints): ") for l in lines)
    assert any(l.startswith("  - hole H03") for l in lines)
    # the committed sheets are left as they were: every redraw went to a folder of its own, since removed
    assert all(open(p, "rb").read() == ("drawn %s" % os.path.basename(p)).encode() for p in paths)


def test_the_wrapper_reads_drawgens_own_environment_line():
    # drawgen_audit.sh takes the environment's place from run.sh's VENV line, so the two never part: keep its form
    run = open(os.path.join(REPO, "tools", "drawgen", "run.sh"), encoding="utf-8").read()
    assert re.search(r'^VENV="\$\{DRAWGEN_VENV:-(.+)\}"$', run, re.M)
    wrapper = open(os.path.join(REPO, "tools", "checks", "drawgen_audit.sh"), encoding="utf-8").read()
    assert "drawgen_audit.py" in wrapper and "-I" in wrapper
