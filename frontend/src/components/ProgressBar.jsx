export default function ProgressBar({ heavyRatio }) {
  const pct = Math.max(0, Math.min(100, heavyRatio * 100))

  return (
    <div className="rounded bg-white p-3 shadow">
      <div className="mb-1 text-sm font-semibold">红句比例</div>
      <div className="h-3 rounded bg-slate-200">
        <div className="h-3 rounded bg-red-500" style={{ width: `${pct}%` }} />
      </div>
      <div className="mt-1 text-xs text-slate-500">{pct.toFixed(2)}%（停止阈值: 5%）</div>
    </div>
  )
}
