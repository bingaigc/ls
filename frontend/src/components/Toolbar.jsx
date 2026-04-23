export default function Toolbar({
  onUpload,
  onBatchUpload,
  onRewriteAll,
  onRewriteRed,
  onRewriteHeavy,
  onAutoOptimize,
  onNextRed,
  onLockAll,
  onUnlockAll,
  onDownloadDocx,
  onExportPdf,
  onExportText,
  onExportJson
}) {
  return (
    <div className="rounded bg-white p-3 shadow">
      <div className="flex flex-wrap gap-2">
        <label className="cursor-pointer rounded bg-blue-600 px-3 py-2 text-xs text-white">
          docx 上传
          <input className="hidden" type="file" accept=".docx" onChange={(e) => onUpload(e.target.files?.[0])} />
        </label>
        <label className="cursor-pointer rounded bg-slate-700 px-3 py-2 text-xs text-white">
          批量上传
          <input className="hidden" multiple type="file" accept=".docx" onChange={(e) => onBatchUpload(Array.from(e.target.files || []))} />
        </label>
        <button className="rounded bg-indigo-600 px-3 py-2 text-xs text-white" onClick={onRewriteAll}>全量改写</button>
        <button className="rounded bg-orange-600 px-3 py-2 text-xs text-white" onClick={onRewriteRed}>只改红句</button>
        <button className="rounded bg-red-600 px-3 py-2 text-xs text-white" onClick={onRewriteHeavy}>只改重度句</button>
        <button className="rounded bg-emerald-600 px-3 py-2 text-xs text-white" onClick={onAutoOptimize}>自动优化（循环）</button>
        <button className="rounded bg-slate-600 px-3 py-2 text-xs text-white" onClick={onNextRed}>下一条红句</button>
        <button className="rounded bg-slate-600 px-3 py-2 text-xs text-white" onClick={onLockAll}>全锁</button>
        <button className="rounded bg-slate-600 px-3 py-2 text-xs text-white" onClick={onUnlockAll}>全解锁</button>
        <button className="rounded bg-violet-700 px-3 py-2 text-xs text-white" onClick={onDownloadDocx}>docx 下载</button>
        <button className="rounded bg-sky-700 px-3 py-2 text-xs text-white" onClick={onExportPdf}>导出 PDF</button>
        <button className="rounded bg-sky-700 px-3 py-2 text-xs text-white" onClick={onExportText}>导出文本</button>
        <button className="rounded bg-sky-700 px-3 py-2 text-xs text-white" onClick={onExportJson}>导出 JSON</button>
      </div>
    </div>
  )
}
