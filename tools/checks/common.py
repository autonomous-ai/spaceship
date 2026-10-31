#!/usr/bin/env python3
"""Shared pieces for the mechanical checks: findings, owners, part numbers,
file names, and finding the files on a checked-out tree.

Standard library only.
"""

import csv
import io
import os
import re
from dataclasses import dataclass, field, asdict

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHECKS_DIR = "v2/04-Checks"

SEVERITIES = ("severe", "major", "minor")
# severe: it can't be made, assembled or used as drawn (a clash, a part over
#         20 kg, a bolt that can't be reached or bottoms out, a missing
#         drawing for a part we make). Blocks the owner's merge.
# major:  it will cause rework or a wrong part (missing tolerance, material
#         or finish; BOM and CAD disagree; a stack that can't be closed).
# minor:  presentation or record keeping.

CHECK_NAMES = {
    "C01": "clash and minimum gaps (Fusion)",
    "C02": "tolerance stack-ups",
    "C03": "fastener and tool access",
    "C04": "weight, doorway and pallet fit",
    "C05": "drawing completeness",
    "C06": "BOM completeness",
    "C07": "fastener schedule and thread engagement",
    "C08": "hole-to-hole alignment",
    "C09": "edge distance, bend radius, hole-to-bend",
    "C10": "mixed metals",
    "C11": "material grade and finish",
}


@dataclass
class Finding:
    check: str                 # C01 ... C11
    rule: str                  # short rule id inside the check, e.g. "mass-over-20kg"
    subject: str               # what it is about: part number, position code or file
    severity: str              # severe / major / minor
    message: str               # plain words: what is wrong, with numbers
    fix: str = ""              # what the owner should do
    file: str = ""             # repo-relative file the finding points at
    owner: str = ""            # owner group (WALL, FRONT, BASE, CEILING, Fusion Engineer 2, ...)
    evidence: dict = field(default_factory=dict)

    @property
    def key(self):
        return "%s|%s|%s" % (self.check, self.rule, self.subject)

    def to_dict(self):
        d = asdict(self)
        d["key"] = self.key
        return d


# ----------------------------------------------------------------- owners

# Path prefix -> owner group. First match wins; the briefs set these.
PATH_OWNERS = [
    ("v2/01-CAD-Native/wall/", "WALL"), ("v2/02-Drawings/wall/", "WALL"), ("v2/03-Manufacturing/wall/", "WALL"),
    ("v2/01-CAD-Native/front/", "FRONT"), ("v2/02-Drawings/front/", "FRONT"), ("v2/03-Manufacturing/front/", "FRONT"),
    ("v2/01-CAD-Native/base/", "BASE"), ("v2/02-Drawings/base/", "BASE"), ("v2/03-Manufacturing/base/", "BASE"),
    ("v2/01-CAD-Native/ceiling/", "CEILING"), ("v2/02-Drawings/ceiling/", "CEILING"),
    ("v2/03-Manufacturing/ceiling/", "CEILING"),
    ("v2/01-CAD-Native/electrical/", "ELECTRICAL"), ("v2/02-Drawings/electrical/", "ELECTRICAL"),
    ("v2/03-Manufacturing/electrical/", "ELECTRICAL"), ("v2/05-Engineering/electrical/", "ELECTRICAL"),
    ("v2/01-CAD-Native/air/", "CEILING"), ("v2/02-Drawings/air/", "CEILING"), ("v2/03-Manufacturing/air/", "CEILING"),
    ("v2/01-CAD-Native/interior/", "CEILING"), ("v2/02-Drawings/interior/", "CEILING"),
    ("v2/03-Manufacturing/interior/", "CEILING"),
    ("v2/07-Packaging/", "Packing and Assembly"), ("v2/02-Drawings/30-Assembly-Instructions/", "Packing and Assembly"),
    ("v2/01-CAD-Native/joints/", "Joints Engineer"), ("v2/02-Drawings/joints/", "Joints Engineer"),
    ("v2/03-Manufacturing/joints/", "Joints Engineer"), ("v2/05-Engineering/joints/", "Joints Engineer"),
    ("v2/05-Engineering/acoustics-air/", "Air Engineer"), ("v2/05-Engineering/hardware/", "Air Engineer"),
    ("v2/05-Engineering/layout-study/", "Layout Engineer"),
    ("v2/00-Control/", "PM"), ("v2/04-BOM/", "PM"),
    ("v2/01-CAD-Native/", "Fusion Engineer 2"), ("v2/02-Drawings/", "Fusion Engineer 2"),
    ("v2/03-Manufacturing/", "Fusion Engineer 2"), ("tools/fusion/", "Fusion Engineer 2"),
]

