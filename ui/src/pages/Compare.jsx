import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import Header from '../components/Header'
import StepBlock from '../components/StepBlock'

const STATUS_PILL = {
  complete: 'bg-green-100 text-green-700',
  running:  'bg-yellow-100 text-yellow-700',
  pending:  'bg-gray-100 text-gray-500',
  failed:   'bg-red-100 text-red-600',
}

function RunColumn({ run, navigate }) {
  if (!run) return (
    <div className="flex-1 min-w-0">
      <p className="text-sm text-red-400">Failed to load run.</p>
    </div>
  )

  const pill = STATUS_PILL[run.status] || STATUS_PILL.pending
  const synthesis = (run.steps || []).find(s => s.step_type === 'synthesis')
  const otherSteps = (run.steps || []).filter(s => s.step_type !== 'synthesis')

  return (
    <div className="flex-1 min-w-0 space-y-3">
      {/* Run card */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-4">
        <button
          onClick={() => navigate(`/runs/${run.id}`)}
          className="text-xs text-cyan-500 hover:text-cyan-700 mb-2 block transition-colors"
        >
          Run #{run.id} &rarr;
        </button>
        <p className="text-sm font-semibold text-gray-900 dark:text-gray-100 leading-snug mb-2">"{run.query}"</p>
        <div className="flex flex-wrap gap-2 items-center text-xs text-gray-400 dark:text-gray-500">
          <span className={`font-medium px-2 py-0.5 rounded-full ${pill}`}>{run.status}</span>
          {run.user_name && <span>by {run.user_name}</span>}
          <span>{(run.steps || []).length} steps</span>
        </div>
      </div>

      {/* Synthesis first */}
      {synthesis && <StepBlock step={synthesis} defaultOpen={true} />}

      {/* Other steps collapsed */}
      {otherSteps.length > 0 && (
        <div className="space-y-2">
          {otherSteps.map(step => (
            <StepBlock key={step.id} step={step} defaultOpen={false} />
          ))}
        </div>
      )}
    </div>
  )
}

export default function Compare() {
  const { id1, id2 } = useParams()
  const navigate = useNavigate()
  const [run1, setRun1] = useState(undefined)
  const [run2, setRun2] = useState(undefined)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getRun(id1), api.getRun(id2)])
      .then(([r1, r2]) => {
        setRun1(r1)
        setRun2(r2)
      })
      .catch(() => {
        setRun1(null)
        setRun2(null)
      })
      .finally(() => setLoading(false))
  }, [id1, id2])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header onNewResearch={() => navigate('/')} />
      <main className="max-w-7xl mx-auto px-4 py-8">
        <button
          onClick={() => navigate(-1)}
          className="text-sm text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 mb-6 block transition-colors"
        >
          &larr; Back
        </button>

        <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">Compare Runs</h1>

        {loading ? (
          <p className="text-sm text-gray-400 dark:text-gray-500">Loading...</p>
        ) : (
          <div className="flex flex-col sm:flex-row gap-4 items-start">
            <RunColumn run={run1} navigate={navigate} />
            <div className="hidden sm:block w-px bg-gray-200 dark:bg-gray-700 self-stretch" />
            <RunColumn run={run2} navigate={navigate} />
          </div>
        )}
      </main>
    </div>
  )
}
