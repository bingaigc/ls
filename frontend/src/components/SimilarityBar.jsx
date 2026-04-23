export default function SimilarityBar({ similarity, level }) {
  const pct = Math.max(0, Math.min(100, similarity * 100))
  const color = level === 'heavy' ? 'bg-red-500' : level === 'medium' ? 'bg-orange-500' : 'bg-emerald-500'

  return (
    <div className="w-full">
      <div className="h-2 w-full rounded bg-slate-200">
        <div className={`h-2 rounded ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <div className="mt-1 text-xs text-slate-500">相似度: {similarity.toFixed(3)}</div>
    </div>
  )
}
