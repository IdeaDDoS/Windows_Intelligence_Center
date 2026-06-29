import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

import { FindingsList } from './FindingsList'
import { AppProvider } from '../context/AppContext'
import { type FindingItem } from '../api/client'

const mockFindings: FindingItem[] = [
  {
    id: 'PORT-3389-PUBLIC',
    title: 'Porta de risco 3389/TCP exposta na rede',
    severity: 'high',
    category: 'ports',
    description: 'RDP exposto.',
    recommendation: 'Restrinja ao localhost.',
    evidence: { port: 3389 },
  },
  {
    id: 'FW-Domain',
    title: 'Firewall do perfil Domain desativado',
    severity: 'high',
    category: 'firewall',
    description: 'Firewall desligado.',
    recommendation: 'Ative o firewall.',
    evidence: {},
  },
]

describe('FindingsList', () => {
  it('renderiza um item por achado com severidade e recomendação', () => {
    render(
      <AppProvider>
        <FindingsList findings={mockFindings} />
      </AppProvider>,
    )
    expect(screen.getAllByTestId('finding')).toHaveLength(2)
    expect(screen.getByText('Porta de risco 3389/TCP exposta na rede')).toBeInTheDocument()
    expect(screen.getByText('Restrinja ao localhost.')).toBeInTheDocument()
  })

  it('mostra estado limpo quando não há achados', () => {
    render(
      <AppProvider>
        <FindingsList findings={[]} />
      </AppProvider>,
    )
    expect(screen.queryByTestId('finding')).not.toBeInTheDocument()
  })
})
