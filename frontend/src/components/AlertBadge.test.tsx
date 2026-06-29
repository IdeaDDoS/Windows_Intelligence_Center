import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import { AlertBadge } from './AlertBadge'
import { api, type AlertListResponse } from '../api/client'

function renderBadge() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AlertBadge />
    </QueryClientProvider>,
  )
}

const withCounts = (unacked: number, acked: number): AlertListResponse => ({
  alerts: [
    ...Array.from({ length: unacked }, (_, i) => ({
      id: i + 1,
      rule_id: 1,
      ts: '2026-06-28T00:00:00Z',
      value: 95,
      message: 'cpu alto',
      acknowledged: false,
    })),
    ...Array.from({ length: acked }, (_, i) => ({
      id: 100 + i,
      rule_id: 1,
      ts: '2026-06-28T00:00:00Z',
      value: 95,
      message: 'cpu alto',
      acknowledged: true,
    })),
  ],
})

describe('AlertBadge', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('mostra a contagem de alertas não reconhecidos', async () => {
    vi.spyOn(api, 'alerts').mockResolvedValue(withCounts(2, 1))
    renderBadge()
    await waitFor(() => expect(screen.getByTestId('alert-badge')).toHaveTextContent('2'))
  })

  it('não renderiza nada quando não há alertas pendentes', async () => {
    vi.spyOn(api, 'alerts').mockResolvedValue(withCounts(0, 3))
    renderBadge()
    await waitFor(() => expect(api.alerts).toHaveBeenCalled())
    expect(screen.queryByTestId('alert-badge')).not.toBeInTheDocument()
  })
})
