import { useMutation, useQueryClient } from '@tanstack/react-query'

import { api, type AlertRule, type AlertRulePatch } from '../api/client'
import { useApp } from '../context/AppContext'

interface AlertRulesTableProps {
  rules: AlertRule[]
}

export function AlertRulesTable({ rules }: AlertRulesTableProps) {
  const { t } = useApp()
  const queryClient = useQueryClient()

  const update = useMutation({
    mutationFn: ({ id, patch }: { id: number; patch: AlertRulePatch }) =>
      api.updateRule(id, patch),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alert-rules'] }),
  })

  return (
    <table className="table">
      <thead>
        <tr>
          <th>{t.metric}</th>
          <th>{t.operator}</th>
          <th>{t.threshold}</th>
          <th>{t.durationS}</th>
          <th>{t.enabled}</th>
        </tr>
      </thead>
      <tbody>
        {rules.map((r) => (
          <tr key={r.id}>
            <td>{r.metric}</td>
            <td>{r.operator}</td>
            <td>
              <input
                type="number"
                defaultValue={r.threshold}
                onBlur={(e) => {
                  const threshold = Number(e.target.value)
                  if (threshold !== r.threshold) {
                    update.mutate({ id: r.id, patch: { threshold } })
                  }
                }}
              />
            </td>
            <td>{r.duration_s}</td>
            <td>
              <input
                type="checkbox"
                checked={r.enabled}
                onChange={(e) =>
                  update.mutate({ id: r.id, patch: { enabled: e.target.checked } })
                }
              />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
