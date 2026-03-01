import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { UserProvider, useUser } from './UserContext'
import NameModal from './components/NameModal'
import ActivityWall from './pages/ActivityWall'
import RunDetail from './pages/RunDetail'

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
            <Route path="/runs/:id" element={<RunDetail />} />
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
