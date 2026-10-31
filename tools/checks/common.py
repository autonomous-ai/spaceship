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
    ("v2/05-Engineering/joints/", "Joints Engineer"),
    ("v2/05-Engineering/acoustics-air/", "Air Engineer"), ("v2/05-Engineering/hardware/", "Air Engineer"),
    ("v2/05-Engineering/layout-study/", "Layout Engineer"),
    ("v2/00-Control/", "PM"),
    ("v2/01-CAD-Native/", "Fusion Engineer 2"), ("v2/02-Drawings/", "Fusion Engineer 2"),
    ("v2/03-Manufacturing/", "Fusion Engineer 2"), ("tools/fusion/", "Fusion Engineer 2"),
]

# Part-number family -> owner group, from the briefs (LINING follows the
# assembly its cassettes hang in; AIR sits in DR; ELECTRICAL and INTERIOR
# are with CEILING).
FAMILY_OWNERS = {
    "10": "Fusion Engineer 2", "11": "BASE", "21": "WALL", "35": "FRONT", "36": "FRONT",
    "41": "CEILING", "51": "WALL", "61": "FRONT", "71": "CEILING", "81": "CEILING",
}


def owner_for(path="", part_number=""):
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


FASTENER_WORDS = re.compile(r"\b(BOLT|SCREW|NUT|WASHER|RIVNUT|RIVET NUT|INSERT|STUD|RIVET|CLINCH|PIN)\b", re.I)


def is_fastener(pn="", name=""):
    return (pn or "")[:2] == "83" or bool(FASTENER_WORDS.search(name or ""))


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
