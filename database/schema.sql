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

-- Fatia 4: regras de alerta configuráveis e alertas disparados.
CREATE TABLE IF NOT EXISTS alert_rules (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    metric     TEXT    NOT NULL,   -- cpu_pct | mem_pct | disk_pct
    operator   TEXT    NOT NULL,   -- > | >= | < | <=
    threshold  REAL    NOT NULL,
    duration_s INTEGER NOT NULL DEFAULT 0,
    enabled    INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS alerts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id      INTEGER NOT NULL REFERENCES alert_rules (id),
    ts           TEXT    NOT NULL,
    value        REAL    NOT NULL,
    message      TEXT    NOT NULL,
    acknowledged INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_alerts_ts ON alerts (ts);

-- Seed das regras default — só quando a tabela está vazia (idempotente).
INSERT INTO alert_rules (metric, operator, threshold, duration_s, enabled)
SELECT metric, operator, threshold, duration_s, 1
FROM (
    SELECT 'cpu_pct' AS metric, '>' AS operator, 90.0 AS threshold, 60 AS duration_s
    UNION ALL SELECT 'mem_pct', '>', 90.0, 60
    UNION ALL SELECT 'disk_pct', '>', 90.0, 0
)
WHERE NOT EXISTS (SELECT 1 FROM alert_rules);
