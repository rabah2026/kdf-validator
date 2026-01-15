import argparse
import sys
from pathlib import Path

from kdf_validator.validator import validate_file, run_conformance


def main() -> int:
    parser = argparse.ArgumentParser(prog="kdf", description="KDF validator + conformance runner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="Validate a single KDF artifact JSON file")
    v.add_argument("path", type=str, help="Path to KDF JSON file")

    c = sub.add_parser("conformance", help="Run the official conformance suite")
    c.add_argument("--root", type=str, default="conformance", help="Conformance directory root")

    args = parser.parse_args()

    try:
        if args.cmd == "validate":
            ok, report = validate_file(Path(args.path))
            print(report)
            return 0 if ok else 2

        if args.cmd == "conformance":
            ok, report = run_conformance(Path(args.root))
            print(report)
            return 0 if ok else 2

        return 3
    except Exception as e:
        print(f"[UNEXPECTED ERROR] {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
