import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import { KPIStrip } from './KPIStrip'
import { AppProvider } from '../context/AppContext'
import { api, type MetricsLiveResponse } from '../api/client'

const mockResponse: MetricsLiveResponse = {
  metrics: {
    cpu_pct: 12,
    mem_pct: 40,
    mem_used_gb: 6.4,
    mem_total_gb: 16,
    disk_pct: 55,
    disk_used_gb: 250,
    disk_total_gb: 500,
    net_sent: 1024,
    net_recv: 2048,
    uptime_seconds: 3661,
  },
  host: { hostname: 'TEST-PC', os: 'Windows 11', boot_time: '2026-06-23T00:00:00Z' },
  meta: {
    source: 'system',
    partial: false,
    reason: null,
    collected_at: '2026-06-23T12:00:00Z',
    duration_ms: 3,
  },
}

function renderStrip() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AppProvider>
        <KPIStrip />
      </AppProvider>
    </QueryClientProvider>,
  )
}

describe('KPIStrip', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('renderiza host e os 4 KPIs com dados do backend', async () => {
    vi.spyOn(api, 'metricsLive').mockResolvedValue(mockResponse)
    renderStrip()
    await waitFor(() => expect(screen.getByText('TEST-PC')).toBeInTheDocument())
    expect(screen.getByText('CPU')).toBeInTheDocument()
    expect(screen.getByText('Memória')).toBeInTheDocument()
    expect(screen.getByText('Disco')).toBeInTheDocument()
    expect(screen.getByText('Rede')).toBeInTheDocument()
    expect(screen.getByText('12%')).toBeInTheDocument()
  })
})
