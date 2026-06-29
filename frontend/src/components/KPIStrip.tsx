import { useQuery } from '@tanstack/react-query'

import { api, type MetricsLiveResponse } from '../api/client'
import { useApp } from '../context/AppContext'
import { formatBytes, formatUptime } from '../utils/format'

interface KpiCardProps {
  label: string
  value: string
  pct?: number
}

function KpiCard({ label, value, pct }: KpiCardProps) {
  return (
    <div className="kpi">
      <span className="kpi__label">{label}</span>
      <span className="kpi__value">{value}</span>
      {pct !== undefined && (
        <div className="kpi__bar">
          <div className="kpi__bar-fill" style={{ width: `${Math.min(pct, 100)}%` }} />
        </div>
      )}
    </div>
  )
}

export function KPIStrip() {
  const { t } = useApp()
  const { data, isError } = useQuery<MetricsLiveResponse>({
    queryKey: ['metrics-live'],
    queryFn: api.metricsLive,
    refetchInterval: 2000,
  })

  if (isError) {
    return <p className="status status--offline">{t.metricsError}</p>
  }
  if (!data) {
    return <p className="muted">{t.checking}</p>
  }

  const m = data.metrics
  return (
    <>
      <header className="host">
        <strong>{data.host.hostname}</strong> · {data.host.os} · {t.uptime}:{' '}
        {formatUptime(m.uptime_seconds)}
      </header>
      <section className="kpi-strip">
        <KpiCard label={t.cpu} value={`${m.cpu_pct.toFixed(0)}%`} pct={m.cpu_pct} />
        <KpiCard
          label={t.memory}
          value={`${m.mem_used_gb.toFixed(1)} / ${m.mem_total_gb.toFixed(1)} GB`}
          pct={m.mem_pct}
        />
        <KpiCard
          label={t.disk}
          value={`${m.disk_used_gb.toFixed(0)} / ${m.disk_total_gb.toFixed(0)} GB`}
          pct={m.disk_pct}
        />
        <KpiCard
          label={t.network}
          value={`↑ ${formatBytes(m.net_sent)}  ↓ ${formatBytes(m.net_recv)}`}
        />
      </section>
    </>
  )
}
