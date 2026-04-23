from __future__ import annotations

import re
from typing import List


_SENTENCE_PATTERN = re.compile(r"(?<=[。！？!?\.])\s*")


def split_sentences(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    chunks = _SENTENCE_PATTERN.split(text)
    return [c.strip() for c in chunks if c and c.strip()]


def simple_rewrite(text: str) -> str:
    replacements = {
        "因此": "由此可见",
        "所以": "因此",
        "但是": "然而",
        "并且": "同时",
        "我们": "本文",
        "可以": "能够",
        "非常": "较为",
        "重要": "关键",
    }
    out = text
    for old, new in replacements.items():
        out = out.replace(old, new)
    if "，" in out and len(out) > 20:
        parts = [p for p in out.split("，") if p]
        if len(parts) > 1:
            out = "，".join(parts[1:] + [parts[0]])
    return out


def heavy_rewrite(text: str) -> str:
    base = simple_rewrite(text)
    base = re.sub(r"\s+", "", base)
    if "。" in base:
        fragments = [x for x in base.split("。") if x]
        if len(fragments) > 1:
            base = "。".join(reversed(fragments)) + "。"
    return f"通过重构表达，{base}" if base else text
