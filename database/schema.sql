-- DDL versionado do Windows Intelligence Center (fonte canônica do schema).
--
-- Fatia 0: apenas a infraestrutura de versionamento de schema. As tabelas de
-- domínio (metric_samples, process_samples, events, audits, findings,
-- explanations — ver PLANEJAMENTO.md §5) entram nas fatias respectivas.

CREATE TABLE IF NOT EXISTS schema_meta (
    version    INTEGER NOT NULL,
    applied_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Fatia 3: série temporal de métricas do sistema, gravada pelo sampler.
-- `ts` em ISO-8601 UTC; `net_sent`/`net_recv` guardam o acumulado do psutil
-- (a taxa/delta é derivada na borda). Retenção: raw por 7 dias (expurgo no sampler).
CREATE TABLE IF NOT EXISTS metric_samples (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT    NOT NULL,
    cpu_pct     REAL    NOT NULL,
    mem_pct     REAL    NOT NULL,
    mem_used_gb REAL    NOT NULL,
    disk_pct    REAL    NOT NULL,
    net_sent    INTEGER NOT NULL,
    net_recv    INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_metric_samples_ts ON metric_samples (ts);
