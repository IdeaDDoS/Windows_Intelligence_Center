// Cliente HTTP tipado do backend. Os tipos espelham os payloads Pydantic do
// backend (uma fonte canônica, múltiplos destinos): mudou o contrato lá,
// atualize aqui.

export interface HealthResponse {
  status: string
  version: string
  platform: string
  is_admin: boolean
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(path, { headers: { Accept: 'application/json' } })
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} em ${path}`)
  }
  return (await res.json()) as T
}

export const api = {
  health: () => getJson<HealthResponse>('/api/health'),
}
