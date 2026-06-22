# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é este repositório (leia primeiro)

**Windows Intelligence Center** é uma plataforma **local** de observabilidade,
diagnóstico e análise do Windows — coletar → armazenar → correlacionar →
explicar, 100% na máquina (sem nuvem, single-user, privacidade-first).

O projeto está em fase **greenfield**: ainda **não foi scaffoldado**. Hoje o repo
contém só `README.md` (a visão), `docs/PLANEJAMENTO.md` (o plano) e duas pastas
que são **apenas referência** — não são o produto e não devem ser editadas como
se fossem o código ativo.

- **`docs/PLANEJAMENTO.md` é o plano autoritativo** — stack, estrutura-alvo,
  modelo de dados SQLite, princípios e o roadmap em fatias verticais (0–9).
  **Leia-o antes de implementar qualquer coisa**; mantenha-o atualizado conforme
  as decisões evoluem (é documento vivo).
- O `README.md` é o **norte do produto** (visão e fases), não um mapa do código
  atual.

## As duas pastas são REFERÊNCIA, não o produto

| Pasta | Papel | Como usar |
|-------|-------|-----------|
| `Dash_Manager_Windows/` | Protótipo Streamlit **funcional** (métricas psutil, processos, assinatura digital, serviços, atalhos Win+R, "explicar com Claude" desligado) + motor ETL `.local/security_audit/` | **Fonte de lógica para os collectors/analyzers.** Porte a lógica daqui; não construa o produto dentro dela. Tem `CLAUDE.md` própria detalhando o motor de auditoria. |
| `dashboards_us-media/` | Arquitetura de referência **limpa**: FastAPI + Pydantic v2 em camadas + React/Vite + SPA servida pelo `main.py` | **Molde estrutural.** Copie o padrão de camadas e o jeito de servir a SPA. **Descarte tudo que é nuvem/multi-tenant** (GCP, Firestore, Cloud Run, OAuth, magic links) — o WIC é local e single-user. Tem `.git` próprio (repo aninhado). |

**A sacada central do projeto:** adotar a estrutura em camadas do `us-media` e
extrair a lógica de coleta do `Dash_Manager_Windows`, juntando os dois num
backend FastAPI local com armazenamento SQLite.

## Estrutura-alvo (a construir — ainda não existe)

Conforme `docs/PLANEJAMENTO.md`:

```text
backend/
├── api/          # routers: metrics, processes, events, services, ports, audit, explain
├── collectors/   # EXTRACT: system, processes, ports, services, events, security
├── analyzers/    # TRANSFORM: findings, scoring, anomaly
├── services/     # sampler (background), claude_client, explain_cache
├── storage/      # db.py (engine SQLite), migrations, repositories
├── models/       # schema.py (dataclasses canônicas) + pydantic (payloads de API)
├── config.py     # Settings (pydantic-settings)
└── main.py       # app FastAPI + serve a SPA do React
frontend/src/{api,components,pages,context,i18n,utils}/
database/         # arquivo .db em runtime (gitignored) + DDL versionado
scripts/          # start.ps1 etc.
tests/
```

- **Padrão de pipeline (vem do `security_audit`):** `models/schema.py` é a espinha
  dorsal (dataclasses canônicas); **collectors só coletam e normalizam, não
  analisam** e devolvem `(dado, CollectorMeta)`; **analyzers** aplicam regras
  (`findings`) e derivam `score`; uma fonte canônica alimenta múltiplos destinos.
- **Modelo de dados SQLite:** tabelas `metric_samples`, `process_samples`,
  `events`, `audits`, `findings`, `explanations` (cache) — detalhes em
  `PLANEJAMENTO.md §5`.

## Como construir: fatias verticais

Cada fatia entrega **collector → storage → API → UI** ponta a ponta. O ponto de
partida travado é **Fatia 0 (fundação) + Fatia 1 (métricas ao vivo)** — o passo a
passo concreto com arquivos e contratos está em `PLANEJAMENTO.md` (seções
"Detalhe da Fatia 0/1"). Não tente "entregar tudo pronto"; valide uma decisão por
vez.

## Comandos

Ainda **não há** comandos de build/test/lint do produto — ele não foi
scaffoldado. O plano (Fatia 0) prevê:

```powershell
# (a criar) sobe backend :8000 + frontend :5173 em paralelo, espelhando dev.ps1 do us-media
.\scripts\start.ps1
```

Enquanto isso, dá para rodar os **protótipos de referência** para estudar o
comportamento:

```powershell
# Protótipo Streamlit (referência de coleta) — abre em localhost:8501
cd Dash_Manager_Windows/dashboard
pip install -r requirements.txt
streamlit run dashboard.py

# Motor ETL de auditoria (referência do pipeline collectors→analyzers→report)
cd Dash_Manager_Windows/.local/security_audit
python main.py            # JSON + HTML (+ PDF se weasyprint)
```

No Windows, rode o terminal **como administrador** para coleta completa; sem
elevação os coletores se marcam `partial` (devem degradar, nunca quebrar).

## Princípios não negociáveis

- **Local-first** — backend em `localhost`, sem nuvem/servidor remoto.
- **Só sinaliza, nunca remove** — não é antivírus; ação destrutiva só com
  confirmação explícita.
- **Honestidade sobre limitações** — coletor sem privilégio vira
  `CollectorMeta(partial=True)` com o motivo; não afirme garantia que não
  consegue verificar.
- **Claude é opcional** — o painel funciona sem `ANTHROPIC_API_KEY`; o recurso
  "explicar" usa Haiku 4.5 (`claude-haiku-4-5-20251001`), barato para chamadas
  curtas, atrás de feature-flag. A API é cobrada por uso, separada da Pro.
- **Uma fonte canônica, múltiplos destinos** — schema/dataclasses como contrato;
  mudar o contrato propaga para storage, API e UI.

## Convenções

- Docstrings e comentários em **português**; identificadores em **inglês**.
- `from __future__ import annotations` no topo dos módulos Python.
- Não versionar `.venv/`, `__pycache__/`, `*.db`, `node_modules/`, nem os
  artefatos pesados do protótipo (`.mp4`, `.dmp`, datasets, `reports/`).

## Topologia git (cuidado)

- O repo da raiz versiona o produto novo (hoje só `README.md` está rastreado;
  `docs/` e as pastas de referência aparecem como untracked).
- **`dashboards_us-media/` tem `.git` próprio** (origin `bitflowin/dashboards_us-media`).
  É um repo aninhado; está em aberto se vira referência externa, submódulo ou
  cópia limpa (`PLANEJAMENTO.md §7/§8`). **Não** faça `git add` dele pela raiz
  sem resolver isso antes.
- `Dash_Manager_Windows/` não é repo git; é pasta de referência solta.
