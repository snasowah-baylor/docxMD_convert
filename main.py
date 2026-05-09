import io
import pathlib

import mammoth
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

app = FastAPI(title="docx-to-md Converter", version="1.0")


# ── UI ────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})


# ── Conversion ────────────────────────────────────────────────────────────────

@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are accepted.")

    # Read uploaded bytes
    contents = await file.read()

    # Convert docx → markdown via mammoth
    try:
        result = mammoth.convert_to_markdown(io.BytesIO(contents))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {exc}")

    # Build output filename: report.docx → report.md
    stem = pathlib.Path(file.filename).stem
    md_filename = f"{stem}.md"
    md_bytes = result.value.encode("utf-8")

    return StreamingResponse(
        io.BytesIO(md_bytes),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{md_filename}"'},
    )
