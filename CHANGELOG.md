# Changelog

All notable changes to the KDF validator are documented in this file.

## [0.1.1] - 2026-01-15

### Changed
- **Node path chain validation**: Node paths are now validated as a proper
  chain. For a path like `document:doc1/section:s1/paragraph:p1`, the validator
  now verifies that `s1` is a descendant of `doc1` and `p1` is a descendant
  of `s1`. Previously, only ID existence was checked.

- **Valid requires fingerprint**: Evidence with `validation.status` of `valid`
  MUST now include at least one `span_fingerprint` anchor with `algo: sha256`.
  This enforces verifiable evidence for valid status claims.

- **Unique ID enforcement**: Added validation that `atoms[].id` values MUST
  be unique across the artifact. Document node IDs were already checked.

- **Expanded inference markers**: Added conservative additional inference
  markers: `may`, `might`, `could`, `likely`, `suggests`.

### Added
- Fixture `i007_path_chain_not_real.json`: Tests node path chain validation.
- Fixture `i008_duplicate_atom_id.json`: Tests duplicate atom ID detection.

### Fixed
- Updated `e003_conflicting_atoms.json` edge fixture to include required
  `span_fingerprint` anchors for valid status evidence.

## [0.1.0] - 2026-01-15

### Added
- Initial release of KDF validator
- JSON Schema validation for KDF v0.1 artifacts
- Semantic validation (evidence, spans, hashes, anchors)
- Conformance suite runner with PASS/FAIL + edge classification
- CLI with `validate` and `conformance` commands
