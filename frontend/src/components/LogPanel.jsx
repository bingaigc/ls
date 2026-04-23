import { useEffect, useRef } from 'react'

export default function LogPanel({ logs }) {
  const ref = useRef(null)

  useEffect(() => {
    if (ref.current) {
      ref.current.scrollTop = ref.current.scrollHeight
    }
  }, [logs])

  return (
    <div className="rounded bg-slate-900 p-3 text-xs text-slate-100 shadow">
      <h3 className="mb-2 font-semibold">LogPanel</h3>
      <div ref={ref} className="max-h-64 overflow-auto space-y-1">
        {logs.map((line, idx) => (
          <div key={`${idx}-${line}`}>{line}</div>
        ))}
      </div>
    </div>
  )
}
