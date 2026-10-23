"""Resume Checker – Flask entrypoint.

Routes:
  GET  /                       → single-page UI
  GET  /api/health             → liveness probe (used by Docker/systemd/nginx)
  GET  /api/presets            → list preset role JDs
  GET  /api/ai-info            → which AI provider is active
  POST /api/analyze            → multipart upload + optional jd_text / preset_id
  POST /api/tailor             → multipart upload + jd → tailored resume JSON
  POST /api/download/docx      → JSON body (tailored dict) → .docx file
  POST /api/download/pdf       → JSON body (tailored dict) → .pdf  file
"""

from __future__ import annotations

import os
import re
import tempfile
import uuid

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

from analyzer import analyze_resume, render_docx, render_pdf, tailor_resume
from analyzer.parser import parse_resume
from analyzer.presets import get_preset_jd, list_presets

APP_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "resume_checker_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "5"))
ALLOWED_EXT = {".pdf", ".docx"}

app = Flask(
    __name__,
    template_folder=os.path.join(APP_DIR, "templates"),
    static_folder=os.path.join(APP_DIR, "static"),
)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024

# When behind nginx, trust 1 hop of X-Forwarded-*
try:
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
except Exception:  # pragma: no cover
    pass


# ------------------------------- helpers -----------------------------------

def _save_upload() -> tuple[str | None, str | None, tuple | None]:
    """Return (saved_path, original_name, error_response)."""
    if "file" not in request.files:
        return None, None, (
            jsonify({"error": "No file uploaded. Use field name 'file'."}),
            400,
        )
    f = request.files["file"]
    if not f.filename:
        return None, None, (jsonify({"error": "Empty filename."}), 400)
    filename = secure_filename(f.filename)
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXT:
        return None, None, (
            jsonify({"error": f"Unsupported file type '{ext}'. Allowed: .pdf, .docx"}),
            400,
        )
    unique = f"{uuid.uuid4().hex}{ext}"
    saved = os.path.join(UPLOAD_DIR, unique)
    f.save(saved)
    return saved, filename, None


def _safe_filename_root(name: str) -> str:
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", name or "resume")
    return (base or "resume")[:60]


# ------------------------------- routes ------------------------------------

@app.get("/")
def index():
    return render_template(
        "index.html",
        max_upload_mb=MAX_UPLOAD_MB,
        ai_provider=os.environ.get("AI_PROVIDER", "rule_based"),
    )


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/ai-info")
def ai_info():
    return jsonify({
        "provider": os.environ.get("AI_PROVIDER", "rule_based"),
        "model": os.environ.get("AI_MODEL", ""),
        "ollama_url": os.environ.get("OLLAMA_URL", "http://localhost:11434"),
        "openai_base": os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1"),
    })


@app.get("/api/presets")
def presets():
    return jsonify({"presets": list_presets()})


@app.post("/api/analyze")
def analyze():
    saved_path, filename, err = _save_upload()
    if err:
        return err
    try:
        jd_text = (request.form.get("jd_text") or "").strip()
        preset_id = (request.form.get("preset_id") or "").strip() or None
        result = analyze_resume(saved_path, jd_text=jd_text, preset_id=preset_id)
        result["filename"] = filename
        return jsonify(result)
    except Exception as exc:  # pragma: no cover - defensive
        return jsonify({"error": f"Analysis failed: {exc}"}), 500
    finally:
        try:
            os.remove(saved_path)
        except OSError:
            pass


@app.post("/api/tailor")
def tailor():
    saved_path, filename, err = _save_upload()
    if err:
        return err
    try:
        jd_text = (request.form.get("jd_text") or "").strip()
        preset_id = (request.form.get("preset_id") or "").strip() or None
        if not jd_text and preset_id:
            jd_text = get_preset_jd(preset_id) or ""
        if not jd_text:
            return jsonify({
                "error": "A JD (jd_text) or preset_id is required for tailoring."
            }), 400

        parsed = parse_resume(saved_path)
        if not parsed["has_text"]:
            return jsonify({"error": "Could not extract text from the uploaded file."}), 400

        tailored = tailor_resume(parsed["text"], jd_text)
        tailored["_meta"] = tailored.get("_meta") or {}
        tailored["_meta"]["original_filename"] = filename
        return jsonify(tailored)
    except Exception as exc:  # pragma: no cover - defensive
        return jsonify({"error": f"Tailoring failed: {exc}"}), 500
    finally:
        try:
            os.remove(saved_path)
        except OSError:
            pass


@app.post("/api/download/docx")
def download_docx():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict) or "name" not in data:
        return jsonify({"error": "POST JSON body (tailored resume) is required."}), 400
    try:
        buf = render_docx(data)
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": f"DOCX render failed: {exc}"}), 500
    fname = f"{_safe_filename_root(data.get('name'))}_Tailored.docx"
    return send_file(
        buf,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=fname,
    )


@app.post("/api/download/pdf")
def download_pdf():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict) or "name" not in data:
        return jsonify({"error": "POST JSON body (tailored resume) is required."}), 400
    try:
        buf = render_pdf(data)
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": f"PDF render failed: {exc}"}), 500
    fname = f"{_safe_filename_root(data.get('name'))}_Tailored.pdf"
    return send_file(buf, mimetype="application/pdf",
                     as_attachment=True, download_name=fname)


# ------------------------------- errors ------------------------------------

@app.errorhandler(413)
def too_large(_e):
    return jsonify({"error": f"File too large. Max allowed: {MAX_UPLOAD_MB} MB."}), 413


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_ENV", "production") != "production"
    if os.environ.get("FLASK_ENV") == "production" and os.path.exists("/.dockerenv"):
        host = "0.0.0.0"  # noqa: S104 (intentional in container)
    app.run(host=host, port=port, debug=debug)
