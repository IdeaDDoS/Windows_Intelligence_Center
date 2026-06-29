import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { type HistoryPoint } from '../api/client'
import { useApp } from '../context/AppContext'

interface MetricsChartProps {
  points: HistoryPoint[]
}

export function MetricsChart({ points }: MetricsChartProps) {
  const { t } = useApp()

  if (points.length === 0) {
    return <p className="muted">{t.noHistory}</p>
  }

  const data = points.map((p) => ({
    ...p,
    time: new Date(p.ts).toLocaleTimeString(),
  }))

  return (
    <figure className="chart" data-testid="metrics-chart">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: -16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
          <XAxis dataKey="time" tick={{ fontSize: 11 }} stroke="#8b949e" minTickGap={40} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} stroke="#8b949e" />
          <Tooltip
            contentStyle={{ background: '#161b22', border: '1px solid #30363d' }}
          />
          <Line type="monotone" dataKey="cpu_pct" name={t.cpu} stroke="#58a6ff" dot={false} />
          <Line type="monotone" dataKey="mem_pct" name={t.memory} stroke="#3fb950" dot={false} />
          <Line type="monotone" dataKey="disk_pct" name={t.disk} stroke="#d29922" dot={false} />
        </LineChart>
      </ResponsiveContainer>
      <figcaption className="sr-only" data-testid="chart-points">
        {points.length}
      </figcaption>
    </figure>
  )
}
