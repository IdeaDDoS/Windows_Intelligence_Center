import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'

import { ProcessTable } from './ProcessTable'
import { AppProvider } from '../context/AppContext'
import { type ProcessItem } from '../api/client'

const mockProcesses: ProcessItem[] = [
  { pid: 100, name: 'chrome.exe', cpu_pct: 12.5, rss_mb: 512.3, username: 'user', exe: 'C:/chrome.exe' },
  { pid: 200, name: 'code.exe', cpu_pct: 3.2, rss_mb: 256.1, username: 'user', exe: null },
]

function renderTable(onSelect = vi.fn()) {
  render(
    <AppProvider>
      <ProcessTable processes={mockProcesses} onSelect={onSelect} />
    </AppProvider>,
  )
  return onSelect
}

describe('ProcessTable', () => {
  it('renderiza uma linha por processo', () => {
    renderTable()
    expect(screen.getByText('chrome.exe')).toBeInTheDocument()
    expect(screen.getByText('code.exe')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
    expect(screen.getByText('12.5')).toBeInTheDocument()
  })

  it('chama onSelect com o pid ao clicar na linha', () => {
    const onSelect = renderTable()
    fireEvent.click(screen.getByText('chrome.exe'))
    expect(onSelect).toHaveBeenCalledWith(100)
  })
})