# Part-number family -> owner group, used when no team folder applies (the
# path comes first: LINING follows the assembly its cassettes hang in, so a
# ceiling cassette inside CEILING's STEP is CEILING's). D-80: ELECTRICAL is
# its own team; CEILING keeps AIR (61) and INTERIOR (81); Packing and Assembly
# owns PACKAGING (91). Hardware and seals (83, 84) are the joints register's:
# a shared made part such as the spigot 831001 gets its drawing from the
# Joints Engineer, while a team's parts-list row stays that team's.
FAMILY_OWNERS = {
    "10": "Fusion Engineer 2", "11": "BASE", "21": "WALL", "35": "FRONT", "36": "FRONT",
    "41": "CEILING", "51": "WALL", "61": "CEILING", "71": "ELECTRICAL", "81": "CEILING",
    "83": "Joints Engineer", "84": "Joints Engineer", "91": "Packing and Assembly",
}


# D-95: the base corner and inline keys have one source, the Joints Engineer; the teams place them by reference
JOINTS_KEYS = re.compile(r"^11121[1-4]$")


def owner_for(path="", part_number=""):
    if JOINTS_KEYS.match(part_number or ""):
        return "Joints Engineer"
    path = (path or "").replace("\\", "/")
    for prefix, owner in PATH_OWNERS:
        if path.startswith(prefix):
            return owner
    fam = (part_number or "")[:2]
    return FAMILY_OWNERS.get(fam, "PM")


# ----------------------------------------------------------------- part numbers

RESERVED_NUMBERS = {"110006", "110002", "120001", "211000", "210001", "210003", "210005",
                    "350011", "830001", "830005"}            # D-28
FAMILIES = {"10", "11", "21", "35", "36", "41", "51", "61", "71", "81", "83", "84", "91"}   # conventions s6
PN_RE = re.compile(r"^\d{6}$")


def pn_class(pn):
    """'assembly', 'part', 'bought', 'kit' or 'bad' (conventions section 6)."""
    if not PN_RE.match(pn or ""):
        return "bad"
    n = int(pn[2:])
    if n <= 999:
        return "assembly"
    if n <= 7999:
        return "part"
    if n <= 8999:
        return "bought"
    return "kit"


def pn_problems(pn):
    out = []
    if not PN_RE.match(pn or ""):
        return ["not 6 digits"]
    if pn in RESERVED_NUMBERS:
        out.append("reserved by D-28 (old V5 number)")
    if pn[:2] not in FAMILIES:
        out.append("family %s is not in conventions section 6" % pn[:2])
    return out


FASTENER_WORDS = re.compile(r"^HARDWARE - (BOLT|SCREW|NUT|WASHER|RIVNUT|RIVET NUT|INSERT|STUD|RIVET|CLINCH|PIN)\b|"
                            r"\b(RIVNUT|RIVET NUT)\b", re.I)


SOFT_HEADS = re.compile(r"(?:[A-Z]+-)*(?:FILLS?|FELTS?|FOAMS?|GASKETS?|SEALS?|TAPES?)")


def head_noun(name):
    """The last word of a part name's FUNCTION field (conventions section 5): 'BASE - SEAL HOLDER - LH'
    gives HOLDER, 'LINING - FILL - CEILING - BAY A' gives FILL, 'FRONT - DROP SEAL - ATHMER' gives SEAL."""
    fields = [f.strip() for f in (name or "").upper().split(" - ")]
    func = fields[1] if len(fields) > 1 else fields[0]
    words = re.findall(r"[A-Z][A-Z-]*", func)
    return words[-1] if words else ""


def is_soft(name, kinds=None):
    """A soft good by its head noun (fill, felt, foam, gasket, seal, tape); kinds narrows the set."""
    h = head_noun(name)
    if not SOFT_HEADS.fullmatch(h):
        return False
    return kinds is None or any(h.rstrip("S").endswith(k) for k in kinds)


def is_fastener(pn="", name=""):
    """A standard fastener: family 83 (conventions section 6) or a HARDWARE - BOLT/NUT/... name."""
    return (pn or "")[:2] == "83" or bool(FASTENER_WORDS.search((name or "").strip()))


# ----------------------------------------------------------------- file names

FILE_RE = re.compile(r"^(?P<pn>\d{6})_(?P<rev>[PR]\d{2})_(?P<name>[A-Z0-9][A-Z0-9-]*)_(?P<doc>CAD|STEP|DWG|DXF|BOM|"
                     r"SPEC|CALC|FAI|INS|PKG|IMG)\.(?P<ext>[a-z0-9]+)$")


def parse_file_name(path):
    m = FILE_RE.match(os.path.basename(path))
    return m.groupdict() if m else None


