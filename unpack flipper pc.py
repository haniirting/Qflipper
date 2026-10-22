"""Unpacks flipper-pc.zip into a folder.

Usage:
    python unpack_flipper_pc.py                    # flipper-pc.zip next to this script -> ./flipper-pc
    python unpack_flipper_pc.py archive.zip        # any archive path -> ./flipper-pc
    python unpack_flipper_pc.py archive.zip out    # any archive path -> out
    python unpack_flipper_pc.py archive.zip out --force   # replace an existing folder

Only standard library. Refuses paths that try to leave the target folder.
"""
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))


def unpack(archive, target, force=False):
    if not os.path.isfile(archive):
        raise SystemExit("Archive not found: %s" % archive)
    if not zipfile.is_zipfile(archive):
        raise SystemExit("Not a zip archive: %s" % archive)
    target = os.path.abspath(target)
    if os.path.exists(target) and os.listdir(target) if os.path.isdir(target) else os.path.exists(target):
        if not force:
            raise SystemExit("Target already exists and is not empty: %s (use --force to replace it)" % target)
        if os.path.isdir(target):
            shutil.rmtree(target)
        else:
            os.remove(target)
    os.makedirs(target, exist_ok=True)

    count = 0
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            name = info.filename.replace("\\", "/")
            parts = [p for p in name.split("/") if p not in ("", ".")]
            if not parts:
                continue
            if ".." in parts or os.path.isabs(name) or ":" in parts[0]:
                raise SystemExit("Unsafe path in archive, stopped: %s" % info.filename)
            # the archive may wrap everything in one top folder (e.g. fpc/ or flipper-pc/): strip it
            dest = os.path.join(target, *parts)
            if info.is_dir():
                os.makedirs(dest, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with z.open(info) as src, open(dest, "wb") as out:
                shutil.copyfileobj(src, out)
            count += 1
    return target, count


def main(argv):
    force = "--force" in argv
    args = [a for a in argv if a != "--force"]
    archive = args[0] if len(args) > 0 else os.path.join(HERE, "flipper-pc.zip")
    target = args[1] if len(args) > 1 else os.path.join(os.path.dirname(os.path.abspath(archive)), "flipper-pc")
    path, count = unpack(archive, target, force)
    # a single top folder from the archive: move its contents up so the repo root is the target
    entries = [e for e in os.listdir(path) if e != ".git"]
    if len(entries) == 1 and os.path.isdir(os.path.join(path, entries[0])) and not os.path.exists(os.path.join(path, "README.md")):
        inner = os.path.join(path, entries[0])
        tmp = path + "_tmp"
        os.rename(inner, tmp)
        shutil.rmtree(path)
        os.rename(tmp, path)
    checks = ["README.md", "flipper-desk/flipper_desk.py", "phone-desk/flipper_phone_desk.py",
              "phone-mirror/flipper_phone_mirror.py", ".github/workflows/ci.yml"]
    missing = [c for c in checks if not os.path.exists(os.path.join(path, c))]
    print("Unpacked %d files to %s" % (count, path))
    if missing:
        print("WARNING, missing: " + ", ".join(missing))
        return 1
    print("All main files are present. Next: open the folder, run the GitHub push commands from README.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
