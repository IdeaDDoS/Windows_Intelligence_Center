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
| Escopo do 1º teste do harness | **Fase 1 = fatias 1–4**, execução autônoma | 2026-06-23 |
| Verificação de "pronto" | **Testes automatizados** (pytest + vitest) verdes | 2026-06-23 |
| Sampler (Fatia 3) | **asyncio task** no lifespan (APScheduler descartado) | 2026-06-23 |
| Gráficos / data-fetching | **Recharts + TanStack Query** | 2026-06-23 |
| Alertas (Fatia 4) | **in-app** (badge + lista), sem notificação nativa | 2026-06-23 |
| Assinatura digital (Fatia 2) | **sob demanda** no detalhe do processo | 2026-06-23 |

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
| Coleta | psutil + PowerShell (Get-AuthenticodeSignature, Get-WinEvent) + WMI |
| Armazenamento | SQLite (camada de repositório) |
| Sampler | **asyncio task** no lifespan (APScheduler descartado) |
| Frontend | React 18 + Vite + **TypeScript** + **Recharts** + **TanStack Query** + i18n (PT) + tema escuro |
| IA | anthropic SDK (Haiku `claude-haiku-4-5-20251001`), feature-flag |
| Testes | **pytest** (backend) + **vitest** (frontend) |
| Empacotar | start.ps1 (dev) → PyInstaller (futuro) |

## 4. Estrutura-alvo

```text
Windows_Intelligence_Center/
├── backend/
│   ├── api/              # routers: metrics, processes, services, alerts, events, audit, explain
│   ├── collectors/       # EXTRACT: system, processes, services, signature, events, security
│   ├── analyzers/        # TRANSFORM: alerts (limiar), findings, scoring, anomaly
│   ├── services/         # sampler (asyncio), claude_client, explain_cache
│   ├── storage/          # db.py (engine), repositories
│   ├── models/           # schema.py (dataclasses) + pydantic (payloads de API)
│   ├── config.py
│   └── main.py           # app FastAPI + serve SPA do React
├── frontend/
│   └── src/{api,components,pages,context,i18n,utils}/
├── database/             # wic.db em runtime (gitignored) + schema.sql versionado
├── scripts/
├── docs/
└── tests/                # pytest (backend) — vitest mora em frontend/
```

## 5. Modelo de dados (SQLite)

**Convenções:** toda tabela tem `id INTEGER PRIMARY KEY AUTOINCREMENT`; carimbos de
tempo em `ts TEXT` no formato **ISO-8601 UTC**; **índice em `ts`** nas tabelas de
série temporal. `net_sent/net_recv` guardam o **acumulado** do psutil (a taxa/delta
é derivada na borda). DDL versionado em `database/schema.sql`, controlado por
`schema_meta`.

| Tabela | Colunas (além de `id`) | Origem | Fatia |
|---|---|---|---|
| `metric_samples` | ts, cpu_pct, mem_pct, mem_used_gb, disk_pct, net_sent, net_recv | sampler | 3 |
| `alert_rules` | metric, operator, threshold, duration_s, enabled | UI de alertas | 4 |
| `alerts` | rule_id, ts, value, message, acknowledged | alert engine | 4 |
| `process_samples` | ts, pid, name, cpu_pct, rss_mb, username (top-N) | collectors/processes | futuro (opcional) |
| `events` | ts, log, provider, event_id, level, message | collectors/events | 5 |
| `audits` | ts, score, resumo | analyzers/scoring | 6 |
| `findings` | audit_id, severity, category, description, recommendation | analyzers/findings | 6 |
| `explanations` | hash(meta), texto, modelo, ts (cache) | serviço Claude | 7 |

**Retenção:** `metric_samples` mantém **raw por 7 dias** (expurgo das amostras
antigas no próprio sampler); roll-up/agregação por hora **adiado** para fatia futura.

## 6. Roadmap em fatias verticais

Cada fatia entrega coletor → storage → API → UI ponta a ponta, mapeada às fases do README.

