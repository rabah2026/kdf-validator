# kdf-validator

Reference validator for KDF (Knowledge-Dense Format) v0.1.

This repository provides:
- JSON Schema validation for KDF artifacts
- Semantic enforcement required by KDF v0.1 (evidence, spans, hashes, anchors)
- Official conformance suite execution (PASS/FAIL + edge classification)

KDF conformance is defined by passing the conformance suite.
Partial compliance is not compliance.

## Install (Windows / PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -U pip
pip install -e .
```

## Run conformance suite

```powershell
kdf conformance
```

## Validate a file

```powershell
kdf validate path\to\artifact.json
```

## Exit codes

* 0: success
* 2: validation failure
* 3: unexpected error
