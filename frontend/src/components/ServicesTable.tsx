import { type ServiceItem } from '../api/client'
import { useApp } from '../context/AppContext'

interface ServicesTableProps {
  services: ServiceItem[]
}

export function ServicesTable({ services }: ServicesTableProps) {
  const { t } = useApp()
  return (
    <table className="table">
      <thead>
        <tr>
          <th>{t.colDisplayName}</th>
          <th>{t.colStatus}</th>
          <th>{t.colStartType}</th>
        </tr>
      </thead>
      <tbody>
        {services.map((s) => (
          <tr key={s.name}>
            <td>{s.display_name || s.name}</td>
            <td>
              <span className={`badge badge--${s.status}`}>{s.status}</span>
            </td>
            <td>{s.start_type}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
