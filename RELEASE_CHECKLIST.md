# Release Checklist

This document defines the release process for the KDF validator.

---

## Pre-Release Checks

Before tagging a release:

- [ ] All conformance fixtures PASS
  ```bash
  kdf conformance conformance/
  ```
- [ ] All unit tests pass (if present)
- [ ] CHANGELOG.md is updated with all changes
- [ ] Version bumped in `pyproject.toml`
- [ ] No breaking changes to CLI interface (for patch releases)
- [ ] Documentation reflects current behavior

---

## Version Discipline

- **Patch (0.1.x):** Bug fixes, documentation, conformance fixture updates
- **Minor (0.x.0):** New features, CLI additions (backward compatible)
- **Major (x.0.0):** Breaking changes, schema updates

Patch releases MUST NOT change validation semantics.

---

## Release Steps

1. **Final conformance run:**
   ```bash
   kdf conformance conformance/
   ```
   All fixtures must PASS.

2. **Update CHANGELOG.md:** Ensure date and version are correct

3. **Bump version in pyproject.toml**

4. **Commit:**
   ```
   git commit -am "Validator: release v0.1.x"
   ```

5. **Tag:**
   ```bash
   git tag -a v0.1.x -m "KDF Validator v0.1.x"
   ```

6. **Push:**
   ```bash
   git push origin main
   git push origin v0.1.x
   ```

7. **GitHub Release:** Create release on GitHub with:
   - Tag: `v0.1.x`
   - Title: `KDF Validator v0.1.x`
   - Body: Copy relevant CHANGELOG section

---

## Optional: PyPI Publishing

If publishing to PyPI:

```bash
python -m build
twine upload dist/*
```

Ensure credentials are configured. PyPI publishing is optional for this project.

---

## Post-Release

- [ ] Verify GitHub Release is visible
- [ ] Verify tag is accessible
- [ ] Test installation from source:
  ```bash
  pip install git+https://github.com/rabah2026/kdf-validator.git@v0.1.x
  ```
- [ ] Notify kdf-spec maintainers if validator behavior changed

---

## No Force-Push Rule

- Do NOT delete tags after release
- Do NOT force-push to main after tagging
- If errors are found, create a new patch release

---

## Related Documents

- [CHANGELOG.md](CHANGELOG.md) — Version history
- [SECURITY.md](SECURITY.md) — Security issue reporting
- [SUPPORT.md](SUPPORT.md) — Contribution expectations