| Fatia | Entrega | Fase README |
|---|---|---|
| **0** ✅ | Fundação: esqueleto backend+frontend, config, `/api/health`, start.ps1, `.gitignore` — **concluída 2026-06-23** | — |
| **1** 🎯 | Métricas ao vivo (CPU/mem/disco/rede) + KPI cards | Fase 1 |
| **2** 🎯 | Processos + metadados (assinatura, serviços) + detalhe | Fase 1 |
| **3** 🎯 | Histórico: sampler em background + `/metrics/history` + gráficos ⭐ | Fase 1→3 |
| **4** 🎯 | Alertas por limiar configurável | Fase 1 |
| **5** | Logs / Event Viewer (Get-WinEvent) + busca/filtros | Fase 2 |
| **6** | Postura de segurança: ports/services/security_config + findings + score | Fase 4 |
| **7** | Explicações com Claude (Haiku) + cache | Fase 3 |
| **8** | Anomalias, baseline, comparação entre períodos, correlação | Fase 3 |
| **9** | Atalhos Win+R + export de snapshot (JSON/HTML/CSV) | Fase 3/4 |

🎯 = escopo do 1º teste de execução autônoma do claude-harness (ver "Protocolo" abaixo).

## 7. Itens transversais

- **Referências externas:** o molde `dashboards_us-media/` e o protótipo
  `Dash_Manager_Windows/` vivem **fora** do repo (em `C:/Cofres_C/IdeaDDoS/clones/`
  e `C:/Cofres_C/IdeaDDoS/`). São referência de consulta, **não versionadas** no
  WIC — não são submódulo nem cópia. (Decisão resolvida.)
- **Testes:** pytest (collectors com mock de privilégio `partial`, analyzers,
  contrato dos endpoints) + vitest (componentes). Testes verdes = critério de
  "pronto" por fatia.
- **i18n + tema:** PT padrão, tema escuro.
- **Privacidade:** auditar que nenhuma rota externa é chamada exceto Claude (opt-in).

## 8. Riscos / decisões em aberto

- **Resolvidas:** privilégio admin (campo `is_admin` no `/api/health`; collectors
  degradam `partial`); retenção do histórico (**raw 7 dias, sem roll-up** — §5);
  git hygiene das pastas de referência (externas — §7).
- **Em aberto:** convivência com o protótipo Streamlit (mantido até paridade);
  empacotamento final (PyInstaller, fatia futura); temperatura de hardware
  (best-effort no Windows — adiada).

---

## Protocolo de execução autônoma (1º teste do claude-harness)

> Duplo objetivo desta rodada: **construir** as fatias 1–4 do WIC e, ao mesmo
> tempo, **testar** se o claude-harness conduz o processo sozinho até o fim.

**Escopo autônomo:** fatias **1, 2, 3 e 4** (Fase 1). As fatias 5–9 ficam fora.

**Loop por fatia** (sem aprovação humana entre fatias):
1. Lê o "Detalhe da Fatia N" abaixo (contratos já fechados — sem adivinhação).
2. Implementa `collector → storage → API → UI`.
3. Escreve e roda os testes da fatia (`pytest` + `vitest`).
4. Verde? → `git commit` (conventional, **sem push**) → segue para a próxima fatia.
5. Vermelho? → corrige e re-roda, sujeito à política de parada.

**Política de parada (break) — evita loop infinito:**
- O avanço **exige testes verdes**. Se uma unidade travar, o orçamento é
  **15 min de wall-clock OU 3 tentativas sem progresso** (mesma causa raiz) — o
  que vier primeiro.
- Ao estourar: **para tudo** (não pula de fatia), **não desfaz** o trabalho
  parcial (é local, conserta-se depois) e escreve um **relatório de bloqueio**:
  `fatia · unidade · causa raiz · tentativas · erro do teste · hipóteses`. Então
  aguarda o usuário. Sem estouro, segue sozinho até concluir a Fatia 4.
- `push` e qualquer publicação ficam **sempre** com o usuário.

---

## Detalhe da Fatia 0 — Fundação

