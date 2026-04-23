from __future__ import annotations

import json
import uuid
import base64
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from backend.models.schemas import (
    AutoOptimizeStepResponse,
    DocumentSession,
    EditSentenceRequest,
    LockAllRequest,
    ProcessResponse,
    RewriteRequest,
    VersionSwitchRequest,
)
from backend.models.session_store import store
from backend.pipeline.optimizer import (
    apply_rewrite,
    build_items,
    compute_stats,
    optimize_one_heavy,
    rebuild_paragraphs,
    recalc_items,
    rewrite_heavy,
    rewrite_red,
    rewrite_sentences,
    save_version,
)
from backend.report import build_pdf_report, build_text_report
from backend.utils.docx_io import read_docx, write_docx


app = FastAPI(title="Paper Optimization and Analysis System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _response(session: DocumentSession) -> ProcessResponse:
    return ProcessResponse(
        session_id=session.session_id,
        filename=session.filename,
        items=session.items,
        stats=compute_stats(session.items),
        versions=session.versions,
        logs=session.logs,
    )


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/process", response_model=ProcessResponse)
async def process_docx(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx is supported")

    content = await file.read()
    paragraphs = read_docx(content)
    items = build_items(paragraphs)
    session = DocumentSession(
        session_id=str(uuid.uuid4()),
        filename=file.filename,
        paragraphs=paragraphs,
        items=items,
        logs=[f"已加载文档 {file.filename}", f"初始红句比例={compute_stats(items).heavy_ratio:.2%}"],
    )
    save_version(session, "初始版本")
    store.set(session)
    return _response(session)


@app.post("/api/rewrite/all", response_model=ProcessResponse)
def rewrite_all(req: RewriteRequest):
    session = store.get(req.session_id)
    changed = apply_rewrite(session, lambda i: True, rewrite_sentences, "全量改写句子")
    save_version(session, f"全量改写({changed})")
    session.logs.append(f"优化完成，共优化 {changed} 句")
    return _response(session)


@app.post("/api/rewrite/red", response_model=ProcessResponse)
def rewrite_only_red(req: RewriteRequest):
    session = store.get(req.session_id)
    changed = apply_rewrite(session, lambda i: i.level in {"heavy", "medium"}, rewrite_red, "红句改写")
    save_version(session, f"红句改写({changed})")
    session.logs.append(f"优化完成，共优化 {changed} 句")
    return _response(session)


@app.post("/api/rewrite/heavy", response_model=ProcessResponse)
def rewrite_only_heavy(req: RewriteRequest):
    session = store.get(req.session_id)
    changed = apply_rewrite(session, lambda i: i.level == "heavy", rewrite_heavy, "重度改写")
    save_version(session, f"重度改写({changed})")
    session.logs.append(f"优化完成，共优化 {changed} 句")
    return _response(session)


@app.post("/api/optimize/step", response_model=AutoOptimizeStepResponse)
def auto_optimize_step(req: RewriteRequest):
    session = store.get(req.session_id)
    done, msg, sid = optimize_one_heavy(session)
    if done:
        save_version(session, "自动优化完成")
    return AutoOptimizeStepResponse(
        done=done,
        message=msg,
        optimized_sentence_id=sid,
        items=session.items,
        stats=compute_stats(session.items),
        logs=session.logs,
    )


@app.post("/api/lock/all", response_model=ProcessResponse)
def lock_all(req: LockAllRequest):
    session = store.get(req.session_id)
    for item in session.items:
        item.locked = req.locked
    save_version(session, "全锁" if req.locked else "全解锁")
    session.logs.append("已全锁" if req.locked else "已全解锁")
    return _response(session)


@app.post("/api/sentence/{sentence_id}/edit", response_model=ProcessResponse)
def edit_sentence(sentence_id: int, req: EditSentenceRequest, session_id: str):
    session = store.get(session_id)
    target = next((i for i in session.items if i.id == sentence_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Sentence not found")
    if target.locked:
        raise HTTPException(status_code=400, detail="Sentence is locked")
    target.rewritten = req.text
    recalc_items(session.items)
    save_version(session, f"编辑句子{sentence_id}")
    session.logs.append(f"手动编辑句子 ID={sentence_id}")
    return _response(session)


@app.post("/api/sentence/{sentence_id}/lock", response_model=ProcessResponse)
def lock_sentence(sentence_id: int, session_id: str, locked: bool):
    session = store.get(session_id)
    target = next((i for i in session.items if i.id == sentence_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Sentence not found")
    target.locked = locked
    save_version(session, f"{'锁定' if locked else '解锁'}句子{sentence_id}")
    session.logs.append(f"{'锁定' if locked else '解锁'}句子 ID={sentence_id}")
    return _response(session)


@app.post("/api/version/switch", response_model=ProcessResponse)
def switch_version(req: VersionSwitchRequest):
    session = store.get(req.session_id)
    version = next((v for v in session.versions if v.version == req.version), None)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    session.items = [i.model_copy(deep=True) for i in version.items]
    session.logs.append(f"切换到版本 {req.version} - {version.title}")
    return _response(session)


@app.get("/api/docx/download/{session_id}")
def download_docx(session_id: str):
    session = store.get(session_id)
    paragraphs = rebuild_paragraphs(session)
    content = write_docx(paragraphs)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=optimized-{session.filename}"},
    )


@app.get("/api/report/pdf/{session_id}")
def export_pdf(session_id: str):
    session = store.get(session_id)
    content = build_pdf_report(session)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report-{session.filename}.pdf"},
    )


@app.get("/api/report/text/{session_id}")
def export_text(session_id: str):
    session = store.get(session_id)
    content = build_text_report(session)
    return Response(
        content=content.encode("utf-8"),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=report-{session.filename}.txt"},
    )


@app.get("/api/report/json/{session_id}")
def export_json(session_id: str):
    session = store.get(session_id)
    payload = {
        "session_id": session.session_id,
        "filename": session.filename,
        "stats": compute_stats(session.items).model_dump(),
        "items": [i.model_dump() for i in session.items],
        "versions": [v.model_dump() for v in session.versions],
        "logs": session.logs,
    }
    return Response(
        content=json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=report-{session.filename}.json"},
    )


@app.post("/api/batch/process")
async def batch_process(files: List[UploadFile] = File(...)):
    results = []
    report_sessions: List[DocumentSession] = []

    for file in files:
        if not file.filename.lower().endswith(".docx"):
            continue
        content = await file.read()
        paragraphs = read_docx(content)
        items = build_items(paragraphs)
        session = DocumentSession(
            session_id=str(uuid.uuid4()),
            filename=file.filename,
            paragraphs=paragraphs,
            items=items,
            logs=[f"批处理已处理 {file.filename}"],
        )
        save_version(session, "批处理初始")
        store.set(session)
        report_sessions.append(session)
        results.append({
            "session_id": session.session_id,
            "filename": file.filename,
            "stats": compute_stats(items).model_dump(),
        })

    if not report_sessions:
        raise HTTPException(status_code=400, detail="No valid docx files")

    merged = DocumentSession(
        session_id=str(uuid.uuid4()),
        filename="batch",
        items=[i for s in report_sessions for i in s.items],
    )
    pdf_content = build_pdf_report(merged)

    return JSONResponse(
        {
            "results": results,
            "batch_report_pdf_base64": base64.b64encode(pdf_content).decode("utf-8"),
            "note": "Decode base64 to bytes to save the merged PDF report.",
        }
    )
