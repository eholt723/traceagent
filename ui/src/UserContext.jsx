import { createContext, useContext, useState, useEffect } from 'react'
import { api } from './api'

const UserContext = createContext(null)

function generateUuid() {
  if (typeof crypto.randomUUID === 'function') return crypto.randomUUID()
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16)
  })
}

export function UserProvider({ children }) {
  const [user, setUser] = useState(null)   // null = not loaded yet
  const [ready, setReady] = useState(false) // false until localStorage checked

  useEffect(() => {
    const stored = localStorage.getItem('traceagent_user')
    if (stored) {
      setUser(JSON.parse(stored))
    }
    setReady(true)
  }, [])

  async function identify(name) {
    const uuid = generateUuid()
    const saved = await api.upsertUser(uuid, name)
    const identity = { uuid, name: saved.name, id: saved.id }
    localStorage.setItem('traceagent_user', JSON.stringify(identity))
    setUser(identity)
  }

  return (
    <UserContext.Provider value={{ user, ready, identify }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  return useContext(UserContext)
}
