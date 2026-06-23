-- DDL versionado do Windows Intelligence Center (fonte canônica do schema).
--
-- Fatia 0: apenas a infraestrutura de versionamento de schema. As tabelas de
-- domínio (metric_samples, process_samples, events, audits, findings,
-- explanations — ver PLANEJAMENTO.md §5) entram nas fatias respectivas.

CREATE TABLE IF NOT EXISTS schema_meta (
    version    INTEGER NOT NULL,
    applied_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
