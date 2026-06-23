# Planejamento — Windows Intelligence Center

> Plano de desenvolvimento da plataforma local de observabilidade, diagnóstico e
> análise do Windows. Documento vivo — escopo e nomes mudam ao longo das iterações.

## Decisões travadas

| Decisão | Escolha | Data |
|---|---|---|
| Stack / UI | **FastAPI + React (Vite)** | 2026-06-21 |
| Armazenamento local | **SQLite** (via camada de repositório, trocável) | 2026-06-21 |
| Ponto de partida | **Fatia 0 + Fatia 1** | 2026-06-21 |
| Frontend | **TypeScript** (strict) | 2026-06-23 |

---

## 1. Diagnóstico: ativos existentes

| Ativo | O que é | Papel |
|---|---|---|
| `README.md` | A visão: coletar → armazenar → correlacionar → explicar, 100% local | Norte do produto |
| `C:/Cofres_C/IdeaDDoS/Dash_Manager_Windows/` | Protótipo Streamlit funcional (métricas, processos, assinatura digital, serviços, atalhos Win+R, "explicar com Claude" desligado) | Fonte de lógica p/ os collectors |
| `C:/Cofres_C/IdeaDDoS/clones/dashboards_us-media/` | Arquitetura de referência limpa (FastAPI + Pydantic v2 + camadas + React/Vite), porém cloud/multi-tenant | Molde estrutural |

**Sacada central:** adotar a estrutura em camadas do us-media e **descartar** tudo
que é nuvem/multiusuário (GCP, Firestore, Cloud Run, OAuth, magic links). O
Windows Intelligence Center é **local, single-user, privacidade-first**.

## 2. Princípios não negociáveis

- **Local-first** — sem nuvem/servidor remoto; backend em `localhost`.
- **Só sinaliza, nunca remove** — não é antivírus; ações destrutivas só com confirmação.
- **Honestidade sobre limitações** — coletor sem privilégio vira `partial=True` com motivo.
- **Uma fonte canônica, múltiplos destinos** — schema/dataclasses como espinha dorsal.
- **Claude é opcional** — painel funciona sem `ANTHROPIC_API_KEY`; modelo Haiku p/ chamadas curtas.
- **Convenções** — docstrings/comentários em português, identificadores em inglês, `from __future__ import annotations` no topo.
- **Método iterativo** — fatias verticais, validar uma decisão por vez.

## 3. Stack

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI + Pydantic v2 + pydantic-settings |
| Coleta | psutil + PowerShell/WMI + Get-WinEvent |
| Armazenamento | SQLite (camada de repositório) |
| Agendador | APScheduler / task asyncio (sampler) |
| Frontend | React 18 + Vite + i18n (PT) + tema escuro |
| IA | anthropic SDK (Haiku), feature-flag |
| Empacotar | start.ps1 (dev) → PyInstaller (futuro) |

## 4. Estrutura-alvo

```text
Windows_Intelligence_Center/
├── backend/
│   ├── api/              # routers: metrics, processes, events, services, ports, audit, explain
│   ├── collectors/       # EXTRACT: system, processes, ports, services, events, security
│   ├── analyzers/        # TRANSFORM: findings, scoring, anomaly
│   ├── services/         # sampler (background), claude_client, explain_cache
│   ├── storage/          # db.py (engine), schema/migrations, repositories
│   ├── models/           # schema.py (dataclasses) + pydantic (payloads de API)
│   ├── config.py
│   └── main.py           # app FastAPI + serve SPA do React
├── frontend/
│   └── src/{api,components,pages,context,i18n,utils}/
├── database/             # arquivo .db em runtime (gitignored) + DDL versionado
├── scripts/
├── docs/
└── tests/
```

## 5. Modelo de dados (SQLite)

| Tabela | Conteúdo | Origem |
|---|---|---|
| `metric_samples` | ts, cpu_pct, mem_pct, mem_used, disk_pct, net_sent, net_recv | sampler |
| `process_samples` | ts, pid, name, cpu, rss, user (top-N) | collectors/processes |
| `events` | ts, log, provider, event_id, level, message | collectors/events |
| `audits` | ts, score, resumo | analyzers/scoring |
| `findings` | audit_id, severity, category, description, recommendation | analyzers/findings |
| `explanations` | hash(meta), texto, modelo, ts (cache) | serviço Claude |

## 6. Roadmap em fatias verticais

