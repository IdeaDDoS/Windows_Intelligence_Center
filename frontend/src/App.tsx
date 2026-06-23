import { useEffect, useState } from 'react'

import { api, type HealthResponse } from './api/client'
import { useApp } from './context/AppContext'

type Status = 'checking' | 'online' | 'offline'

export function App() {
  const { t } = useApp()
  const [status, setStatus] = useState<Status>('checking')
  const [health, setHealth] = useState<HealthResponse | null>(null)

  useEffect(() => {
    let active = true
    api
      .health()
      .then((data) => {
        if (!active) return
        setHealth(data)
        setStatus('online')
      })
      .catch(() => {
        if (active) setStatus('offline')
      })
    return () => {
      active = false
    }
  }, [])

  const label =
    status === 'online' ? t.online : status === 'offline' ? t.offline : t.checking

  return (
    <main className="app">
      <h1>{t.appName}</h1>
      <section className="card">
        <div className={`status status--${status}`}>
          <span className="dot" />
          {t.backendStatus}: <strong>{label}</strong>
        </div>
        {health && (
          <dl className="meta">
            <dt>{t.version}</dt>
            <dd>{health.version}</dd>
            <dt>{t.platform}</dt>
            <dd>{health.platform}</dd>
            <dt>{t.privilege}</dt>
            <dd>{health.is_admin ? t.admin : t.standardUser}</dd>
          </dl>
        )}
      </section>
    </main>
  )
}
