from __future__ import annotations

from pathlib import Path
import sys

EXTENSIONS = {".py", ".html", ".css", ".js", ".md", ".yml", ".yaml", ".toml"}


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    failed: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts or "_vendor_hop_and_barley" in path.parts:
            continue
        if path.suffix.lower() not in EXTENSIONS:
            continue

        data = path.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            failed.append(f"{path}: has UTF-8 BOM")
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            failed.append(f"{path}: not valid UTF-8")

    if failed:
        print("Encoding check failed:")
        for line in failed:
            print(f"- {line}")
        return 1
    print("Encoding check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())