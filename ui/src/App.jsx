import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { UserProvider, useUser } from './UserContext'
import NameModal from './components/NameModal'
import ActivityWall from './pages/ActivityWall'

function AppShell() {
  const { user, ready } = useUser()

  if (!ready) return null

  return (
    <>
      {!user && <NameModal />}
      {user && (
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<ActivityWall />} />
          </Routes>
        </BrowserRouter>
      )}
    </>
  )
}

export default function App() {
  return (
    <UserProvider>
      <AppShell />
    </UserProvider>
  )
}
