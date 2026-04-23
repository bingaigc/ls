import { useMemo, useState } from 'react'
import {
  batchUpload,
  downloadDocx,
  downloadJson,
  downloadPdf,
  downloadText,
  editSentence,
  lockAll,
  optimizeStep,
  rewriteAll,
  rewriteHeavy,
  rewriteRed,
  switchVersion,
  toggleSentenceLock,
  uploadDocx
} from './api'
import DiffView from './components/DiffView'
import LogPanel from './components/LogPanel'
import MiniMap from './components/MiniMap'
import ProgressBar from './components/ProgressBar'
import ScorePanel from './components/ScorePanel'
import SentenceCard from './components/SentenceCard'
import Toolbar from './components/Toolbar'
import VersionPanel from './components/VersionPanel'

export default function App() {
  const [sessionId, setSessionId] = useState('')
  const [filename, setFilename] = useState('')
  const [items, setItems] = useState([])
  const [stats, setStats] = useState({ total: 0, heavy: 0, medium: 0, safe: 0, heavy_ratio: 0, score: 0 })
  const [logs, setLogs] = useState([])
  const [versions, setVersions] = useState([])
  const [selectedId, setSelectedId] = useState(null)

  const selected = useMemo(() => items.find((x) => x.id === selectedId), [items, selectedId])

  const syncData = (data) => {
    setSessionId(data.session_id)
    setFilename(data.filename)
    setItems(data.items || [])
    setStats(data.stats || stats)
    setVersions(data.versions || [])
    setLogs(data.logs || [])
  }

  const handleUpload = async (file) => {
    if (!file) return
    const data = await uploadDocx(file)
    syncData(data)
  }

  const handleBatchUpload = async (files) => {
    if (!files.length) return
    const result = await batchUpload(files)
    setLogs((prev) => [...prev, `批量处理完成，共 ${result.results.length} 个文件`])
  }

  const applyAction = async (fn) => {
    if (!sessionId) return
    const data = await fn(sessionId)
    syncData(data)
  }

  const runAutoOptimize = async () => {
    if (!sessionId) return
    let done = false
    let optimizedCount = 0
    while (!done) {
      const data = await optimizeStep(sessionId)
      setItems(data.items)
      setStats(data.stats)
      setLogs(data.logs)
      if (data.optimized_sentence_id) {
        optimizedCount += 1
        setSelectedId(data.optimized_sentence_id)
        document.getElementById(`sentence-${data.optimized_sentence_id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
      done = data.done
      if (done) break
    }
    setLogs((prev) => [...prev, `优化完成，共优化 ${optimizedCount} 句`])
  }

  const handleSaveSentence = async (id, text) => {
    if (!sessionId) return
    const data = await editSentence(sessionId, id, text)
    syncData(data)
  }

  const handleToggleLock = async (id, locked) => {
    if (!sessionId) return
    const data = await toggleSentenceLock(sessionId, id, locked)
    syncData(data)
  }

  const goNextRed = () => {
    const redIds = items.filter((i) => i.level !== 'safe').map((i) => i.id)
    if (!redIds.length) return
    const currentIndex = redIds.findIndex((id) => id === selectedId)
    const nextId = redIds[(currentIndex + 1) % redIds.length]
    setSelectedId(nextId)
    document.getElementById(`sentence-${nextId}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }

  const onSwitchVersion = async (version) => {
    if (!sessionId) return
    const data = await switchVersion(sessionId, version)
    syncData(data)
  }

  return (
    <div className="mx-auto max-w-7xl space-y-4 p-4">
      <h1 className="text-2xl font-bold">论文优化与分析系统</h1>
      <div className="text-sm text-slate-600">当前文件：{filename || '未上传'}</div>

      <Toolbar
        onUpload={handleUpload}
        onBatchUpload={handleBatchUpload}
        onRewriteAll={() => applyAction(rewriteAll)}
        onRewriteRed={() => applyAction(rewriteRed)}
        onRewriteHeavy={() => applyAction(rewriteHeavy)}
        onAutoOptimize={runAutoOptimize}
        onNextRed={goNextRed}
        onLockAll={() => applyAction((id) => lockAll(id, true))}
        onUnlockAll={() => applyAction((id) => lockAll(id, false))}
        onDownloadDocx={() => sessionId && downloadDocx(sessionId)}
        onExportPdf={() => sessionId && downloadPdf(sessionId)}
        onExportText={() => sessionId && downloadText(sessionId)}
        onExportJson={() => sessionId && downloadJson(sessionId)}
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
        <div className="space-y-4 lg:col-span-1">
          <ScorePanel stats={stats} />
          <ProgressBar heavyRatio={stats.heavy_ratio || 0} />
          <MiniMap items={items} onSelect={(id) => setSelectedId(id)} />
          <VersionPanel versions={versions} onSwitch={onSwitchVersion} />
          <LogPanel logs={logs} />
        </div>

        <div className="space-y-4 lg:col-span-3">
          <DiffView item={selected} />
          <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
            {items.map((item) => (
              <div key={item.id} onClick={() => setSelectedId(item.id)}>
                <SentenceCard
                  item={item}
                  highlighted={selectedId === item.id}
                  onSave={handleSaveSentence}
                  onToggleLock={handleToggleLock}
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
