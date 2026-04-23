export default function DiffView({ item }) {
  if (!item) return <div className="rounded bg-white p-4 shadow">请选择句子</div>

  return (
    <div className="grid grid-cols-1 gap-3 rounded bg-white p-4 shadow md:grid-cols-2">
      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-700">原文</h3>
        <p className="min-h-24 rounded bg-slate-50 p-2 text-sm">{item.original}</p>
      </div>
      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-700">改写</h3>
        <p className="min-h-24 rounded bg-slate-50 p-2 text-sm">{item.rewritten}</p>
      </div>
    </div>
  )
}
