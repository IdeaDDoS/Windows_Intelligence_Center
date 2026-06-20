# Windows Intelligence Center

Plataforma local de observabilidade, diagnóstico e análise do Windows.

O objetivo deste projeto é criar um painel centralizado capaz de coletar, armazenar, correlacionar e explicar informações do sistema operacional em tempo real, transformando logs e métricas técnicas em informações compreensíveis e acionáveis.

A inspiração inicial surgiu de uma ferramenta simples de monitoramento local de CPU, memória, disco e processos. Entretanto, o escopo evoluiu para uma plataforma mais robusta, adotando uma arquitetura moderna baseada em frontend, backend, serviços especializados e armazenamento estruturado de dados.

## Objetivo

Criar um centro de inteligência para o Windows que permita:

* Monitorar recursos do sistema em tempo real.
* Coletar eventos e logs do Windows.
* Centralizar informações hoje dispersas entre diversas ferramentas.
* Detectar anomalias e comportamentos incomuns.
* Explicar processos, serviços e eventos em linguagem simples.
* Construir histórico para análises futuras.
* Auxiliar investigações de desempenho, estabilidade e segurança.

O projeto funciona localmente, priorizando privacidade e controle total dos dados.

---

## Visão Geral

O sistema atua como uma camada de observabilidade sobre o Windows.

```text
Windows
│
├── Processos
├── Serviços
├── Event Viewer
├── Performance Counters
├── Logs do Sistema
├── Rede
├── Disco
└── Hardware
        │
        ▼
 Coletores
        │
        ▼
 Banco de Dados Local
        │
        ▼
 API de Diagnóstico
        │
        ▼
 Dashboard Web
        │
        ▼
 Análises e Explicações
```

---

## Principais Funcionalidades

### Monitoramento em Tempo Real

* CPU
* Memória
* Disco
* Rede
* Temperatura (quando disponível)
* Processos ativos

### Centralização de Logs

* Event Viewer
* Logs de Aplicações
* Logs de Sistema
* Logs de Segurança
* Logs personalizados

### Diagnóstico Inteligente

* Explicação de processos
* Explicação de eventos do Windows
* Identificação de possíveis gargalos
* Correlação entre eventos e consumo de recursos

### Histórico

* Armazenamento local de métricas
* Tendências de uso
* Comparação entre períodos
* Investigação retroativa de problemas

### Alertas

* Uso excessivo de CPU
* Consumo anormal de memória
* Picos de disco
* Eventos críticos do Windows
* Regras personalizadas

---

## Arquitetura

A arquitetura segue conceitos inspirados em aplicações modernas de observabilidade.

```text
windows-intelligence-center/

backend/
├── api/
├── collectors/
├── analyzers/
├── services/
├── storage/
└── main.py

frontend/
├── src/
├── components/
├── pages/
├── charts/
└── services/

database/
├── metrics
├── logs
└── events

scripts/
docs/
```

### Responsabilidades

| Camada       | Função                              |
| ------------ | ----------------------------------- |
| Collectors   | Capturam dados do Windows           |
| Storage      | Persistência local                  |
| API          | Disponibiliza dados para o frontend |
| Analyzer     | Correlação e interpretação          |
| Frontend     | Visualização e interação            |
| Alert Engine | Geração de alertas                  |

---

## Roadmap

### Fase 1 — Observabilidade

* [ ] Monitoramento de CPU
* [ ] Monitoramento de memória
* [ ] Monitoramento de disco
* [ ] Processos ativos
* [ ] Dashboard inicial

### Fase 2 — Logs

* [ ] Integração com Event Viewer
* [ ] Histórico local
* [ ] Filtros avançados
* [ ] Busca por eventos

### Fase 3 — Inteligência

* [ ] Explicação automática de eventos
* [ ] Correlação entre falhas
* [ ] Detecção de anomalias
* [ ] Sugestões de correção

### Fase 4 — Segurança

* [ ] Monitoramento de serviços
* [ ] Auditoria de alterações
* [ ] Alertas de comportamento suspeito
* [ ] Relatórios periódicos

---

## Filosofia

O Windows gera uma quantidade enorme de informações técnicas diariamente.

Grande parte delas fica espalhada entre ferramentas diferentes:

* Gerenciador de Tarefas
* Visualizador de Eventos
* Monitor de Recursos
* Performance Monitor
* Logs diversos

O objetivo deste projeto é reunir essas informações em um único lugar e transformá-las em conhecimento útil.

Em vez de apenas mostrar números, o sistema busca responder:

**O que aconteceu?**

**Por que aconteceu?**

**O que merece atenção?**

**O que posso fazer a respeito?**
