import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

import { MetricsChart } from './MetricsChart'
import { AppProvider } from '../context/AppContext'
import { type HistoryPoint } from '../api/client'

const mockPoints: HistoryPoint[] = [
  { ts: '2026-06-28T00:00:00Z', cpu_pct: 10, mem_pct: 40, disk_pct: 55, net_sent: 1, net_recv: 2 },
  { ts: '2026-06-28T00:00:05Z', cpu_pct: 20, mem_pct: 42, disk_pct: 55, net_sent: 3, net_recv: 4 },
  { ts: '2026-06-28T00:00:10Z', cpu_pct: 15, mem_pct: 41, disk_pct: 56, net_sent: 5, net_recv: 6 },
]

function renderChart(points: HistoryPoint[]) {
  return render(
    <AppProvider>
      <MetricsChart points={points} />
    </AppProvider>,
  )
}

describe('MetricsChart', () => {
  it('renderiza o gráfico com a quantidade de pontos da série', () => {
    renderChart(mockPoints)
    expect(screen.getByTestId('metrics-chart')).toBeInTheDocument()
    expect(screen.getByTestId('chart-points').textContent).toBe('3')
  })

  it('mostra estado vazio quando não há pontos', () => {
    renderChart([])
    expect(screen.queryByTestId('metrics-chart')).not.toBeInTheDocument()
  })
})
