export default function VersionPanel({ versions, onSwitch }) {
  return (
    <div className="rounded bg-white p-3 shadow">
      <h3 className="mb-2 text-sm font-semibold">版本管理</h3>
      <div className="space-y-1">
        {versions.map((v) => (
          <button
            key={v.version}
            onClick={() => onSwitch(v.version)}
            className="w-full rounded border border-slate-200 px-2 py-1 text-left text-xs hover:bg-slate-50"
          >
            v{v.version} - {v.title}
          </button>
        ))}
      </div>
    </div>
  )
}