# ----------------------------------------------------------------- tree

def rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def walk_files(root, top, exts=None, skip=("/proof/", "/.raw/", "/__pycache__/")):
    base = os.path.join(root, top)
    out = []
    for d, _dirs, files in os.walk(base):
        for f in files:
            p = os.path.join(d, f)
            r = rel(root, p)
            if any(s in "/" + r for s in skip):
                continue
            if exts and not f.lower().endswith(tuple(exts)):
                continue
            out.append(p)
    return sorted(out)


def export_ref(ref, repo=REPO_ROOT, dest=None):
    """Check out a git ref (for example origin/main or a PR head) into a
    fresh folder with git archive, so a run checks exactly that revision.
    Returns (folder, short sha). The rule files in v2/04-Checks/config and
    stacks come from this checkout, so a revision without them is still
    checked with the current rules."""
    import shutil
    import subprocess
    import tarfile
    import tempfile
    sha = subprocess.run(["git", "-C", repo, "rev-parse", "--short", ref], capture_output=True, text=True,
                         check=True).stdout.strip()
    dest = dest or tempfile.mkdtemp(prefix="checks-%s-" % sha)
    tar = subprocess.run(["git", "-C", repo, "archive", "--format=tar", ref], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as tf:
        tf.extractall(dest, filter="data")
    for sub in ("v2/04-Checks/config", "v2/04-Checks/stacks"):
        src = os.path.join(repo, sub)
        if os.path.isdir(src):
            dst = os.path.join(dest, sub)
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
    return dest, sha


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        text = fh.read()
    return list(csv.DictReader(io.StringIO(text)))


def num(v):
    """Float from a CSV cell ('12.3', '12,3', '12.3 kg'); None if empty or bad."""
    if v is None:
        return None
    m = re.search(r"[-+]?\d+(?:[.,]\d+)?", str(v))
    if not m:
        return None
    return float(m.group(0).replace(",", "."))


REGISTER = "v2/05-Engineering/joints/joints-register.md"


def register_names(root):
    """D-99: hardware names come from the joints register: {part number: name} from its hardware tables
    ('| H-05 | **831001** | HARDWARE - LOCATING SPIGOT - M6 X Ø8 - STAINLESS · Chốt định vị Ø8 | ...'),
    the English name before the ' · ' that starts the Vietnamese one."""
    p = os.path.join(root, REGISTER)
    out = {}
    if not os.path.exists(p):
        return out
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^\|\s*H-[\w.]+\s*\|\s*\*\*(\d{6})\*\*\s*\|\s*([^|]+?)\s*\|", line)
            if m:
                out.setdefault(m.group(1), m.group(2).split(" · ")[0].strip())
    return out


def name_words(name):
    """A part name as its words, for comparing names: case, hyphens, brackets and spacing don't count
    ('BASE - LEVELLING GLIDE - M10 (HOLD)' and 'BASE - LEVELLING GLIDE - M10 - HOLD' are one name)."""
    return " ".join(re.findall(r"[A-Z0-9Ø±×.,+/°]+", (name or "").upper()))


def reserved_spaces(root):
    """{part number: row} from v2/04-Checks/config/reserved-spaces.csv: bodies that only hold space for a part
    another team designs later (the Lead's rulings, like D-92's ELECTRICAL routes). No drawing and no seam rules
    for them; each is listed open under its designer until it's designed."""
    out = {}
    # D-105: a row a team types "reserved air space" is one too, as the master BOM and the checklist read it
    for f in walk_files(root, "v2/03-Manufacturing", exts=(".csv",)):
        try:
            rows = read_csv(f)
        except (UnicodeDecodeError, OSError):
            continue
        for r in rows:
            pn = (r.get("part_number") or "").strip()
            kinds = " ".join((v or "") for k, v in r.items() if isinstance(k, str) and isinstance(v, str)
                             and re.search(r"type|kind", k, re.I))
            if PN_RE.match(pn) and re.search(r"\breserved air space\b", kinds, re.I):
                out.setdefault(pn, {"part_number": pn, "owner": "AIR", "ruling": "D-105",
                                    "why": "typed reserved air space in %s" % rel(root, f)})
    p = os.path.join(root, CHECKS_DIR, "config", "reserved-spaces.csv")
    if os.path.exists(p):
        out.update({r["part_number"].strip(): r for r in read_csv(p) if (r.get("part_number") or "").strip()})
    return out


def reserved_label(label, reserved):
    """Does a body's label name one of the reserved part numbers?"""
    return any(re.search(r"(?<!\d)%s(?!\d)" % pn, label or "") for pn in reserved)
