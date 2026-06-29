import { useQuery } from '@tanstack/react-query'

import { api, type AlertListResponse, type AlertRuleListResponse } from '../api/client'
import { useApp } from '../context/AppContext'
import { AlertsList } from '../components/AlertsList'
import { AlertRulesTable } from '../components/AlertRulesTable'

export function AlertsPage() {
  const { t } = useApp()

  const alerts = useQuery<AlertListResponse>({
    queryKey: ['alerts'],
    queryFn: api.alerts,
    refetchInterval: 5000,
  })

  const rules = useQuery<AlertRuleListResponse>({
    queryKey: ['alert-rules'],
    queryFn: api.alertRules,
  })

  return (
    <div className="stack">
      <section>
        <h2>{t.alerts}</h2>
        {alerts.isError && <p className="status status--offline">{t.loadError}</p>}
        {!alerts.data && !alerts.isError && <p className="muted">{t.loading}</p>}
        {alerts.data && <AlertsList alerts={alerts.data.alerts} />}
      </section>

      <section>
        <h2>{t.alertRules}</h2>
        {rules.isError && <p className="status status--offline">{t.loadError}</p>}
        {!rules.data && !rules.isError && <p className="muted">{t.loading}</p>}
        {rules.data && <AlertRulesTable rules={rules.data.rules} />}
      </section>
    </div>
  )
}
