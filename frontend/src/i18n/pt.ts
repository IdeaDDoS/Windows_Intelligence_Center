// Strings da interface em português (idioma padrão do produto).

export const pt = {
  appName: 'Windows Intelligence Center',
  checking: 'verificando…',
  loading: 'carregando…',
  empty: 'nada para mostrar',
  close: 'fechar',
  // Navegação
  navDashboard: 'Painel',
  navProcesses: 'Processos',
  navHistory: 'Histórico',
  navAlerts: 'Alertas',
  // Métricas (Fatia 1)
  cpu: 'CPU',
  memory: 'Memória',
  disk: 'Disco',
  network: 'Rede',
  uptime: 'Uptime',
  metricsError: 'Não foi possível ler as métricas (backend offline?)',
  // Processos e serviços (Fatia 2)
  processes: 'Processos',
  services: 'Serviços',
  colPid: 'PID',
  colName: 'Nome',
  colCpu: 'CPU %',
  colMemory: 'Memória (MB)',
  colUser: 'Usuário',
  colStatus: 'Estado',
  colStartType: 'Inicialização',
  colDisplayName: 'Serviço',
  processDetail: 'Detalhe do processo',
  signature: 'Assinatura digital',
  signed: 'Assinado',
  notSigned: 'Não assinado',
  signer: 'Assinante',
  executable: 'Executável',
  partialWarning: 'Coleta parcial — rode como administrador para dados completos.',
  loadError: 'Falha ao carregar os dados.',
  // Histórico (Fatia 3)
  history: 'Histórico de métricas',
  range1h: '1h',
  range6h: '6h',
  range24h: '24h',
  noHistory: 'Sem amostras ainda — o coletor grava em segundo plano.',
  // Alertas (Fatia 4)
  alerts: 'Alertas',
  alertRules: 'Regras de alerta',
  noAlerts: 'Nenhum alerta.',
  acknowledge: 'Reconhecer',
  acknowledged: 'reconhecido',
  metric: 'Métrica',
  operator: 'Operador',
  threshold: 'Limiar',
  durationS: 'Duração (s)',
  enabled: 'Ativa',
} as const

export type Strings = typeof pt
