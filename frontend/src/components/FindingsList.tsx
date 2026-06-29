import { type FindingItem } from '../api/client'
import { useApp } from '../context/AppContext'

const SEVERITY_CLASS: Record<string, string> = {
  critical: 'sev sev--critical',
  high: 'sev sev--high',
  medium: 'sev sev--medium',
  low: 'sev sev--low',
  info: 'sev sev--info',
}

interface FindingsListProps {
  findings: FindingItem[]
}

export function FindingsList({ findings }: FindingsListProps) {
  const { t } = useApp()
  if (findings.length === 0) {
    return <p className="muted">{t.noFindings}</p>
  }
  return (
    <ul className="findings">
      {findings.map((f) => (
        <li key={f.id} className="finding" data-testid="finding">
          <div className="finding__head">
            <span className={SEVERITY_CLASS[f.severity] ?? 'sev'}>{f.severity}</span>
            <strong>{f.title}</strong>
          </div>
          <p className="finding__desc">{f.description}</p>
          {f.recommendation && (
            <p className="finding__rec">
              <em>{t.recommendation}:</em> {f.recommendation}
            </p>
          )}
        </li>
      ))}
    </ul>
  )
}
