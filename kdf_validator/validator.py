from __future__ import annotations

import json
import re
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

from jsonschema import Draft202012Validator


# v0.1.1: Expanded inference markers (conservative additions)
INFERENCE_MARKERS = [
    r"\bimplied\b",
    r"\bassumed\b",
    r"\btypically\b",
    r"\bgenerally\b",
    r"\bmost likely\b",
    r"\bprobably\b",
    r"\btherefore\b",
    r"\bwe conclude\b",
    r"\binferred\b",
    # v0.1.1 additions
    r"\bmay\b",
    r"\bmight\b",
    r"\bcould\b",
    r"\blikely\b",
    r"\bsuggests\b",
]


@dataclass
class Issue:
    code: str
    message: str
    path: str


def _load_schema() -> Dict[str, Any]:
    schema_path = Path(__file__).parent / "schema" / "kdf_v0_1.schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _iter_nodes(nodes: List[Dict[str, Any]], prefix: str = "documents") -> List[Tuple[str, Dict[str, Any]]]:
    out: List[Tuple[str, Dict[str, Any]]] = []
    for i, n in enumerate(nodes):
        p = f"{prefix}[{i}]"
        out.append((p, n))
        for j, c in enumerate(n.get("children", []) or []):
            out.extend(_iter_nodes([c], prefix=f"{p}.children[{j}]"))
    return out


