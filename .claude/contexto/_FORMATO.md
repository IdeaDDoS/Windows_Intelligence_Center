# Contexto — memória coletiva do projeto

Diário estruturado e compartilhado (usuário + Claude). Cada sessão de trabalho
vira um registro datado. Serve para: ver **o que foi feito e quando**, rastrear
**decisões/objetivos**, e enxergar **as viradas** de rumo ao longo do tempo.

## Convenção
- **Um arquivo por dia**: `AAAA-MM-DD.md` (ex.: `2026-06-21.md`).
- Dentro, **uma entrada por sessão/horário** — sempre com `hora`.
- Estilo **objetivo, quase dicionário** (campos fixos), não prosa longa.
- Ordem cronológica: entradas mais novas embaixo.

## Campos de cada entrada
```
## HH:MM — <título curto da sessão>
- feito:        o que foi efetivamente realizado (lista)
- resolvido:    problemas fechados (lista)
- decisões:     escolhas/objetivos estabelecidos (lista)
- viradas:      mudanças de rumo / repensadas (se houve)
- próximos:     o que fica em aberto para a próxima vez
- artefatos:    arquivos/scripts criados ou alterados
```
Campos sem conteúdo podem ser omitidos.

## Manutenção
- O Claude atualiza este diário **por conta própria**, sempre **avisando** que
  está atualizando.
- Gatilho = **fechamento de tópico/marco** (registrar por tópicos), não no meio
  de um raciocínio.
