import { useNavigate } from 'react-router-dom'

const STATUS_DOT = {
  complete: 'bg-green-500',
  running:  'bg-yellow-400 animate-pulse',
  pending:  'bg-gray-300 animate-pulse',
  failed:   'bg-red-500',
}

function timeAgo(dateStr) {
  const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000)
  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)} hr ago`
  return `${Math.floor(diff / 86400)}d ago`
}

export default function RunCard({ run }) {
  const navigate = useNavigate()
  const dot = STATUS_DOT[run.status] || 'bg-gray-300'

  return (
    <button
      onClick={() => navigate(`/runs/${run.id}`)}
      className="w-full text-left px-5 py-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors border-b border-gray-100 dark:border-gray-700 last:border-0 flex items-start gap-3 group"
    >
      <span className={`mt-1.5 w-2 h-2 rounded-full flex-shrink-0 ${dot}`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-900 dark:text-gray-100 truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
          <span className="font-medium">{run.user_name ?? 'Anonymous'}</span>
          {' ran: '}
          <span>"{run.query}"</span>
        </p>
      </div>
      <div className="flex-shrink-0 text-right text-xs text-gray-400 dark:text-gray-500 space-y-0.5">
        <p>{timeAgo(run.started_at)}</p>
        {run.step_count > 0 && (
          <p>{run.step_count} steps</p>
        )}
      </div>
    </button>
  )
}
