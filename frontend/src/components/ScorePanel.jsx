export default function ScorePanel({ stats }) {
  return (
    <div className="rounded bg-white p-3 shadow">
      <h3 className="mb-2 text-sm font-semibold">评分</h3>
      <div className="text-3xl font-bold text-slate-800">{stats?.score ?? 0}</div>
      <div className="mt-1 text-xs text-slate-500">score = 100 - heavy*5 - medium*2</div>
      <div className="mt-2 text-xs text-slate-600">
        heavy={stats?.heavy ?? 0} medium={stats?.medium ?? 0} safe={stats?.safe ?? 0}
      </div>
    </div>
  )
}