def _build_node_index(doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Index by node id across all documents."""
    idx: Dict[str, Dict[str, Any]] = {}
    for _, n in _iter_nodes(doc["documents"]):
        idx[n["id"]] = n
    return idx


def _build_parent_map(doc: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """Build a map of node_id -> parent_id for path chain validation."""
    parent_map: Dict[str, Optional[str]] = {}
    
    def _traverse(nodes: List[Dict[str, Any]], parent_id: Optional[str] = None) -> None:
        for n in nodes:
            node_id = n.get("id")
            if node_id:
                parent_map[node_id] = parent_id
                for c in n.get("children", []) or []:
                    _traverse([c], node_id)
    
    for doc_node in doc.get("documents", []):
        node_id = doc_node.get("id")
        if node_id:
            parent_map[node_id] = None  # Top-level documents have no parent
            for c in doc_node.get("children", []) or []:
                _traverse([c], node_id)
    
    return parent_map


def _resolve_node_path_chain(doc: Dict[str, Any], node_path: str) -> bool:
    """
    v0.1.1: Path-chain validation.
    For a path like "document:doc1/section:s1/paragraph:p1":
    - doc1 must exist
    - s1 must exist as a descendant of doc1
    - p1 must exist as a descendant of s1
    """
    idx = _build_node_index(doc)
    parent_map = _build_parent_map(doc)
    
    parts = node_path.split("/")
    if not parts:
        return False
    
    # Parse all node IDs from path
    path_node_ids: List[str] = []
    for part in parts:
        if ":" not in part:
            return False
        _, node_id = part.split(":", 1)
        if node_id not in idx:
            return False
        path_node_ids.append(node_id)
    
    # Validate chain: each node must be a child (direct or indirect) of the previous
    for i in range(1, len(path_node_ids)):
        current_id = path_node_ids[i]
        expected_ancestor = path_node_ids[i - 1]
        
        # Walk up parent chain to find expected ancestor
        found = False
        walk_id: Optional[str] = current_id
        while walk_id is not None:
            parent_id = parent_map.get(walk_id)
            if parent_id == expected_ancestor:
                found = True
                break
            walk_id = parent_id
        
        if not found:
            return False
    
    return True


def _find_node_text_by_path(doc: Dict[str, Any], node_path: str) -> str | None:
    idx = _build_node_index(doc)
    parts = node_path.split("/")
    last = parts[-1]
    if ":" not in last:
        return None
    _, node_id = last.split(":", 1)
    node = idx.get(node_id)
    return None if node is None else node.get("text", "")


def _schema_validate(doc: Dict[str, Any]) -> List[Issue]:
    schema = _load_schema()
    v = Draft202012Validator(schema)
    issues: List[Issue] = []
    for err in sorted(v.iter_errors(doc), key=str):
        path = "/".join([str(p) for p in err.absolute_path])
        issues.append(Issue("SCHEMA", err.message, path))
    return issues


def _semantic_validate(doc: Dict[str, Any]) -> List[Issue]:
    issues: List[Issue] = []

    # sources must have unique ids
    src_ids = [s["id"] for s in doc.get("sources", [])]
    if len(set(src_ids)) != len(src_ids):
        issues.append(Issue("SOURCE_DUP", "Duplicate source.id values are not allowed", "sources"))

    sources_by_id = {s["id"]: s for s in doc.get("sources", [])}

    # v0.1.1: documents node ids must be unique across entire artifact
    all_node_ids: List[str] = []
    for _, n in _iter_nodes(doc.get("documents", [])):
        all_node_ids.append(n["id"])
    if len(set(all_node_ids)) != len(all_node_ids):
        issues.append(Issue("NODE_ID_DUP", "Duplicate node id values are not allowed across documents", "documents"))

    # v0.1.1: atoms[].id must be unique
    atoms = doc.get("atoms", []) or []
    atom_ids = [a.get("id") for a in atoms if a.get("id")]
    if len(set(atom_ids)) != len(atom_ids):
        issues.append(Issue("ATOM_ID_DUP", "Duplicate atom.id values are not allowed", "atoms"))

    for ai, atom in enumerate(atoms):
        a_path = f"atoms[{ai}]"

        # inference markers in payload are forbidden for v0.1 conformance fixtures
        payload = atom.get("payload", "")
        for pat in INFERENCE_MARKERS:
            if re.search(pat, payload, flags=re.IGNORECASE):
                issues.append(Issue("INFERRED_ATOM", "Atom payload contains inferred/non-source-backed phrasing", f"{a_path}.payload"))
                break

        ev_list = atom.get("evidence", []) or []
        if len(ev_list) == 0:
            issues.append(Issue("NO_EVIDENCE", "Atom must contain at least one evidence entry", f"{a_path}.evidence"))
            continue

        for ei, ev in enumerate(ev_list):
            e_path = f"{a_path}.evidence[{ei}]"
            source_id = ev.get("source_id")
            if source_id not in sources_by_id:
                issues.append(Issue("BAD_SOURCE", "Evidence source_id does not exist in sources", f"{e_path}.source_id"))

            # v0.1.1: node_path must be resolvable via path-chain validation
            node_path = ev.get("node_path")
            anchors = ev.get("locators", {}).get("anchors", []) or []
            has_node_path_anchor = any(a.get("type") == "node_path" for a in anchors)
            
            if node_path:
                if not _resolve_node_path_chain(doc, node_path):
                    issues.append(Issue("BAD_NODE_PATH", "Evidence node_path not resolvable or chain invalid", f"{e_path}.node_path"))

            if has_node_path_anchor:
                for aj, a in enumerate(anchors):
                    if a.get("type") == "node_path":
                        ap = a.get("path", "")
                        if not ap or not _resolve_node_path_chain(doc, ap):
                            issues.append(Issue("BAD_NODE_PATH_ANCHOR", "Evidence anchor node_path not resolvable or chain invalid", f"{e_path}.locators.anchors[{aj}]"))

            primary = ev.get("locators", {}).get("primary", {})
            if primary.get("type") == "text_offset":
                start = primary.get("start")
                end = primary.get("end")
                if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end < 0 or start >= end:
                    issues.append(Issue("BAD_SPAN", "Invalid text_offset span (start must be < end)", f"{e_path}.locators.primary"))
                # if node_path resolves, check bounds against node text
                if node_path and _resolve_node_path_chain(doc, node_path):
                    text = _find_node_text_by_path(doc, node_path)
                    if text is not None and isinstance(start, int) and isinstance(end, int) and end > len(text):
                        issues.append(Issue("SPAN_OOB", "Span end exceeds node text length", f"{e_path}.locators.primary"))

            # v0.1.1: valid requires fingerprint
            vstatus = ev.get("validation", {}).get("status")
            fp_entries = [a for a in anchors if a.get("type") == "span_fingerprint" and a.get("algo") == "sha256"]
            
            if vstatus == "valid":
                # v0.1.1: If status is valid, MUST have at least one sha256 span_fingerprint
                if not fp_entries:
                    issues.append(Issue("VALID_NO_FP", "Evidence with status 'valid' MUST include a sha256 span_fingerprint anchor", f"{e_path}.validation"))
            
            # Fingerprint mismatch check
            if fp_entries and node_path and _resolve_node_path_chain(doc, node_path):
                text = _find_node_text_by_path(doc, node_path) or ""
                start = primary.get("start")
                end = primary.get("end")
                if isinstance(start, int) and isinstance(end, int) and 0 <= start < end <= len(text):
                    span = text[start:end]
                    expected = _sha256_hex(span)
                    for fj, fp in enumerate(fp_entries):
                        val = fp.get("value", "")
                        if val != expected and vstatus == "valid":
                            issues.append(Issue("FP_MISMATCH_VALID", "Evidence marked valid but fingerprint does not match span", f"{e_path}.locators.anchors[{fj}]"))

    return issues


def validate_doc(doc: Dict[str, Any]) -> Tuple[bool, List[Issue]]:
    issues = []
    issues.extend(_schema_validate(doc))
    issues.extend(_semantic_validate(doc))
    ok = len(issues) == 0
    return ok, issues


def validate_file(path: Path) -> Tuple[bool, str]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    ok, issues = validate_doc(doc)
    report_lines = [f"[{'PASS' if ok else 'FAIL'}] {path}"]
    for it in issues:
        report_lines.append(f"- {it.code}: {it.message} @ {it.path}")
    return ok, "\n".join(report_lines)


def _classify_edge(doc: Dict[str, Any]) -> str:
    """Edge classification by looking at evidence.validation.status values."""
    statuses = []
    for atom in doc.get("atoms", []) or []:
        for ev in atom.get("evidence", []) or []:
            statuses.append(ev.get("validation", {}).get("status"))
    if any(s == "invalid" for s in statuses):
        return "invalid"
    if any(s == "needs_review" for s in statuses):
        return "needs_review"
    return "valid"


def run_conformance(root: Path) -> Tuple[bool, str]:
    sections = [("valid", True), ("invalid", False), ("edge", None)]
    report: List[str] = []
    overall_ok = True

    for sec, expected in sections:
        sec_path = root / sec
        files = sorted(sec_path.glob("*.json"))
        report.append(f"\n== {sec.upper()} ==")
        if not files:
            report.append(f"(no fixtures found in {sec_path})")
            overall_ok = False
            continue

        for f in files:
            ok, issues = validate_doc(json.loads(f.read_text(encoding="utf-8")))

            if sec == "edge":
                cls = _classify_edge(json.loads(f.read_text(encoding="utf-8")))
                if not ok:
                    overall_ok = False
                    report.append(f"[FAIL] {f.name} (edge file must be structurally valid)")
                    for it in issues:
                        report.append(f"  - {it.code}: {it.message} @ {it.path}")
                else:
                    report.append(f"[PASS] {f.name} (class={cls})")
                continue

            if expected is True:
                if ok:
                    report.append(f"[PASS] {f.name}")
                else:
                    overall_ok = False
                    report.append(f"[FAIL] {f.name} (expected PASS)")
                    for it in issues:
                        report.append(f"  - {it.code}: {it.message} @ {it.path}")

            if expected is False:
                if ok:
                    overall_ok = False
                    report.append(f"[FAIL] {f.name} (expected FAIL)")
                else:
                    report.append(f"[PASS] {f.name} (failed as expected)")

    report.insert(0, f"[{'PASS' if overall_ok else 'FAIL'}] KDF Conformance Suite")
    return overall_ok, "\n".join(report)
