import { useState, useEffect } from 'react'
import Header from '../components/Header'
import { api } from '../api'

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">{label}</p>
      <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">{value}</p>
      {sub && <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">{sub}</p>}
    </div>
  )
}

function fmt_duration(ms) {
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)

  async function load() {
    try {
      const data = await api.getStats()
      setStats(data)
      setError(null)
    } catch (e) {
      setError('Failed to load stats.')
    }
  }

  useEffect(() => {
    load()
    const id = setInterval(load, 30000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Pipeline Stats</h1>
          <span className="text-xs text-gray-400 dark:text-gray-500">refreshes every 30s</span>
        </div>

        {error && (
          <p className="text-sm text-red-500 mb-4">{error}</p>
        )}

        {!stats && !error && (
          <p className="text-sm text-gray-500 dark:text-gray-400">Loading...</p>
        )}

        {stats && (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
              <StatCard
                label="Total Runs"
                value={stats.total_runs}
              />
              <StatCard
                label="Success Rate"
                value={`${stats.success_rate}%`}
                sub={`${stats.completed_runs} completed`}
              />
              <StatCard
                label="Avg Duration"
                value={fmt_duration(stats.avg_duration_ms)}
                sub="full pipeline"
              />
              <StatCard
                label="Reflection Loop Rate"
                value={`${stats.reflection_loop_rate}%`}
                sub={`${stats.runs_with_loops} runs looped`}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <StatCard
                label="Completed"
                value={stats.completed_runs}
              />
              <StatCard
                label="Failed"
                value={stats.failed_runs}
              />
              <StatCard
                label="Avg Steps / Run"
                value={stats.avg_steps_per_run}
              />
            </div>
          </>
        )}
      </main>
    </div>
  )
}
