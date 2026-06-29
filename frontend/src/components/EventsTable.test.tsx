import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

import { EventsTable } from './EventsTable'
import { AppProvider } from '../context/AppContext'
import { type EventItem } from '../api/client'

const mockEvents: EventItem[] = [
  {
    ts: '2026-06-29T12:00:00Z',
    log: 'System',
    provider: 'Service Control Manager',
    event_id: 7000,
    level: 'Error',
    message: 'O serviço Foo falhou ao iniciar.',
  },
  {
    ts: '2026-06-29T11:00:00Z',
    log: 'System',
    provider: 'Kernel-Power',
    event_id: 41,
    level: 'Critical',
    message: 'O sistema reiniciou sem desligar corretamente.',
  },
]

describe('EventsTable', () => {
  it('renderiza uma linha por evento', () => {
    render(
      <AppProvider>
        <EventsTable events={mockEvents} />
      </AppProvider>,
    )
    expect(screen.getByText('7000')).toBeInTheDocument()
    expect(screen.getByText('Service Control Manager')).toBeInTheDocument()
    expect(screen.getByText('41')).toBeInTheDocument()
    expect(screen.getByText('O serviço Foo falhou ao iniciar.')).toBeInTheDocument()
  })
})
