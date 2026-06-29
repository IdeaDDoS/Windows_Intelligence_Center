import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'

import { api, type ProcessListResponse, type ServiceListResponse } from '../api/client'
import { useApp } from '../context/AppContext'
import { ProcessTable } from '../components/ProcessTable'
import { ServicesTable } from '../components/ServicesTable'
import { ProcessDetailModal } from '../components/ProcessDetailModal'

export function ProcessesPage() {
  const { t } = useApp()
  const [selectedPid, setSelectedPid] = useState<number | null>(null)

  const procs = useQuery<ProcessListResponse>({
    queryKey: ['processes'],
    queryFn: () => api.processes(15),
    refetchInterval: 3000,
  })

  const svcs = useQuery<ServiceListResponse>({
    queryKey: ['services'],
    queryFn: api.services,
  })

  return (
    <div className="stack">
      <section>
        <h2>{t.processes}</h2>
        {procs.isError && <p className="status status--offline">{t.loadError}</p>}
        {!procs.data && !procs.isError && <p className="muted">{t.loading}</p>}
        {procs.data?.meta.partial && (
          <p className="warn">{t.partialWarning}</p>
        )}
        {procs.data && (
          <ProcessTable processes={procs.data.processes} onSelect={setSelectedPid} />
        )}
      </section>

      <section>
        <h2>{t.services}</h2>
        {svcs.isError && <p className="status status--offline">{t.loadError}</p>}
        {!svcs.data && !svcs.isError && <p className="muted">{t.loading}</p>}
        {svcs.data?.meta.partial && <p className="warn">{t.partialWarning}</p>}
        {svcs.data && <ServicesTable services={svcs.data.services} />}
      </section>

      {selectedPid !== null && (
        <ProcessDetailModal pid={selectedPid} onClose={() => setSelectedPid(null)} />
      )}
    </div>
  )
}
