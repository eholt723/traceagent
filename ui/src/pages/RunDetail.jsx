import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { useUser } from '../UserContext'
import Header from '../components/Header'
import StepBlock from '../components/StepBlock'

// Derive WS base URL from env or window.location at runtime
const WS_BASE = (() => {
  const explicit = import.meta.env.VITE_WS_URL
  if (explicit) return explicit
  const apiEnv = import.meta.env.VITE_API_URL
  // env var set to non-empty string (e.g. local dev with VITE_API_URL set)
  if (apiEnv) return apiEnv.replace(/^http/, 'ws')
  // env var not defined at all → local dev default
  if (apiEnv === undefined) return 'ws://localhost:8000'
  // env var set to '' → same-origin production
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${window.location.host}`
})()

const STATUS_PILL = {
  complete: 'bg-green-100 text-green-700',
  running:  'bg-yellow-100 text-yellow-700',
  pending:  'bg-gray-100 text-gray-500',
  failed:   'bg-red-100 text-red-600',
}

function formatDuration(started, ended) {
  if (!ended) return null
  const ms = new Date(ended) - new Date(started)
  return ms < 60000 ? `${(ms / 1000).toFixed(0)}s` : `${(ms / 60000).toFixed(1)}m`
}

export default function RunDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useUser()
  const [run, setRun] = useState(null)
  const [steps, setSteps] = useState([])
  const [status, setStatus] = useState('pending')
  const [error, setError] = useState(null)
  const [runError, setRunError] = useState(null)
  const wsRef = useRef(null)

  // fork state
  const [forkOpen, setForkOpen] = useState(false)
  const [forkQuery, setForkQuery] = useState('')
  const [forking, setForking] = useState(false)

  // compare picker state
  const [compareOpen, setCompareOpen] = useState(false)
  const [compareRuns, setCompareRuns] = useState([])
  const [compareFetching, setCompareFetching] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const data = await api.getRun(id)
        if (cancelled) return
        setRun(data)
        setStatus(data.status)
        setSteps(data.steps || [])

        if (data.status === 'pending' || data.status === 'running') {
          connectWs(data.steps || [])
        }
      } catch {
        if (!cancelled) setError('Run not found.')
      }
    }

    load()
    return () => {
      cancelled = true
      if (wsRef.current) wsRef.current.close()
    }
  }, [id])

  function connectWs(existingSteps) {
    const knownIds = new Set(existingSteps.map(s => s.id))
    const ws = new WebSocket(`${WS_BASE}/ws/runs/${id}`)
    wsRef.current = ws

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      if (msg.event === 'step_complete') {
        const step = msg.data
        if (!knownIds.has(step.id)) {
          knownIds.add(step.id)
          setSteps(prev => [...prev, step])
        }
      }
      if (msg.event === 'run_complete') {
        setStatus('complete')
        api.getRun(id).then(data => setRun(data)).catch(() => {})
      }
      if (msg.event === 'run_error') {
        setStatus('failed')
        if (msg.data?.error) setRunError(msg.data.error)
      }
    }

    ws.onerror = () => {
      setTimeout(() => {
        api.getRun(id).then(data => {
          setRun(data)
          setStatus(data.status)
          setSteps(data.steps || [])
        }).catch(() => {})
      }, 2000)
    }
  }

  async function handleFork(e) {
    e.preventDefault()
    const q = forkQuery.trim()
    if (!q) return
    setForking(true)
    try {
      const newRun = await api.forkRun(id, q, user?.id ?? null)
      navigate(`/runs/${newRun.id}`)
    } catch {
      setForking(false)
    }
  }

  async function openCompare() {
    const next = !compareOpen
    setCompareOpen(next)
    if (next && compareRuns.length === 0) {
      setCompareFetching(true)
      try {
        const data = await api.listRuns(20)
        setCompareRuns(data.filter(r => r.id !== Number(id) && r.status === 'complete'))
      } catch {}
      setCompareFetching(false)
    }
  }

  if (error) return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header onNewResearch={() => navigate('/')} />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <p className="text-sm text-red-500">{error}</p>
      </main>
    </div>
  )

  if (!run) return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header onNewResearch={() => navigate('/')} />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <p className="text-sm text-gray-400">Loading...</p>
      </main>
    </div>
  )

  const pill = STATUS_PILL[status] || STATUS_PILL.pending
  const duration = formatDuration(run.started_at, run.ended_at)

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header onNewResearch={() => navigate('/')} />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <button
          onClick={() => navigate('/')}
          className="text-sm text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 mb-6 block transition-colors"
        >
          &larr; Back
        </button>

        {/* Run header */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-5 mb-2">
          <div className="flex items-start justify-between gap-4">
            <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100 leading-snug">
              "{run.query}"
            </h1>
            <span className={`text-xs font-medium px-2.5 py-1 rounded-full flex-shrink-0 ${pill}`}>
              {status}
            </span>
          </div>
          <div className="mt-2 flex flex-wrap gap-4 text-xs text-gray-400 dark:text-gray-500">
            {run.user_name && <span>by {run.user_name}</span>}
            <span>Started {new Date(run.started_at).toLocaleString()}</span>
            {duration && <span>Duration {duration}</span>}
            {steps.length > 0 && <span>{steps.length} steps</span>}
            {run.forked_from_id && (
              <button
                onClick={() => navigate(`/runs/${run.forked_from_id}`)}
                className="text-cyan-400 hover:text-cyan-600 transition-colors"
              >
                Forked from #{run.forked_from_id}
              </button>
            )}
          </div>
          {status === 'complete' && (
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => {
                  setForkOpen(v => !v)
                  setForkQuery(run.query)
                  setCompareOpen(false)
                }}
                className="text-xs px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Fork
              </button>
              <button
                onClick={() => { openCompare(); setForkOpen(false) }}
                className="text-xs px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Compare
              </button>
            </div>
          )}
        </div>

        {/* Fork panel */}
        {forkOpen && (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-cyan-200 dark:border-cyan-800 shadow-sm p-4 mb-2">
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">Fork this run — edit the query if you like</p>
            <form onSubmit={handleFork} className="flex gap-2">
              <input
                type="text"
                value={forkQuery}
                onChange={e => setForkQuery(e.target.value)}
                autoFocus
                className="flex-1 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              />
              <button
                type="submit"
                disabled={!forkQuery.trim() || forking}
                className="bg-cyan-600 hover:bg-cyan-700 disabled:opacity-40 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
              >
                {forking ? 'Forking...' : 'Fork'}
              </button>
              <button
                type="button"
                onClick={() => setForkOpen(false)}
                className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 px-2 transition-colors"
              >
                &times;
              </button>
            </form>
          </div>
        )}

        {/* Compare picker */}
        {compareOpen && (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-4 mb-2">
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">Compare with another completed run</p>
            {compareFetching ? (
              <p className="text-sm text-gray-400 dark:text-gray-500">Loading runs...</p>
            ) : compareRuns.length === 0 ? (
              <p className="text-sm text-gray-400 dark:text-gray-500">No other completed runs to compare.</p>
            ) : (
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {compareRuns.map(r => (
                  <button
                    key={r.id}
                    onClick={() => navigate(`/compare/${id}/${r.id}`)}
                    className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-sm transition-colors"
                  >
                    <span className="font-medium text-gray-800 dark:text-gray-200 block truncate">"{r.query}"</span>
                    <span className="text-xs text-gray-400 dark:text-gray-500">
                      #{r.id}{r.user_name ? ` · by ${r.user_name}` : ''}
                    </span>
                  </button>
                ))}
              </div>
            )}
            <button
              onClick={() => setCompareOpen(false)}
              className="mt-2 text-xs text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              Cancel
            </button>
          </div>
        )}

        {/* Error banner */}
        {runError && (
          <div className="mt-2 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl text-sm text-red-700 dark:text-red-300">
            {runError}
          </div>
        )}

        {/* Steps */}
        <div className="space-y-2 mt-2">
          {steps.length === 0 && status !== 'complete' && status !== 'failed' && (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm px-5 py-8 text-center text-sm text-gray-400 dark:text-gray-500">
              Agent is starting...
            </div>
          )}
          {steps.map((step, i) => (
            <StepBlock
              key={step.id}
              step={step}
              defaultOpen={step.step_type === 'synthesis' || i === steps.length - 1}
            />
          ))}
          {(status === 'pending' || status === 'running') && steps.length > 0 && (
            <div className="flex items-center gap-2 px-4 py-3 text-sm text-gray-400 dark:text-gray-500">
              <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
              Running...
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
