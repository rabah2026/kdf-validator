# kdf-validator

Reference validator for KDF (Knowledge-Dense Format) v0.1.

This repository provides:
- JSON Schema validation for KDF artifacts
- Semantic enforcement required by KDF v0.1 (evidence, spans, hashes, anchors)
- Official conformance suite execution (PASS/FAIL + edge classification)

KDF conformance is defined by passing the conformance suite.
Partial compliance is not compliance.

## Install

```bash
pip install kdf-validator
```

Or from source:

```bash
pip install git+https://github.com/rabah2026/kdf-validator.git
```

## Run conformance suite

```powershell
kdf conformance
```

## Validate a file

```powershell
kdf validate path\to\artifact.json
```

## Evidence Helpers

The CLI includes helpers for calculating canonical hashes and fingerprints for **plain text** documents.
(See `spec/CANONICALIZATION.md` for PDF/HTML guidance).

```powershell
# Get canonical source hash
kdf hash-text path\to\source.txt

# Get span fingerprint
kdf fingerprint path\to\source.txt <start_offset> <end_offset>
```

## Exit codes

* 0: success
* 2: validation failure
* 3: unexpected error