**Backend**
- `backend/config.py` — `Settings` (pydantic-settings): `app_port`, `sample_interval_seconds`, `db_path`, `anthropic_api_key`, `allowed_origins`.
- `backend/main.py` — app FastAPI, CORS, monta routers, serve SPA do React em `/static` (padrão us-media).
- `backend/api/router.py` + `backend/api/health.py` — `GET /api/health` → `{status, version, platform, is_admin}`.
- `backend/storage/db.py` — engine SQLite + criação de schema na subida.
- `backend/requirements.txt` — fastapi, uvicorn, pydantic, pydantic-settings, psutil, anthropic.

**Frontend**
- `frontend/` — scaffold Vite + React + TypeScript, `AppContext` (tema/i18n), client HTTP, tela inicial consumindo `/api/health`.

**Infra**
- `scripts/start.ps1` — sobe backend (`:8000`) e frontend (`:5173`) em paralelo (padrão `dev.ps1` do us-media).
- `.gitignore` — `.venv/`, `__pycache__/`, `*.db`, `node_modules/`, `dist/`, `*.tsbuildinfo`.

**Pronto quando:** `start.ps1` sobe os dois serviços e a tela mostra "online" lendo `/api/health`.

> **Status (2026-06-23): concluída.** Backend validado (TestClient + uvicorn real
> na `:8000` → `/api/health` 200; schema SQLite versionado via `database/schema.sql`
> + tabela `schema_meta`). Frontend em **TypeScript** compila e builda (`tsc --noEmit`
> + `vite build`). Backend bind em `127.0.0.1` (local-first). Pré-requisitos
> instalados: `backend/.venv` + `frontend/node_modules`.

---

## Detalhe da Fatia 1 — Métricas ao vivo

**Contratos (espinha dorsal — `backend/models/schema.py`)**
- `@dataclass CollectorMeta`: `partial: bool = False`, `reason: str | None = None`, `source: str`, `collected_at: datetime`, `duration_ms: int`.
- `@dataclass SystemMetrics`: `cpu_pct`, `mem_pct`, `mem_used_gb`, `mem_total_gb`, `disk_pct`, `disk_used_gb`, `disk_total_gb`, `net_sent`, `net_recv`, `uptime_seconds`.
- `@dataclass HostInfo`: `hostname`, `os`, `boot_time`.
- Padrão de coletor: retorna **`(payload, CollectorMeta)`**.

**Backend**
- `backend/collectors/system.py` — `collect_system_metrics() -> tuple[SystemMetrics, CollectorMeta]` via psutil (porta da lógica do `dashboard.py`). `disk_pct` = volume `C:`.
- `backend/api/metrics.py` — `GET /api/metrics/live` → pydantic `MetricsLiveResponse { metrics, host, meta }`. Registrar no `api/router.py`.

**Frontend**
- `src/api/client.ts` — `metricsLive(): Promise<MetricsLiveResponse>` (tipos espelham o backend).
- `src/components/KPIStrip.tsx` — 4 cards (CPU, memória, disco, rede) com **TanStack Query** em polling de **2s**.
- Cabeçalho com host, OS e uptime (de `uptime_seconds`).

**Testes (critério de pronto)**
- `tests/test_collectors_system.py` — coletor devolve `SystemMetrics` + `CollectorMeta`; percentuais em 0–100; `source` preenchido; caminho `partial` testado com mock.
- `tests/test_api_metrics.py` — `GET /api/metrics/live` → 200 e shape `{metrics, host, meta}`.
- `frontend/src/components/KPIStrip.test.tsx` (vitest) — renderiza 4 cards dado um mock de resposta.

**Pronto quando:** os 3 testes acima passam (pytest + vitest verdes).

---

## Detalhe da Fatia 2 — Processos, serviços e detalhe

**Contratos (`backend/models/schema.py`)**
- `ProcessInfo`: `pid`, `name`, `cpu_pct`, `rss_mb`, `username`, `exe`.
- `ServiceInfo`: `name`, `display_name`, `status`, `start_type`.
- `SignatureInfo`: `is_signed: bool`, `status`, `signer: str | None`.
- `ProcessDetail`: `ProcessInfo` + `signature: SignatureInfo`.

