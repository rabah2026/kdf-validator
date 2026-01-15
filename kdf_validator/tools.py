import hashlib

def compute_source_hash_from_text(text: str) -> str:
    """
    Compute SHA-256 hash of canonicalized text.
    Canonicalization:
    - Decode UTF-8 (assumed input is str, so already decoded)
    - Strip BOM if present
    - Normalize line endings to LF (\n)
    """
    # 1. Strip BOM
    if text.startswith("\ufeff"):
        text = text[1:]
    
    # 2. Normalize Line Endings (CRLF -> LF, CR -> LF)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # 3. Encode to UTF-8
    data = text.encode("utf-8")
    
    return hashlib.sha256(data).hexdigest()


def compute_span_fingerprint(text: str, start: int, end: int) -> str:
    """
    Compute SHA-256 fingerprint of a text span.
    Input text MUST be the text against which coordinates are valid.
    Usually this implies the text is already canonicalized if coordinates were generated from canonical text.
    """
    if start < 0 or end < 0:
        raise ValueError("Span coordinates must be non-negative")
    if start >= end:
        raise ValueError("Span start must be strictly less than end")
    if end > len(text):
        raise ValueError(f"Span end {end} exceeds text length {len(text)}")
        
    span = text[start:end]
    return hashlib.sha256(span.encode("utf-8")).hexdigest()
