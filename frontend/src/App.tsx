import { KPIStrip } from './components/KPIStrip'
import { useApp } from './context/AppContext'

export function App() {
  const { t } = useApp()
  return (
    <main className="app">
      <h1>{t.appName}</h1>
      <KPIStrip />
    </main>
  )
}
