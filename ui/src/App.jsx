import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { UserProvider, useUser } from './UserContext'
import NameModal from './components/NameModal'
import ActivityWall from './pages/ActivityWall'
import RunDetail from './pages/RunDetail'
import Compare from './pages/Compare'

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
            <Route path="/compare/:id1/:id2" element={<Compare />} />
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
