import { NavLink, Route, Routes } from 'react-router-dom'

import { useApp } from './context/AppContext'
import { DashboardPage } from './pages/DashboardPage'
import { ProcessesPage } from './pages/ProcessesPage'

export function App() {
  const { t } = useApp()
  return (
    <div className="app">
      <header className="topbar">
        <h1>{t.appName}</h1>
        <nav className="nav">
          <NavLink to="/" end>
            {t.navDashboard}
          </NavLink>
          <NavLink to="/processes">{t.navProcesses}</NavLink>
        </nav>
      </header>
      <main className="content">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/processes" element={<ProcessesPage />} />
        </Routes>
      </main>
    </div>
  )
}
