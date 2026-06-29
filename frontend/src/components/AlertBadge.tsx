import { useQuery } from '@tanstack/react-query'

import { api, type AlertListResponse } from '../api/client'

export function AlertBadge() {
  const { data } = useQuery<AlertListResponse>({
    queryKey: ['alerts'],
    queryFn: api.alerts,
    refetchInterval: 5000,
  })

  const count = data?.alerts.filter((a) => !a.acknowledged).length ?? 0
  if (count === 0) {
    return null
  }
  return (
    <span className="alert-badge" data-testid="alert-badge">
      {count}
    </span>
  )
}
