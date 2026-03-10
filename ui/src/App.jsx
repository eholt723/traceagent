import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { UserProvider, useUser } from './UserContext'
import NameModal from './components/NameModal'
import About from './pages/About'
import ActivityWall from './pages/ActivityWall'
import Compare from './pages/Compare'
import Dashboard from './pages/Dashboard'
import RunDetail from './pages/RunDetail'

function AppShell() {
  const { user, ready } = useUser()

  if (!ready) return null

  return (
    <BrowserRouter>
      {!user && <NameModal />}
      <Routes>
        <Route path="/about" element={<About />} />
        <Route path="/" element={<ActivityWall />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/runs/:id" element={<RunDetail />} />
        <Route path="/compare/:id1/:id2" element={<Compare />} />
      </Routes>
      <div className="fixed bottom-3 right-4 text-right text-xs pointer-events-none select-none">
        <p className="text-gray-400 dark:text-gray-600">Created by</p>
        <p className="font-medium text-gray-500 dark:text-gray-500">Eric Holt</p>
      </div>
    </BrowserRouter>
  )
}

export default function App() {
  return (
    <UserProvider>
      <AppShell />
    </UserProvider>
  )
}
