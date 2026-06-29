// Strings da interface em português (idioma padrão do produto).

export const pt = {
  appName: 'Windows Intelligence Center',
  checking: 'verificando…',
  // Métricas (Fatia 1)
  cpu: 'CPU',
  memory: 'Memória',
  disk: 'Disco',
  network: 'Rede',
  uptime: 'Uptime',
  metricsError: 'Não foi possível ler as métricas (backend offline?)',
} as const

export type Strings = typeof pt
