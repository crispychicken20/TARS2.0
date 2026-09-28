from core.config import settings

def simple_overlap_chunk(text: str, chunk_size: int | None = None, overlap: int | None = None):
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP
    text = text.strip().replace("\r", "")
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = end - overlap
        if start < 0: start = 0
    return chunks
