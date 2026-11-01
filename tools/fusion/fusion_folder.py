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
NEW_FILE_PAUSE_S = 10.0   # after a new cloud file, before the folder is read (PM ruling 2026-11-01)


def _short(e):
    text = str(e).strip()
    return text.splitlines()[0][:100] if text else type(e).__name__


def _listing(folder):
    """The folder's entries from ONE listing, as [(position, DataFile or error text)].

    DataFiles.asArray() fetches the folder's contents once. count + item(i)
    fetched them again for every entry (live 2026-11-01: about 2 s each in
    Fusion's log, so a folder of 89 files took 3 minutes a pass, and a run that
    read the folder a few times looked hung). Falls back to item(i), on one kept
    collection, when asArray isn't there or fails."""
    files = folder.dataFiles
    try:
        arr = files.asArray()
    except Exception:
        arr = None
    if arr is not None:
        out = [(i, f if f is not None else "unreadable entry") for i, f in enumerate(arr)]
        # Reviewer 5, P2 on #213: count + item(i) could never lose a file without saying
        # so, but a listing that came back short would let one vanish from the pass. So
        # the slots past the array's end, by the count of the same collection, count as
        # unreadable: read again, and refused by safe_to_create if they never appear.
        try:
            n = files.count
        except Exception as e:
            # Reviewer 5, P3 on #220: a count that can't be read can't vouch for the
            # listing, so it counts as one unreadable entry (read again; refused if it
            # never answers)
            return out + [(len(out), "the folder's count can't be read: %s" % _short(e))]
        out += [(i, "missing from the listing: the folder counts %d" % n) for i in range(len(out), n)]
        return out
    out = []
    for i in range(files.count):
        try:
            out.append((i, files.item(i)))
        except Exception as e:
            out.append((i, _short(e)))
    return out


def pause_after_new_file(sleep=time.sleep, clock=time.time, pause_s=NEW_FILE_PAUSE_S):
    """Wait until pause_s has gone by since the last new cloud file this Fusion saved, letting Fusion work in the
    meantime; returns the seconds waited. The runner's hook notes each saveAs on adsk.core (_spaceship_new_file_at,
    a time.time(); _spaceship_new_file, its name), in every run through run_script.py and start_drawing.py.

    Why (PM ruling 2026-11-01): Fusion crashed twice that day right after it fetched the team folder's second page
    of files, each time 1 to 3 s after it started a live-update subscription; at 14:00:58 that was two seconds after
    BASE's run saved a new file and went on to read the folder for its next one. The same fetch had worked about
    1,700 times before, so this is a pause on a pattern seen twice, not a proven cure."""
    if adsk is None:
        return 0.0
    try:
        import adsk.core as _ac
        t = getattr(_ac, "_spaceship_new_file_at", None)
        name = getattr(_ac, "_spaceship_new_file", "") or "?"
    except Exception:
        return 0.0
    if not isinstance(t, (int, float)):
        return 0.0
    left = pause_s - (clock() - t)
    if left <= 0:
        return 0.0
    print("fusion_folder: waiting %.1f s after the new cloud file %s before reading the folder" % (left, name))
    end = clock() + left
    while clock() < end:
        adsk.doEvents()
        sleep(min(0.5, max(0.0, end - clock())))
    return left


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
    until wait_s has gone by, or until stop_when(files, unknown, others) is
    true: an open step that found its file, or a check where nothing still
    unread could be the new file, needn't wait (Reviewer 5, P3 on #121: a
    warn-only entry must not hold Fusion for a minute). It first waits out the pause after a new cloud file
    (pause_after_new_file)."""
    pause_after_new_file(sleep=sleep)
    t_end = now() + wait_s
    while True:
        files, unknown, others = {}, [], {}
        for i, f in _listing(folder):            # one fetch of the folder per pass
            if isinstance(f, str):
                unknown.append("entry %d (%s)" % (i, f))
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
        if (not unknown and not others) or now() >= t_end or (stop_when and stop_when(files, unknown, others)):
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
    files, unknown, others = read_folder(          # stop as soon as nothing unread could be it
        folder, wait_s, pause_s, sleep, now,
        stop_when=lambda fs, u, o: name in fs or not could_be(u, o, extension))
    if name in files:
        raise RuntimeError("%s is already in the folder; not made again" % name)
    risky = could_be(unknown, others, extension)
    if risky:
        raise RuntimeError("%s can't be read and could be %s, so it isn't made (try again later): %s"
                           % ("an entry" if len(risky) == 1 else "%d entries" % len(risky), name,
                              "; ".join(risky)))
    return ["%s can't be read by name, but it isn't a .%s, so it isn't %s"
            % (t, extension.lower().lstrip("."), name) for t in cannot_be(others, extension)]
