# Support

This document sets expectations for support and contributions.

---

## What This Project Provides

- A reference validator for KDF v0.1 artifacts
- JSON Schema validation
- Semantic validation (evidence, spans, hashes, anchors)
- CLI tools: `validate`, `conformance`, `hash-text`, `fingerprint`
- Conformance suite runner

---

## What This Project Does NOT Provide

- **PDF extraction pipelines:** The validator does not parse PDFs
- **HTML pipelines:** The validator does not normalize or process HTML
- **Hosted validation services:** No web API or cloud service is provided
- **Extraction tooling:** The validator checks artifacts, not creates them
- **Commercial support or SLAs:** This is a volunteer-maintained project
- **Guaranteed compatibility:** Only KDF v0.1 is currently supported

---

## Reporting Bugs

When reporting bugs:

1. **Search existing issues** before opening a new one
2. **Provide a minimal reproduction:**
   - Include the smallest possible KDF artifact that triggers the issue
   - Specify validator version (`kdf --version`)
   - Include full command and output
3. **Describe expected vs. actual behavior**
4. **Include environment details** (Python version, OS)

Good bug reports significantly increase the chance of resolution.

---

## Contribution Expectations

This project follows a **conservative change policy**.

Contributions are evaluated on:

- **Correctness:** Does this fix a genuine issue?
- **Conformance:** Does this align with KDF specification semantics?
- **Testability:** Does this include or update conformance fixtures?
- **Scope:** Does this stay within current feature boundaries?

Contributions that:

- Expand scope beyond KDF v0.1
- Add new validation rules not in the specification
- Add external service integrations

will generally be declined.

---

## Response Times

This is a volunteer-maintained project. Response times vary. Critical issues (validation bypass, incorrect results) are prioritized.

---

## Related Documents

- [SECURITY.md](SECURITY.md) — Security issue reporting
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) — Release process
