import { type ProcessItem } from '../api/client'
import { useApp } from '../context/AppContext'

interface ProcessTableProps {
  processes: ProcessItem[]
  onSelect: (pid: number) => void
}

export function ProcessTable({ processes, onSelect }: ProcessTableProps) {
  const { t } = useApp()
  return (
    <table className="table">
      <thead>
        <tr>
          <th>{t.colPid}</th>
          <th>{t.colName}</th>
          <th>{t.colCpu}</th>
          <th>{t.colMemory}</th>
          <th>{t.colUser}</th>
        </tr>
      </thead>
      <tbody>
        {processes.map((p) => (
          <tr key={p.pid} className="table__row" onClick={() => onSelect(p.pid)}>
            <td>{p.pid}</td>
            <td>{p.name}</td>
            <td>{p.cpu_pct.toFixed(1)}</td>
            <td>{p.rss_mb.toFixed(1)}</td>
            <td>{p.username}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
