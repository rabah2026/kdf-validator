# Security Policy

This document describes how to report security issues in the KDF validator.

---

## Scope

Security issues in the KDF validator include:

- **Validation bypass:** Non-compliant artifacts incorrectly pass validation
- **Forgery enablement:** Validator behavior that could mask forged evidence
- **Nondeterminism:** Inconsistent validation results for identical inputs
- **Hash computation errors:** Incorrect canonical hashing behavior
- **Dependency vulnerabilities:** Critical vulnerabilities in direct dependencies

Security issues do NOT include:

- Feature requests or scope expansions
- Extraction quality or AI behavior (out of scope)
- Issues in the KDF specification (report to kdf-spec repository)

---

## How to Report

For security-sensitive issues, do not open a public issue.

**Contact:** Open a private security advisory via GitHub's Security tab, or email the repository owner.

Include:

1. Description of the issue
2. Steps to reproduce
3. Expected vs. actual behavior
4. Potential impact
5. Validator version affected

---

## Disclosure Process

1. **Acknowledgment:** We aim to acknowledge reports within 7 days
2. **Reproduction:** We will attempt to reproduce the issue
3. **Fix development:** Patches will be developed privately
4. **Release:** Fix will be released as a patch version
5. **Advisory:** Security advisory will be published after release

---

## Expectations

- No SLAs are provided; this is a volunteer-maintained project
- Critical issues (validation bypass, forgery) are prioritized
- Minor issues may be addressed in regular releases
- We follow coordinated disclosure practices

---

## Related Documents

- [SUPPORT.md](SUPPORT.md) — General support expectations
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) — Release process
