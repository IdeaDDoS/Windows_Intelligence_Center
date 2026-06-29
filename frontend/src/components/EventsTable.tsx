import { type EventItem } from '../api/client'
import { useApp } from '../context/AppContext'

interface EventsTableProps {
  events: EventItem[]
}

// Mapeia o nível textual do Windows para a classe de badge.
function levelClass(level: string): string {
  const l = level.toLowerCase()
  if (l.includes('crit') || l.includes('error') || l.includes('erro')) return 'badge--warn'
  if (l.includes('warn') || l.includes('aviso')) return 'badge--warn'
  return 'badge'
}

export function EventsTable({ events }: EventsTableProps) {
  const { t } = useApp()
  return (
    <table className="table">
      <thead>
        <tr>
          <th>{t.colTime}</th>
          <th>{t.colLevel}</th>
          <th>{t.colSource}</th>
          <th>{t.colEventId}</th>
          <th>{t.colMessage}</th>
        </tr>
      </thead>
      <tbody>
        {events.map((e, i) => (
          <tr key={`${e.event_id}-${e.ts}-${i}`}>
            <td>{new Date(e.ts).toLocaleString()}</td>
            <td>
              <span className={`badge ${levelClass(e.level)}`}>{e.level}</span>
            </td>
            <td>{e.provider}</td>
            <td>{e.event_id}</td>
            <td className="event-message">{e.message}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
