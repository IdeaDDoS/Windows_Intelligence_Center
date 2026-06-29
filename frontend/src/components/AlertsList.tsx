import { useMutation, useQueryClient } from '@tanstack/react-query'

import { api, type AlertItem } from '../api/client'
import { useApp } from '../context/AppContext'

interface AlertsListProps {
  alerts: AlertItem[]
}

export function AlertsList({ alerts }: AlertsListProps) {
  const { t } = useApp()
  const queryClient = useQueryClient()

  const ack = useMutation({
    mutationFn: (id: number) => api.ackAlert(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  })

  if (alerts.length === 0) {
    return <p className="muted">{t.noAlerts}</p>
  }

  return (
    <div className="alerts-list">
      {alerts.map((a) => (
        <div
          key={a.id}
          className={`alert-item ${a.acknowledged ? 'alert-item--ack' : ''}`}
        >
          <span>
            {a.message}
            {a.acknowledged && <em> · {t.acknowledged}</em>}
          </span>
          {!a.acknowledged && (
            <button type="button" onClick={() => ack.mutate(a.id)} disabled={ack.isPending}>
              {t.acknowledge}
            </button>
          )}
        </div>
      ))}
    </div>
  )
}
