const API_BASE = 'http://localhost:8000/api'
const SERVER_BASE = 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options)
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Request failed')
  }
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    return response.json()
  }
  return response.blob()
}

export function uploadDocx(file) {
  const fd = new FormData()
  fd.append('file', file)
  return request('/process', { method: 'POST', body: fd })
}

export function batchUpload(files) {
  const fd = new FormData()
  files.forEach((file) => fd.append('files', file))
  return request('/batch/process', { method: 'POST', body: fd })
}

export function rewriteAll(session_id) {
  return request('/rewrite/all', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id })
  })
}

export function rewriteRed(session_id) {
  return request('/rewrite/red', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id })
  })
}

export function rewriteHeavy(session_id) {
  return request('/rewrite/heavy', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id })
  })
}

export function optimizeStep(session_id) {
  return request('/optimize/step', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id })
  })
}

export function lockAll(session_id, locked) {
  return request('/lock/all', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, locked })
  })
}

export function editSentence(session_id, sentenceId, text) {
  return request(`/sentence/${sentenceId}/edit?session_id=${encodeURIComponent(session_id)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  })
}

export function toggleSentenceLock(session_id, sentenceId, locked) {
  return request(`/sentence/${sentenceId}/lock?session_id=${encodeURIComponent(session_id)}&locked=${locked}`, {
    method: 'POST'
  })
}

export function switchVersion(session_id, version) {
  return request('/version/switch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, version })
  })
}

export function downloadDocx(sessionId) {
  window.open(`${SERVER_BASE}/api/docx/download/${sessionId}`, '_blank')
}

export function downloadPdf(sessionId) {
  window.open(`${SERVER_BASE}/api/report/pdf/${sessionId}`, '_blank')
}

export function downloadText(sessionId) {
  window.open(`${SERVER_BASE}/api/report/text/${sessionId}`, '_blank')
}

export function downloadJson(sessionId) {
  window.open(`${SERVER_BASE}/api/report/json/${sessionId}`, '_blank')
}
