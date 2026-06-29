import { useState } from 'react'
import { useQuery, keepPreviousData } from '@tanstack/react-query'

import {
  api,
  type EventLevel,
  type EventListResponse,
  type EventLog,
  type EventSince,
} from '../api/client'
import { useApp } from '../context/AppContext'
import { EventsTable } from '../components/EventsTable'

const LOGS: EventLog[] = ['System', 'Application', 'Security']
const SINCES: EventSince[] = ['1h', '6h', '24h', '7d']

export function EventsPage() {
  const { t } = useApp()
  const [log, setLog] = useState<EventLog>('System')
  const [level, setLevel] = useState<EventLevel>('all')
  const [since, setSince] = useState<EventSince>('24h')

  const levelLabels: Record<EventLevel, string> = {
    all: t.levelAll,
    critical: t.levelCritical,
    error: t.levelError,
    warning: t.levelWarning,
    information: t.levelInformation,
  }

  const { data, isError, isFetching } = useQuery<EventListResponse>({
    queryKey: ['events', log, level, since],
    queryFn: () => api.events({ log, level, since }),
    placeholderData: keepPreviousData,
  })

  return (
    <div className="stack">
      <section>
        <h2>{t.events}</h2>

        <div className="filters">
          <label className="field">
            <span>{t.eventLog}</span>
            <select value={log} onChange={(e) => setLog(e.target.value as EventLog)}>
              {LOGS.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>{t.eventLevel}</span>
            <select value={level} onChange={(e) => setLevel(e.target.value as EventLevel)}>
              {(Object.keys(levelLabels) as EventLevel[]).map((lv) => (
                <option key={lv} value={lv}>
                  {levelLabels[lv]}
                </option>
              ))}
            </select>
          </label>

          <label className="field">
            <span>{t.eventSince}</span>
            <select value={since} onChange={(e) => setSince(e.target.value as EventSince)}>
              {SINCES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
        </div>

        {isError && <p className="status status--offline">{t.loadError}</p>}
        {data?.meta.partial && <p className="warn">{t.eventsPartial}</p>}
        {!data && !isError && <p className="muted">{t.loading}</p>}
        {data && data.events.length === 0 && !isFetching && (
          <p className="muted">{t.noEvents}</p>
        )}
        {data && data.events.length > 0 && <EventsTable events={data.events} />}
      </section>
    </div>
  )
}
