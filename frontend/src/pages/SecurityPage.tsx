import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  api,
  type AuditDetailResponse,
  type AuditRunResponse,
  type SecurityConfigPayload,
} from '../api/client'
import { useApp } from '../context/AppContext'
import { FindingsList } from '../components/FindingsList'

function scoreBand(score: number): 'good' | 'warn' | 'bad' {
  if (score >= 80) return 'good'
  if (score >= 50) return 'warn'
  return 'bad'
}

export function SecurityPage() {
  const { t } = useApp()
  const queryClient = useQueryClient()
  const [detail, setDetail] = useState<AuditRunResponse | null>(null)

  const onOffUnknown = (value: boolean | null): string =>
    value === null ? t.unknown : value ? t.on : t.off

  const latest = useQuery<AuditDetailResponse>({
    queryKey: ['audit-latest'],
    queryFn: api.auditLatest,
  })

  const run = useMutation({
    mutationFn: api.runAudit,
    onSuccess: (res) => {
      setDetail(res)
      queryClient.invalidateQueries({ queryKey: ['audit-latest'] })
    },
  })

  const score = detail?.score ?? latest.data?.audit?.score ?? null
  const findings = detail?.findings ?? latest.data?.findings ?? []
  const security: SecurityConfigPayload | null = detail?.security ?? null

  return (
    <div className="stack">
      <section>
        <div className="security-head">
          <h2>{t.security}</h2>
          <button type="button" onClick={() => run.mutate()} disabled={run.isPending}>
            {run.isPending ? t.running : t.runAudit}
          </button>
        </div>

        {run.isError && <p className="status status--offline">{t.loadError}</p>}
        {detail?.partial && <p className="warn">{t.auditPartial}</p>}
        {score === null && !run.isPending && <p className="muted">{t.noAudit}</p>}
        {score !== null && (
          <div className={`score score--${scoreBand(score)}`}>
            <span className="score__value">{score}</span>
            <span className="score__max">/100</span>
          </div>
        )}
      </section>

      {score !== null && (
        <section>
          <h2>{t.findings}</h2>
          <FindingsList findings={findings} />
        </section>
      )}

      {security && (
        <section>
          <h2>{t.security}</h2>
          <dl className="detail">
            <dt>{t.firewall}</dt>
            <dd>
              {Object.entries(security.firewall).map(([profile, enabled]) => (
                <span key={profile} className={`badge ${enabled ? 'badge--ok' : 'badge--warn'}`}>
                  {profile}: {enabled ? t.on : t.off}
                </span>
              ))}
            </dd>
            <dt>{t.defender}</dt>
            <dd>
              {t.on}/{t.off}: {onOffUnknown(security.defender.antivirus_enabled)} ·{' '}
              {onOffUnknown(security.defender.realtime_enabled)}
            </dd>
            <dt>{t.thirdPartyAv}</dt>
            <dd>{security.antivirus.length ? security.antivirus.join(', ') : '—'}</dd>
            <dt>{t.lastHotfix}</dt>
            <dd>{security.last_hotfix ?? '—'}</dd>
          </dl>
        </section>
      )}

      {detail && detail.ports.length > 0 && (
        <section>
          <h2>{t.openPorts}</h2>
          <table className="table">
            <thead>
              <tr>
                <th>{t.colPort}</th>
                <th>{t.colProtocol}</th>
                <th>{t.colAddress}</th>
                <th>{t.colProcess}</th>
              </tr>
            </thead>
            <tbody>
              {detail.ports.map((p) => (
                <tr key={`${p.protocol}-${p.port}-${p.address}`}>
                  <td>
                    {p.port}
                    {p.public && <span className="badge badge--warn"> {t.exposed}</span>}
                  </td>
                  <td>{p.protocol}</td>
                  <td>{p.address}</td>
                  <td>{p.process ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  )
}
