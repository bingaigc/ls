from __future__ import annotations

from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import List

import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.models.schemas import DocumentSession
from backend.pipeline.optimizer import compute_stats


def _make_chart_images(session: DocumentSession) -> tuple[str, str]:
    stats = compute_stats(session.items)
    labels = ["heavy", "medium", "safe"]
    values = [stats.heavy, stats.medium, stats.safe]
    colors_map = ["#ef4444", "#f97316", "#111827"]

    pie_tmp = NamedTemporaryFile(suffix=".png", delete=False)
    bar_tmp = NamedTemporaryFile(suffix=".png", delete=False)

    fig1, ax1 = plt.subplots(figsize=(4, 3))
    ax1.pie(values, labels=labels, autopct="%1.1f%%", colors=colors_map)
    ax1.set_title("句子分布饼图")
    fig1.savefig(pie_tmp.name, dpi=160, bbox_inches="tight")
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(4, 3))
    ax2.bar(labels, values, color=colors_map)
    ax2.set_title("等级统计柱状图")
    fig2.savefig(bar_tmp.name, dpi=160, bbox_inches="tight")
    plt.close(fig2)

    return pie_tmp.name, bar_tmp.name


def build_pdf_report(session: DocumentSession) -> bytes:
    stats = compute_stats(session.items)
    pie_path, bar_path = _make_chart_images(session)

    out = BytesIO()
    doc = SimpleDocTemplate(out, pagesize=A4)
    styles = getSampleStyleSheet()
    story: List = []

    story.append(Paragraph("论文优化分析报告", styles["Title"]))
    story.append(Spacer(1, 12))

    overview = Table(
        [
            ["total", "heavy", "medium", "score"],
            [str(stats.total), str(stats.heavy), str(stats.medium), str(stats.score)],
        ]
    )
    overview.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(overview)
    story.append(Spacer(1, 12))

    story.append(Image(pie_path, width=240, height=180))
    story.append(Spacer(1, 8))
    story.append(Image(bar_path, width=240, height=180))
    story.append(Spacer(1, 12))

    story.append(Paragraph("优化前后对比", styles["Heading2"]))
    for item in session.items:
        if item.level == "heavy":
            color = "red"
        elif item.level == "medium":
            color = "orange"
        else:
            color = "black"
        story.append(
            Paragraph(
                f"<font color='{color}'>[{item.id}] 原文：{item.original}<br/>改写：{item.rewritten}</font>",
                styles["BodyText"],
            )
        )
        story.append(Spacer(1, 6))

    doc.build(story)
    return out.getvalue()


def build_text_report(session: DocumentSession) -> str:
    stats = compute_stats(session.items)
    lines = [
        "论文优化分析报告",
        f"total={stats.total} heavy={stats.heavy} medium={stats.medium} safe={stats.safe} score={stats.score}",
        "",
    ]
    for item in session.items:
        lines.extend(
            [
                f"[{item.id}] level={item.level} similarity={item.similarity:.4f}",
                f"原文: {item.original}",
                f"改写: {item.rewritten}",
                "",
            ]
        )
    return "\n".join(lines)
