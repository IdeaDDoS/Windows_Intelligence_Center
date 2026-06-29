import { NavLink, Route, Routes } from 'react-router-dom'

import { useApp } from './context/AppContext'
import { AlertBadge } from './components/AlertBadge'
import { DashboardPage } from './pages/DashboardPage'
import { ProcessesPage } from './pages/ProcessesPage'
import { HistoryPage } from './pages/HistoryPage'
import { AlertsPage } from './pages/AlertsPage'
import { EventsPage } from './pages/EventsPage'

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
          <NavLink to="/history">{t.navHistory}</NavLink>
          <NavLink to="/events">{t.navEvents}</NavLink>
          <NavLink to="/alerts">
            {t.navAlerts}
            <AlertBadge />
          </NavLink>
        </nav>
      </header>
      <main className="content">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/processes" element={<ProcessesPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/events" element={<EventsPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
        </Routes>
      </main>
    </div>
  )
}
