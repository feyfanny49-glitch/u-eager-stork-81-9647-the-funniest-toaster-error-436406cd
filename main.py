#!/usr/bin/env python3
"""Write the single judged text entry, atomically, to /output/entry.txt."""

from __future__ import annotations

import hashlib
import os
import tempfile

ENTRY = "ERROR: toast ready. Insert owner to continue."
OUTPUT = "/output/entry.txt"
MAX_CHARS = 120


def encode_entry(text: str) -> bytes:
    """Fail loudly unless the entry satisfies the published gate before we write."""
    if not 1 <= len(text) <= MAX_CHARS:
        raise ValueError(f"entry must be 1..{MAX_CHARS} characters, got {len(text)}")
    if not text.strip():
        raise ValueError("entry must not be only white space")
    if any(ch in text for ch in ("\n", "\r", "\u2028", "\u2029")):
        raise ValueError("entry must be one line")
    return text.encode("utf-8")


def main() -> None:
    data = encode_entry(ENTRY)
    directory = os.path.dirname(OUTPUT)
    os.makedirs(directory, exist_ok=True)

    # Same filesystem as the destination, so os.replace is an atomic rename.
    fd, temp_path = tempfile.mkstemp(prefix=".entry-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, OUTPUT)
    except BaseException:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise

    print(
        f"wrote {OUTPUT}: {len(ENTRY)} chars, {len(data)} bytes, "
        f"sha256 {hashlib.sha256(data).hexdigest()}"
    )


if __name__ == "__main__":
    main()
