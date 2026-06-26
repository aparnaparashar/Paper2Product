import io
from pathlib import Path
from app.core.config import get_settings

settings = get_settings()


def extract_text(filename: str, file_bytes: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n\n".join(p.extract_text() or "" for p in reader.pages)
    elif ext in (".docx", ".doc"):
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    else:
        return file_bytes.decode("utf-8", errors="replace")


def save_upload(project_id: str, filename: str, file_bytes: bytes) -> str:
    path = Path(settings.upload_dir) / project_id
    path.mkdir(parents=True, exist_ok=True)
    dest = path / filename
    dest.write_bytes(file_bytes)
    return str(dest)


def store_embeddings(project_id: str, text: str):
    """
    Disabled — ChromaDB's default embedding function downloads a 79MB ONNX
    model into memory on first use, which exceeds Render's 512MB free tier
    and crashes the server (causing apparent CORS errors on the next request).

    Embeddings aren't used anywhere in the report pipeline, so this is a no-op.
    Re-enable only on a plan with >1GB RAM, or swap in a lightweight remote
    embedding API instead of the local ONNX model.
    """
    pass