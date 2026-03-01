import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import Header from '../components/Header'
import StepBlock from '../components/StepBlock'

const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

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
  const [run, setRun] = useState(null)
  const [steps, setSteps] = useState([])
  const [status, setStatus] = useState('pending')
  const [error, setError] = useState(null)
  const wsRef = useRef(null)

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
        // re-fetch to get accurate step_count and ended_at
        api.getRun(id).then(data => setRun(data)).catch(() => {})
      }
      if (msg.event === 'run_error') {
        setStatus('failed')
      }
    }

    ws.onerror = () => {
      // pipeline may have finished before we connected — poll once
      setTimeout(() => {
        api.getRun(id).then(data => {
          setRun(data)
          setStatus(data.status)
          setSteps(data.steps || [])
        }).catch(() => {})
      }, 2000)
    }
  }

  if (error) return (
    <div className="min-h-screen bg-gray-50">
      <Header onNewResearch={() => navigate('/')} />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <p className="text-sm text-red-500">{error}</p>
      </main>
    </div>
  )

  if (!run) return (
    <div className="min-h-screen bg-gray-50">
      <Header onNewResearch={() => navigate('/')} />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <p className="text-sm text-gray-400">Loading...</p>
      </main>
    </div>
  )

  const pill = STATUS_PILL[status] || STATUS_PILL.pending
  const duration = formatDuration(run.started_at, run.ended_at)

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onNewResearch={() => navigate('/')} />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <button
          onClick={() => navigate('/')}
          className="text-sm text-gray-400 hover:text-gray-600 mb-6 block transition-colors"
        >
          ← Back
        </button>

        {/* Run header */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 mb-4">
          <div className="flex items-start justify-between gap-4">
            <h1 className="text-lg font-semibold text-gray-900 leading-snug">
              "{run.query}"
            </h1>
            <span className={`text-xs font-medium px-2.5 py-1 rounded-full flex-shrink-0 ${pill}`}>
              {status}
            </span>
          </div>
          <div className="mt-2 flex flex-wrap gap-4 text-xs text-gray-400">
            {run.user_name && <span>by {run.user_name}</span>}
            <span>Started {new Date(run.started_at).toLocaleString()}</span>
            {duration && <span>Duration {duration}</span>}
            {steps.length > 0 && <span>{steps.length} steps</span>}
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-2">
          {steps.length === 0 && status !== 'complete' && status !== 'failed' && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm px-5 py-8 text-center text-sm text-gray-400">
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
            <div className="flex items-center gap-2 px-4 py-3 text-sm text-gray-400">
              <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
              Running...
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
