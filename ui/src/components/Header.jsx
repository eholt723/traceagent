import { useNavigate } from 'react-router-dom'
import { useUser } from '../UserContext'

export default function Header({ onNewResearch }) {
  const { user } = useUser()
  const navigate = useNavigate()

  return (
    <header className="border-b border-gray-200 bg-white sticky top-0 z-40">
      <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="font-semibold text-gray-900 text-lg tracking-tight hover:text-indigo-600 transition-colors"
        >
          TraceAgent
        </button>
        <div className="flex items-center gap-4">
          {user && (
            <span className="text-sm text-gray-500 hidden sm:block">{user.name}</span>
          )}
          <button
            onClick={onNewResearch}
            className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            + New Research
          </button>
        </div>
      </div>
    </header>
  )
}
