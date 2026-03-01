import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useUser } from '../UserContext'
import Header from '../components/Header'
import RunCard from '../components/RunCard'

export default function ActivityWall() {
  const { user } = useUser()
  const navigate = useNavigate()
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [showInput, setShowInput] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const fetchRuns = useCallback(async () => {
    try {
      const data = await api.listRuns(20)
      setRuns(data)
    } catch {
      // silent — keep existing list on refresh failure
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchRuns()
    const interval = setInterval(fetchRuns, 15000)
    return () => clearInterval(interval)
  }, [fetchRuns])

  async function handleSubmit(e) {
    e.preventDefault()
    const trimmed = query.trim()
    if (!trimmed) return
    setSubmitting(true)
    setError(null)
    try {
      const run = await api.createRun(trimmed, user?.id ?? null)
      navigate(`/runs/${run.id}`)
    } catch {
      setError('Failed to start research. Please try again.')
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header onNewResearch={() => setShowInput(true)} />

      <main className="max-w-4xl mx-auto px-4 py-8">
        {showInput && (
          <div className="mb-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-5">
            <h2 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">New Research</h2>
            <form onSubmit={handleSubmit} className="flex gap-3">
              <input
                type="text"
                placeholder="What do you want to research?"
                value={query}
                onChange={e => setQuery(e.target.value)}
                autoFocus
                className="flex-1 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
              <button
                type="submit"
                disabled={!query.trim() || submitting}
                className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium px-5 py-2.5 rounded-lg transition-colors"
              >
                {submitting ? 'Starting...' : 'Research'}
              </button>
              <button
                type="button"
                onClick={() => { setShowInput(false); setQuery(''); setError(null) }}
                className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 px-2 transition-colors"
              >
                ✕
              </button>
            </form>
            {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
          </div>
        )}

        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
            <h1 className="font-semibold text-gray-900 dark:text-gray-100">Recent Research</h1>
            <button
              onClick={fetchRuns}
              className="text-xs text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              Refresh
            </button>
          </div>

          {loading ? (
            <div className="px-5 py-12 text-center text-sm text-gray-400 dark:text-gray-500">Loading...</div>
          ) : runs.length === 0 ? (
            <div className="px-5 py-12 text-center text-sm text-gray-400 dark:text-gray-500">
              No research runs yet. Be the first.
            </div>
          ) : (
            <div>
              {runs.map(run => (
                <RunCard key={run.id} run={run} />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