Cada fatia entrega coletor → storage → API → UI ponta a ponta, mapeada às fases do README.

| Fatia | Entrega | Fase README |
|---|---|---|
| **0** ✅ | Fundação: esqueleto backend+frontend, config, `/api/health`, start.ps1, `.gitignore` — **concluída 2026-06-23** | — |
| **1** | Métricas ao vivo (CPU/mem/disco/rede) + KPI cards | Fase 1 |
| **2** | Processos + metadados (assinatura, serviços) + detalhe | Fase 1 |
| **3** | Histórico: sampler em background + `/metrics/history` + gráficos ⭐ | Fase 1→3 |
| **4** | Alertas por limiar configurável | Fase 1 |
| **5** | Logs / Event Viewer (Get-WinEvent) + busca/filtros | Fase 2 |
| **6** | Postura de segurança: ports/services/security_config + findings + score | Fase 4 |
| **7** | Explicações com Claude (Haiku) + cache | Fase 3 |
| **8** | Anomalias, baseline, comparação entre períodos, correlação | Fase 3 |
| **9** | Atalhos Win+R + export de snapshot (JSON/HTML/CSV) | Fase 3/4 |

## 7. Itens transversais

- **Git hygiene:** `dashboards_us-media/` tem `.git` próprio (repo aninhado) — decidir referência/submódulo/cópia. `.venv/`, `.mp4`, `.dmp`, datasets → `.gitignore`.
- **Testes:** pytest p/ collectors (mock de privilégio `partial`) e analyzers; testes de contrato dos endpoints.
- **i18n + tema:** PT padrão, tema escuro.
- **Privacidade:** auditar que nenhuma rota externa é chamada exceto Claude (opt-in).

## 8. Riscos / decisões em aberto

1. Convivência com o protótipo Streamlit (mantido até paridade).
2. Privilégio de administrador (UI sinaliza "parcial").
3. Política de retenção/agregação do histórico (ex.: raw 7 dias → roll-up por hora).

---

## Detalhe da Fatia 0 — Fundação

**Backend**
- `backend/config.py` — `Settings` (pydantic-settings): `app_port`, `sample_interval_seconds`, `db_path`, `anthropic_api_key`, `allowed_origins`.
- `backend/main.py` — app FastAPI, CORS, monta routers, serve SPA do React em `/static` (padrão us-media).
- `backend/api/router.py` + `backend/api/health.py` — `GET /api/health` → `{status, version, platform, is_admin}`.
- `backend/storage/db.py` — engine SQLite + criação de schema na subida.
- `backend/requirements.txt` — fastapi, uvicorn, pydantic, pydantic-settings, psutil, apscheduler, anthropic.

**Frontend**
- `frontend/` — scaffold Vite + React, `AppContext` (tema/i18n), client HTTP, tela inicial consumindo `/api/health`.

**Infra**
- `scripts/start.ps1` — sobe backend (`:8000`) e frontend (`:5173`) em paralelo (padrão `dev.ps1` do us-media).
- `.gitignore` — `.venv/`, `__pycache__/`, `*.db`, `node_modules/`, datasets/dumps/vídeos pesados.

**Pronto quando:** `start.ps1` sobe os dois serviços e a tela mostra "online" lendo `/api/health`.

> **Status (2026-06-23): concluída.** Backend validado (TestClient + uvicorn real
> na `:8000` → `/api/health` 200; schema SQLite versionado via `database/schema.sql`
> + tabela `schema_meta`). Frontend em **TypeScript** compila e builda (`tsc --noEmit`
> + `vite build`). Backend bind em `127.0.0.1` (local-first). Falta só o check visual
> final via `start.ps1`. Pré-requisitos instalados: `backend/.venv` + `frontend/node_modules`.

## Detalhe da Fatia 1 — Métricas ao vivo

**Backend**
- `backend/collectors/system.py` — extrai a lógica de `dashboard.py` (CPU/mem/disco/rede via psutil); retorna dataclass + `CollectorMeta`.
- `backend/models/schema.py` — dataclasses base (`SystemMetrics`, `CollectorMeta`).
- `backend/api/metrics.py` — `GET /api/metrics/live` → snapshot atual.

**Frontend**
- `KPIStrip` / cards de CPU, memória, disco, rede com polling (intervalo configurável).
- Cabeçalho com host, OS, uptime (porta de `uptime_str`).

**Pronto quando:** a tela mostra os 4 KPIs atualizando ao vivo, lendo do backend real.
