import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUser } from '../UserContext'

export default function Header({ onNewResearch }) {
  const { user } = useUser()
  const navigate = useNavigate()
  const [dark, setDark] = useState(() => localStorage.getItem('dark') === 'true')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('dark', String(dark))
  }, [dark])

  return (
    <header className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 sticky top-0 z-40">
      <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="font-semibold text-gray-900 dark:text-gray-100 text-lg tracking-tight hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
        >
          TraceAgent
        </button>
        <div className="flex items-center gap-3">
          {user && (
            <span className="text-sm text-gray-500 dark:text-gray-400 hidden sm:block">{user.name}</span>
          )}
          <button
            onClick={() => setDark(d => !d)}
            title={dark ? 'Switch to light mode' : 'Switch to dark mode'}
            className="text-sm text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors px-1"
          >
            {dark ? 'Light' : 'Dark'}
          </button>
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
