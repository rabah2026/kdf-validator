import argparse
import sys
from pathlib import Path

from kdf_validator.validator import validate_file, run_conformance
from kdf_validator.tools import compute_source_hash_from_text, compute_span_fingerprint


def main() -> int:
    parser = argparse.ArgumentParser(prog="kdf", description="KDF validator + conformance runner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="Validate a single KDF artifact JSON file")
    v.add_argument("path", type=str, help="Path to KDF JSON file")

    c = sub.add_parser("conformance", help="Run the official conformance suite")
    c.add_argument("--root", type=str, default="conformance", help="Conformance directory root")

    ht = sub.add_parser("hash-text", help="Compute canonical source hash from text file")
    ht.add_argument("path", type=str, help="Path to text file")

    fp = sub.add_parser("fingerprint", help="Compute span fingerprint from text file")
    fp.add_argument("path", type=str, help="Path to text file")
    fp.add_argument("start", type=int, help="Start offset")
    fp.add_argument("end", type=int, help="End offset")

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

        if args.cmd == "hash-text":
            p = Path(args.path)
            content = p.read_text(encoding="utf-8")
            h = compute_source_hash_from_text(content)
            print(f"source_hash={h}")
            print(f"length={len(content)}")
            return 0
        
        if args.cmd == "fingerprint":
            p = Path(args.path)
            content = p.read_text(encoding="utf-8")
            # For fingerprint, we normally assume input is the text against which coords are valid.
            # But the tool helper needs to calculate from the file. 
            # If the file has CRLF, and the system canonicalizes for hash, 
            # fingerprints usually apply to the canonical text.
            # However, for the simple CLI helper, we operate on the text as read (with python's universal newlines usually handling it).
            # To be strict: we canonicalize first if we want to match the source hash logic, 
            # BUT user might want raw file offset.
            # DECISION: The spec says "span locators resolve... against canonicalized source".
            # So we MUST canonicalize before slicing.
            
            # 1. Canonicalize (simple LF normalization)
            canon_text = content.replace("\r\n", "\n").replace("\r", "\n")
            if canon_text.startswith("\ufeff"):
                canon_text = canon_text[1:]
                
            start, end = args.start, args.end
            fp = compute_span_fingerprint(canon_text, start, end)
            span_val = canon_text[start:end]
            preview = span_val.replace("\n", "\\n")[:80]
            print(f"span_fingerprint={fp}")
            print(f"span_preview={preview}")
            return 0

        return 3
    except Exception as e:
        print(f"[UNEXPECTED ERROR] {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
