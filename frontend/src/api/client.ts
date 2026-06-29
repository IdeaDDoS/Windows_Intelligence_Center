// Cliente HTTP tipado do backend. Os tipos espelham os payloads Pydantic do
// backend (uma fonte canônica, múltiplos destinos): mudou o contrato lá,
// atualize aqui.

export interface HealthResponse {
  status: string
  version: string
  platform: string
  is_admin: boolean
}

export interface MetricsPayload {
  cpu_pct: number
  mem_pct: number
  mem_used_gb: number
  mem_total_gb: number
  disk_pct: number
  disk_used_gb: number
  disk_total_gb: number
  net_sent: number
  net_recv: number
  uptime_seconds: number
}

export interface HostPayload {
  hostname: string
  os: string
  boot_time: string
}

export interface MetaPayload {
  source: string
  partial: boolean
  reason: string | null
  collected_at: string
  duration_ms: number
}

export interface MetricsLiveResponse {
  metrics: MetricsPayload
  host: HostPayload
  meta: MetaPayload
}

// ── Processos e serviços (Fatia 2) ───────────────────────────────────────────

export interface ProcessItem {
  pid: number
  name: string
  cpu_pct: number
  rss_mb: number
  username: string
  exe: string | null
}

export interface ProcessListResponse {
  processes: ProcessItem[]
  meta: MetaPayload
}

export interface SignaturePayload {
  is_signed: boolean
  status: string
  signer: string | null
}

export interface ProcessDetailResponse {
  process: ProcessItem
  signature: SignaturePayload
}

export interface ServiceItem {
  name: string
  display_name: string
  status: string
  start_type: string
}

export interface ServiceListResponse {
  services: ServiceItem[]
  meta: MetaPayload
}

// ── Histórico de métricas (Fatia 3) ──────────────────────────────────────────

export type HistoryRange = '1h' | '6h' | '24h'

export interface HistoryPoint {
  ts: string
  cpu_pct: number
  mem_pct: number
  disk_pct: number
  net_sent: number
  net_recv: number
}

export interface MetricsHistoryResponse {
  range: string
  points: HistoryPoint[]
}

// ── Alertas (Fatia 4) ────────────────────────────────────────────────────────

export type AlertMetric = 'cpu_pct' | 'mem_pct' | 'disk_pct'
export type AlertOperator = '>' | '>=' | '<' | '<='

export interface AlertItem {
  id: number
  rule_id: number
  ts: string
  value: number
  message: string
  acknowledged: boolean
}

export interface AlertListResponse {
  alerts: AlertItem[]
}

export interface AlertRule {
  id: number
  metric: string
  operator: string
  threshold: number
  duration_s: number
  enabled: boolean
}

export interface AlertRuleListResponse {
  rules: AlertRule[]
}

export interface AlertRuleInput {
  metric: AlertMetric
  operator: AlertOperator
  threshold: number
  duration_s: number
  enabled: boolean
}

export type AlertRulePatch = Partial<AlertRuleInput>

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(path, { headers: { Accept: 'application/json' } })
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} em ${path}`)
  }
  return (await res.json()) as T
}

async function sendJson<T>(
  path: string,
  method: 'POST' | 'PUT',
  body?: unknown,
): Promise<T> {
  const res = await fetch(path, {
    method,
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} em ${path}`)
  }
  return (await res.json()) as T
}

export const api = {
  health: () => getJson<HealthResponse>('/api/health'),
  metricsLive: () => getJson<MetricsLiveResponse>('/api/metrics/live'),
  processes: (topN = 15) => getJson<ProcessListResponse>(`/api/processes?top_n=${topN}`),
  processDetail: (pid: number) => getJson<ProcessDetailResponse>(`/api/processes/${pid}`),
  services: () => getJson<ServiceListResponse>('/api/services'),
  metricsHistory: (range: HistoryRange) =>
    getJson<MetricsHistoryResponse>(`/api/metrics/history?range=${range}`),
  alerts: () => getJson<AlertListResponse>('/api/alerts'),
  alertRules: () => getJson<AlertRuleListResponse>('/api/alert_rules'),
  ackAlert: (id: number) => sendJson<AlertItem>(`/api/alerts/${id}/ack`, 'POST'),
  createRule: (input: AlertRuleInput) =>
    sendJson<AlertRule>('/api/alert_rules', 'POST', input),
  updateRule: (id: number, patch: AlertRulePatch) =>
    sendJson<AlertRule>(`/api/alert_rules/${id}`, 'PUT', patch),
}