**Backend**
- `backend/collectors/processes.py` — `collect_processes(top_n=15) -> tuple[list[ProcessInfo], CollectorMeta]` (psutil; ordena por `cpu_pct` desc).
- `backend/collectors/services.py` — `collect_services() -> tuple[list[ServiceInfo], CollectorMeta]` (`psutil.win_service_iter`; degrada `partial` sem privilégio).
- `backend/collectors/signature.py` — `get_signature(exe_path) -> SignatureInfo` via PowerShell `Get-AuthenticodeSignature` — **chamado só no detalhe** (sob demanda).
- `backend/api/processes.py` — `GET /api/processes` (top-N), `GET /api/processes/{pid}` (detalhe + assinatura; **404** se o pid sumiu).
- `backend/api/services.py` — `GET /api/services`.

**Frontend**
- `src/pages/ProcessesPage.tsx`, `src/components/ProcessTable.tsx`, `src/components/ProcessDetailModal.tsx`, `src/components/ServicesTable.tsx`.

**Testes (critério de pronto)**
- `tests/test_collectors_processes.py` — respeita `top_n`; ordenação por CPU; `meta`.
- `tests/test_api_processes.py` — lista 200; detalhe 200 com `signature`; pid inexistente → 404.
- `frontend/src/components/ProcessTable.test.tsx` (vitest) — renderiza linhas dado mock.

**Pronto quando:** os testes acima passam (pytest + vitest verdes).

---

## Detalhe da Fatia 3 — Histórico (sampler + gráficos) ⭐

**Storage**
- `database/schema.sql` — adiciona `metric_samples` (tipos/índice da §5). `SCHEMA_VERSION` → 2.
- `backend/storage/repositories.py` — `insert_metric_sample(...)`, `query_history(range) -> list[...]` (downsample no backend).

**Backend**
- `backend/services/sampler.py` — **asyncio task** no lifespan; a cada `sample_interval_seconds` (5s) chama `collect_system_metrics` e persiste; **expurga amostras > 7 dias** (retenção raw).
- `backend/api/metrics.py` — `GET /api/metrics/history?range=1h|6h|24h` → série temporal (downsampled).

**Frontend**
- `src/components/MetricsChart.tsx` (Recharts) + `src/pages/HistoryPage.tsx`; seletor de janela (1h/6h/24h).

**Testes (critério de pronto)**
- `tests/test_sampler.py` — uma iteração insere `metric_sample`; retenção apaga > 7 dias (com ts mockado).
- `tests/test_api_history.py` — `range` válido → série no shape esperado; downsample limita pontos.
- `frontend/src/components/MetricsChart.test.tsx` (vitest) — renderiza dado série mock.

**Pronto quando:** os testes acima passam **e** o sampler persiste amostras ao rodar.

---

## Detalhe da Fatia 4 — Alertas por limiar (in-app)

**Storage**
- `database/schema.sql` — adiciona `alert_rules` e `alerts` (§5). `SCHEMA_VERSION` → 3. **Seed** de regras default: CPU `>` 90% por 60s, mem `>` 90%, disk `>` 90%.

**Backend**
- `backend/analyzers/alerts.py` — `evaluate(metrics, rules) -> list[Alert]`; respeita `duration_s` (viola por X s antes de alertar). Chamado pelo sampler a cada amostra.
- `backend/api/alerts.py` — `GET /api/alerts`, `GET/POST/PUT /api/alert_rules` (configurar limiar), `POST /api/alerts/{id}/ack`.

**Frontend**
- `src/components/AlertBadge.tsx` (contador), `src/components/AlertsList.tsx`, `src/pages/AlertsPage.tsx` (configurar limiares). **In-app apenas** — sem notificação nativa do Windows.

**Testes (critério de pronto)**
- `tests/test_alert_engine.py` — dispara ao violar; **não** dispara abaixo do limiar; respeita `duration_s`.
- `tests/test_api_alerts.py` — lista; ack muda `acknowledged`; criar/editar regra.
- `frontend/src/components/AlertBadge.test.tsx` (vitest) — mostra contagem dado mock.

**Pronto quando:** os testes acima passam (pytest + vitest verdes). **Fim do escopo
autônomo** — o harness relata o resultado das 4 fatias e devolve o controle.
