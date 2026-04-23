import { useState } from 'react'
import SimilarityBar from './SimilarityBar'

export default function SentenceCard({ item, onSave, onToggleLock, highlighted }) {
  const [text, setText] = useState(item.rewritten)
  const levelCls = item.level === 'heavy' ? 'border-red-400' : item.level === 'medium' ? 'border-orange-400' : 'border-emerald-400'

  return (
    <div id={`sentence-${item.id}`} className={`rounded-lg border-2 bg-white p-3 shadow ${levelCls} ${highlighted ? 'ring-2 ring-blue-400' : ''}`}>
      <div className="mb-2 flex items-center justify-between text-xs">
        <span className="font-semibold">ID #{item.id} / {item.level.toUpperCase()}</span>
        <button className="rounded bg-slate-100 px-2 py-1" onClick={() => onToggleLock(item.id, !item.locked)}>
          {item.locked ? '解锁' : '锁定'}
        </button>
      </div>
      <p className="mb-2 text-sm text-slate-600">原文：{item.original}</p>
      <textarea
        className="mb-2 w-full rounded border p-2 text-sm"
        value={text}
        disabled={item.locked}
        onChange={(e) => setText(e.target.value)}
      />
      <div className="mb-2">
        <SimilarityBar similarity={item.similarity} level={item.level} />
      </div>
      <button
        className="rounded bg-blue-600 px-3 py-1 text-xs text-white disabled:bg-slate-400"
        disabled={item.locked}
        onClick={() => onSave(item.id, text)}
      >
        保存
      </button>
    </div>
  )
}
