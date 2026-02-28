import { UserProvider, useUser } from './UserContext'
import NameModal from './components/NameModal'

function AppShell() {
  const { user, ready } = useUser()

  if (!ready) return null

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      {!user && <NameModal />}
      {user && (
        <div className="max-w-4xl mx-auto px-4 py-8">
          <p className="text-gray-500 text-sm">Logged in as {user.name}</p>
        </div>
      )}
    </div>
  )
}

export default function App() {
  return (
    <UserProvider>
      <AppShell />
    </UserProvider>
  )
}
