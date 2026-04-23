from __future__ import annotations

from typing import Callable, List

from backend.models.schemas import DocumentSession, DocumentStats, SentenceItem, VersionSnapshot
from backend.utils.config import load_config
from backend.utils.embedding import cosine_similarity_pairwise, embedding_service
from backend.utils.text_ops import heavy_rewrite, simple_rewrite, split_sentences


def classify_level(similarity: float) -> str:
    classify_cfg = load_config().get("classification", {})
    heavy_threshold = classify_cfg.get("heavy", 0.93)
    medium_threshold = classify_cfg.get("medium", 0.85)

    if similarity >= heavy_threshold:
        return "heavy"
    if medium_threshold <= similarity < heavy_threshold:
        return "medium"
    return "safe"


def rewrite_sentences(sentences: List[str]) -> List[str]:
    return [simple_rewrite(s) for s in sentences]


def rewrite_red(sentences: List[str]) -> List[str]:
    return [heavy_rewrite(s) for s in sentences]


def rewrite_heavy(sentences: List[str]) -> List[str]:
    return [heavy_rewrite(s) for s in sentences]


def compute_similarity(original_sentences: List[str], rewritten_sentences: List[str]) -> List[float]:
    emb_orig = embedding_service.embed_batch(original_sentences)
    emb_new = embedding_service.embed_batch(rewritten_sentences)
    return cosine_similarity_pairwise(emb_orig, emb_new)


def build_items(paragraphs: List[str]) -> List[SentenceItem]:
    items: List[SentenceItem] = []
    sid = 1
    for pidx, paragraph in enumerate(paragraphs):
        for sentence in split_sentences(paragraph):
            rewritten = simple_rewrite(sentence)
            items.append(
                SentenceItem(
                    id=sid,
                    paragraph_index=pidx,
                    original=sentence,
                    rewritten=rewritten,
                )
            )
            sid += 1

    sims = compute_similarity([i.original for i in items], [i.rewritten for i in items])
    for i, sim in zip(items, sims):
        i.similarity = float(sim)
        i.level = classify_level(i.similarity)
    return items


def compute_stats(items: List[SentenceItem]) -> DocumentStats:
    total = len(items)
    heavy = sum(1 for i in items if i.level == "heavy")
    medium = sum(1 for i in items if i.level == "medium")
    safe = sum(1 for i in items if i.level == "safe")
    heavy_ratio = (heavy / total) if total else 0.0
    score = max(0, 100 - heavy * 5 - medium * 2)
    return DocumentStats(total=total, heavy=heavy, medium=medium, safe=safe, heavy_ratio=heavy_ratio, score=score)


def rebuild_paragraphs(session: DocumentSession) -> List[str]:
    grouped: dict[int, List[str]] = {}
    for item in session.items:
        grouped.setdefault(item.paragraph_index, []).append(item.rewritten)

    result: List[str] = []
    max_p = max(grouped.keys()) if grouped else -1
    for idx in range(max_p + 1):
        result.append("".join(grouped.get(idx, [])))
    return result


def save_version(session: DocumentSession, title: str) -> None:
    version = len(session.versions) + 1
    snapshot_items = [SentenceItem.model_validate(i.model_dump()) for i in session.items]
    session.versions.append(VersionSnapshot(version=version, title=title, items=snapshot_items))


def recalc_items(items: List[SentenceItem]) -> None:
    sims = compute_similarity([i.original for i in items], [i.rewritten for i in items])
    for i, sim in zip(items, sims):
        i.similarity = float(sim)
        i.level = classify_level(i.similarity)


def apply_rewrite(
    session: DocumentSession,
    predicate: Callable[[SentenceItem], bool],
    rewriter: Callable[[List[str]], List[str]],
    log_prefix: str,
) -> int:
    targets = [i for i in session.items if predicate(i) and not i.locked]
    if not targets:
        return 0

    new_values = rewriter([i.rewritten for i in targets])
    for item, val in zip(targets, new_values):
        item.rewritten = val
        session.logs.append(f"{log_prefix} ID={item.id}")

    recalc_items(session.items)
    return len(targets)


def optimize_one_heavy(session: DocumentSession) -> tuple[bool, str, int | None]:
    stop_heavy_ratio = load_config().get("optimization", {}).get("stop_heavy_ratio", 0.05)
    stats = compute_stats(session.items)
    if stats.heavy_ratio < stop_heavy_ratio:
        return True, "达到停止条件", None

    for item in session.items:
        if item.level == "heavy" and not item.locked:
            session.logs.append(f"正在优化句子 ID={item.id} 相似度={item.similarity:.2f}")
            item.rewritten = rewrite_heavy([item.rewritten])[0]
            recalc_items(session.items)
            return False, f"已优化句子 {item.id}", item.id

    return True, "无可优化重度句", None
