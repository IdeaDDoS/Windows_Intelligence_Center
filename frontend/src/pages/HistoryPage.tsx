import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'

import { api, type HistoryRange, type MetricsHistoryResponse } from '../api/client'
import { useApp } from '../context/AppContext'
import { MetricsChart } from '../components/MetricsChart'

const RANGES: HistoryRange[] = ['1h', '6h', '24h']

export function HistoryPage() {
  const { t } = useApp()
  const [range, setRange] = useState<HistoryRange>('1h')

  const { data, isError } = useQuery<MetricsHistoryResponse>({
    queryKey: ['metrics-history', range],
    queryFn: () => api.metricsHistory(range),
    refetchInterval: 10000,
  })

  return (
    <div className="stack">
      <section>
        <h2>{t.history}</h2>
        <div className="range-picker">
          {RANGES.map((r) => (
            <button
              key={r}
              type="button"
              className={r === range ? 'active' : ''}
              onClick={() => setRange(r)}
            >
              {r}
            </button>
          ))}
        </div>
        {isError && <p className="status status--offline">{t.loadError}</p>}
        {!data && !isError && <p className="muted">{t.loading}</p>}
        {data && <MetricsChart points={data.points} />}
      </section>
    </div>
  )
}
