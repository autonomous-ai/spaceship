"""Reading a Fusion cloud folder safely, before making a file in it. One copy for
every team script and tool (PM ruling 2026-10-31), so nobody keeps a stricter one.

In a script run through run_script.py:

    from fusion_folder import safe_to_create
    warnings = safe_to_create(folder, "210101_P01_WALL-PANEL_CAD")     # raises if it isn't safe
    for w in warnings:
        print("warning:", w)

run_script.py makes this module importable inside Fusion and loads it fresh on
every run, so a fix here reaches every team at once. Tools that send their own
scripts (start_drawing.py, the runner's --doc step) put this file's text in
front of their script instead.

Why: after a Fusion restart, and while files upload, a folder entry can't be
read for a while (DataFiles.item raises, or the name can't be read). Skipping
it could make a second file with the same name, if the unreadable entry is
that name; refusing on any unreadable entry blocks every team on one bad file.
So this reads the folder again for up to a minute, then refuses only when an
entry that still can't be read could be the new file: its name can't be read
and it isn't known to be another kind of file. Others only give a warning.
"""

import time

try:
    import adsk
except ImportError:                 # offline tests
    adsk = None

WAIT_S = 60.0       # read the folder again for up to this long (PM ruling 2026-10-31)
PAUSE_S = 5.0       # between two reads


def _short(e):
    text = str(e).strip()
    return text.splitlines()[0][:100] if text else type(e).__name__


def read_folder(folder, wait_s=WAIT_S, pause_s=PAUSE_S, sleep=time.sleep, now=time.monotonic,
                stop_when=None):
    """(files, unknown, others) for the entries of a Fusion DataFolder.

    files: {name: [DataFile, ...]} of the entries that could be read;
    unknown: entries whose name can't be read and whose kind isn't known either,
      as text such as "entry 7 (kind unknown, name unreadable)" (with the
      extension when it is known, see `could_be`);
    others: kept per extension, {extension: [text, ...]}, for entries whose
      name can't be read but whose kind can.
    While any entry can't be read, it reads the folder again, every pause_s,
    until wait_s has gone by, or until stop_when(files) is true (an open step
    that found its file needn't wait for the others)."""
    t_end = now() + wait_s
    while True:
        files, unknown, others = {}, [], {}
        for i in range(folder.dataFiles.count):
            try:
                f = folder.dataFiles.item(i)
            except Exception as e:
                unknown.append("entry %d (%s)" % (i, _short(e)))
                continue
            try:
                files.setdefault(f.name, []).append(f)
                continue
            except Exception:
                pass
            try:
                ext = (f.fileExtension or "").lower()
            except Exception:
                ext = ""
            if ext:
                others.setdefault(ext, []).append("entry %d (a .%s file, name unreadable)" % (i, ext))
            else:
                unknown.append("entry %d (kind unknown, name unreadable)" % i)
        if (not unknown and not others) or now() >= t_end or (stop_when and stop_when(files)):
            return files, unknown, others
        if adsk is not None:
            adsk.doEvents()
        sleep(min(pause_s, max(0.0, t_end - now())))


def could_be(unknown, others, extension):
    """The unreadable entries that could be a new file with this extension."""
    return list(unknown) + list(others.get(extension.lower().lstrip("."), []))


def cannot_be(others, extension):
    """The unreadable entries known to be another kind of file."""
    ext = extension.lower().lstrip(".")
    return [t for e, items in sorted(others.items()) if e != ext for t in items]


def safe_to_create(folder, name, extension="f3d", wait_s=WAIT_S, pause_s=PAUSE_S,
                   sleep=time.sleep, now=time.monotonic):
    """Raise RuntimeError unless a new NAME.extension can be made in folder without
    a second copy: NAME isn't there, and no entry that still can't be read after
    up to wait_s could be it. Returns warnings about unreadable entries that
    can't be it (another kind of file)."""
    files, unknown, others = read_folder(folder, wait_s, pause_s, sleep, now)
    if name in files:
        raise RuntimeError("%s is already in the folder; not made again" % name)
    risky = could_be(unknown, others, extension)
    if risky:
        raise RuntimeError("%s can't be read and could be %s, so it isn't made (try again later): %s"
                           % ("an entry" if len(risky) == 1 else "%d entries" % len(risky), name,
                              "; ".join(risky)))
    return ["%s can't be read by name, but it isn't a .%s, so it isn't %s"
            % (t, extension.lower().lstrip("."), name) for t in cannot_be(others, extension)]
