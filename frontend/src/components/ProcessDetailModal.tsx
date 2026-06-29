import { useQuery } from '@tanstack/react-query'

import { api, type ProcessDetailResponse } from '../api/client'
import { useApp } from '../context/AppContext'

interface ProcessDetailModalProps {
  pid: number
  onClose: () => void
}

export function ProcessDetailModal({ pid, onClose }: ProcessDetailModalProps) {
  const { t } = useApp()
  const { data, isError, isLoading } = useQuery<ProcessDetailResponse>({
    queryKey: ['process-detail', pid],
    queryFn: () => api.processDetail(pid),
  })

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <header className="modal__header">
          <h2>{t.processDetail}</h2>
          <button type="button" onClick={onClose}>
            {t.close}
          </button>
        </header>

        {isLoading && <p className="muted">{t.loading}</p>}
        {isError && <p className="status status--offline">{t.loadError}</p>}

        {data && (
          <dl className="detail">
            <dt>{t.colPid}</dt>
            <dd>{data.process.pid}</dd>
            <dt>{t.colName}</dt>
            <dd>{data.process.name}</dd>
            <dt>{t.colUser}</dt>
            <dd>{data.process.username || '—'}</dd>
            <dt>{t.executable}</dt>
            <dd className="detail__path">{data.process.exe ?? '—'}</dd>
            <dt>{t.signature}</dt>
            <dd>
              <span
                className={`badge ${
                  data.signature.is_signed ? 'badge--ok' : 'badge--warn'
                }`}
              >
                {data.signature.is_signed ? t.signed : t.notSigned} ·{' '}
                {data.signature.status}
              </span>
            </dd>
            {data.signature.signer && (
              <>
                <dt>{t.signer}</dt>
                <dd>{data.signature.signer}</dd>
              </>
            )}
          </dl>
        )}
      </div>
    </div>
  )
}
