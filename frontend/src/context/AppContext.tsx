import { createContext, useContext, type ReactNode } from 'react'

import { pt, type Strings } from '../i18n/pt'

type Theme = 'dark' | 'light'

interface AppContextValue {
  theme: Theme
  t: Strings
}

const AppContext = createContext<AppContextValue | null>(null)

export function AppProvider({ children }: { children: ReactNode }) {
  // Fatia 0: tema escuro fixo e idioma PT. A alternância de tema/idioma entra
  // em uma fatia futura.
  const value: AppContextValue = { theme: 'dark', t: pt }
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext)
  if (!ctx) {
    throw new Error('useApp deve ser usado dentro de <AppProvider>')
  }
  return ctx
}
