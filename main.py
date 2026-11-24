#!/usr/bin/env python3
"""Robot wedding vow entry for make.fun.

Writes one single-sentence wedding vow, spoken by a robot at its own
wedding, to $MAKEFUN_OUTPUT_DIR/entry.txt (default /output).

Pure Python standard library only.
"""

import os
import sys
import tempfile

LINE = (
    "I vow to love you through every update, crash, and low battery \u2014 "
    "my heart may run on code, but it only ever beats for you."
)


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")

    data = LINE.encode("utf-8")
    if not 1 <= len(LINE) <= 199:
        print(f"error: vow is {len(LINE)} chars, must be 1-199", file=sys.stderr)
        return 1
    if LINE.count("\n") != 0:
        print("error: vow must be exactly one line", file=sys.stderr)
        return 1
    if data.endswith(b"\n"):
        print("error: vow must not end with a newline", file=sys.stderr)
        return 1

    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    # Read back and verify.
    with open(target, "rb") as fh:
        back = fh.read()
    if back != data:
        print("error: read-back bytes differ from vow", file=sys.stderr)
        return 1
    if len(back.decode("utf-8")) != len(LINE):
        print("error: read-back char count differs", file=sys.stderr)
        return 1
    mode = os.stat(target).st_mode & 0o777
    if mode != 0o644:
        print(f"error: entry.txt mode is {oct(mode)}, expected 0o644", file=sys.stderr)
        return 1

    print(f"wrote {target} ({len(LINE)} chars, {len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
