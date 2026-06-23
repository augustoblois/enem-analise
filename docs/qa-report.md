# QA Report — Análise dos Microdados do ENEM (Desigualdade Socioeconômica × Desempenho)

> Fontes: briefing.md, prd.md, backlog.md, TASKS.md. Gerado pelo qa-agent.
> Auditoria independente da cadeia de governança antes do desenvolvimento.
> Contexto: cadeia remodelada 2x em 2026-06-19 — (1) pivot da quebra de linkage LGPD nos
> microdados 2024; (2) exigência do professor de um **produto USÁVEL e vivo** → módulo vivo
> (escola×região×nota via RESULTADOS, ingere edições novas incl. 2024) + dashboard repriorizado P0.
> Esta é a RE-AUDITORIA após a 2ª remodelagem.

## Veredito: APROVADO
Cadeia íntegra: 0 bloqueios. A 2ª remodelagem está coerente nos quatro documentos — o módulo
vivo entrou com rastreabilidade fechada (O7→RF-15/RF-16/RNF-07→EP-07→US-20..US-23→TASKS, integrado
em US-14 e US-15) e a fronteira crítica (SES×nota 2024+ = impossível) foi preservada em todos os
docs sem contradição. Sem órfãos, sem invenções. 5 avisos não-bloqueantes — gaps já documentados
ou riscos a vigiar, nenhum força REPROVADO.

## Resumo por seam
- **A · briefing → PRD:** OK — 7 objetivos medíveis (O7 novo) traçam a intenção do briefing; escopo
  com IN (módulo vivo) e OUT (SES 2024+ impossível) explícitos; 16 RF com persona + goal; nenhum requisito inventa escopo.
- **B · PRD → backlog:** OK — 7 épicos (EP-07 novo, EP-06 repriorizado P0) fatiados; cada story sob
  um épico; INVEST mantido; aceite Given/When/Then; estimativas Fibonacci ≤ 8; DoD único (com cláusula
  de desacoplamento do módulo vivo); dependências explícitas e ordem coerente.
- **C · backlog → TASKS.md:** OK — 7 seções de épico, 22 stories + tasks como checkboxes; US-19 marcada como NÃO semeada em ambos.
- **Órfãos / invenções:** OK — nenhum requisito/story/task órfão; o "módulo vivo" tem fonte upstream completa (não é mais invenção); nenhum resquício de SES-2024-analisável.

## Coerência da 2ª remodelagem (foco da auditoria) — verificada
- **Mesma história nos quatro docs:** núcleo SES (P1/P4/P5) congelado em 2022–2023 + módulo vivo
  restrito a escola×região×nota (P2/P3) via RESULTADOS, capaz de ingerir 2024+. Briefing (l.7,34,44),
  PRD (l.7,14,41,90), backlog (l.15-20,431-440) e TASKS (l.9-12,124-127) contam isso de forma idêntica.
- **Nenhuma contradição com o escopo antigo:** na 1ª remodelagem o "produto vivo" foi marcado como
  abandonado; a 2ª o reintroduz **corretamente como módulo restrito a P2/P3**. Nenhum doc ainda diz
  "produto vivo abandonado" enquanto outro o exige — o pivot foi propagado por completo. (Esta re-auditoria
  substitui o texto da 1ª auditoria que afirmava "produto vivo só como abandonado", agora desatualizado.)
- **Fronteira crítica preservada (sem bloqueio factual):** SES×nota (renda/preditores/perfil/raça/sexo)
  em 2024+ segue declarado IMPOSSÍVEL em todos os docs — briefing (l.34,43), PRD (l.45 "nunca como dado
  analisado", O6 l.22), backlog (l.216-218, US-18 l.252-254, l.437) e TASKS (l.61,125). O módulo vivo
  **não** ressuscita SES: vive só escola×região×nota. Nenhum doc sugere reabertura da análise SES em 2024+.
- **Rastreabilidade do módulo vivo sem órfão:** O7 (PRD l.23) → RF-15/RF-16 (l.68-69) + RNF-07 (l.78) →
  EP-07 (l.90) → US-20→US-21→US-22→US-23 (backlog l.442-528) → TASKS (l.128-149). Integração: US-14 (task
  de documentar ingestão no README, l.380) e US-15 (filtro de ano comporta edição viva, l.408). Completa.
- **Gaps conhecidos documentados (não resolvidos — confirmado):** (a) cadência da ingestão manual vs.
  automatizada — MVP manual assumido (PRD Gap l.11 + Premissa l.94; backlog l.49-52); (b) datas P2/P3
  SIGAA; (c) compatibilidade dos headers RESULTADOS 2024 vs. 2022–2023 (PRD Risco l.106; backlog l.53-57;
  US-20/US-23 tratam alinhamento como passo explícito). Todos roteados ao gate/build, nenhum falsamente fechado.
- **Fato confirmado (não é gap):** RESULTADOS_2024.csv + PARTICIPANTES_2024 já em disco — a prova de
  conceito da US-23 é factível com dado real (backlog l.7,438-440; US-23 l.515).

## Achados
1. **[Aviso · dono: PM]** seam A/B — Cadência do módulo vivo (manual vs. automatizada) é Premissa, não
   fato. O MVP assume **ingestão manual de 1 CSV RESULTADOS** com 2024 como prova de conceito (PRD l.11,94).
   Se o professor esperar automação (pull/agendamento do INEP), EP-07 amplia de escopo. Honestamente
   sinalizado em todos os docs. Correção esperada: confirmar a expectativa no gate; se for automação, re-rodar `/app-stories` para EP-07.
2. **[Aviso · dono: PM]** seam B — Compatibilidade dos headers de RESULTADOS 2024 com 2022–2023 NÃO foi
   confirmada. US-20 assume que escola+nota coabitam em RESULTADOS e que a codificação é alinhável; se a
   validação na build divergir, US-20 vira reconciliação de schema (pode subir de estimativa). Risco residual:
   edição futura pode remover escola de RESULTADOS, encerrando o módulo vivo. Correção esperada: validar headers reais na 1ª task de US-20/US-23; nenhuma mudança de doc necessária agora.
3. **[Aviso · dono: PM]** seam A/B — A repriorização do dashboard P1→P0 (EP-06) é Premissa do PM contra o
   "peso igual dashboard/relatório" do briefing (l.46). Defensável (face usável exigida pelo professor) e
   sinalizada (PRD l.93). Correção esperada: confirmar com a dupla no gate; se discordarem, reclassificar EP-06.
4. **[Aviso · dono: PM]** seam B — Alvo do modelo P4 (`y` = nota média vs. nota por área) e variáveis
   exatas ainda são Premissa (PRD l.96), mitigado pela US-09 que fecha cedo dentro de EP-03. Correção esperada: priorizar US-09 logo após US-03; nenhuma mudança de doc.
5. **[Aviso · dono: PM]** seam A — Datas oficiais de P2/P3 (SIGAA, PSAE00263-T01) indefinidas; backlog
   ordenado por prioridade, não por data. Documentado em todos os docs. Correção esperada: confirmar o cronograma SIGAA antes do `/app-build`.

## Análise crítica
**Riscos por épico**
- **EP-01:** técnico — CSVs ~1,7 GB/edição; risco de memória. Mitigado por RNF-02 + `usecols`/`dtype`/chunking (US-01). Residual baixo.
- **EP-02:** técnico — comparabilidade 2022↔2023 pode contaminar a variação de P2. US-02 valida antes de unificar — adequado.
- **EP-02b:** negócio — o achado depende de correção factual contra o `Leia_Me_Enem_2024.pdf`. Parafrasear de memória derruba a defensabilidade do diferencial. Mitigado por RNF-04 + revisão cruzada. Risco mais afiado do projeto.
- **EP-03:** negócio — R²≈0,30 pode ser lido como "modelo fraco"; US-10 já exige comunicá-lo como limitação legítima.
- **EP-04:** operacional — US-11 a 8 pts (teto INVEST) concentra P1–P5 + modelo + seção 2024; backlog já prevê fatiar a redação da governança se inchar. Vigiar no build.
- **EP-06:** baixo — dashboard bem delimitado; agora P0 (face usável), carrega a integração da edição viva (US-15/US-22).
- **EP-07:** técnico/operacional — o mais frágil: repousa em (a) cadência manual não confirmada e (b) compatibilidade de schema de RESULTADOS 2024 não validada. Mitigado por US-20 (alinhamento como passo explícito) e pelo dado já em disco (US-23 executável).

**Devil's advocate**
- **Causa mais provável de fracasso:** EP-02b factualmente impreciso (perde o diferencial) OU EP-07 quebrar na validação de headers de 2024 e virar reconciliação de schema sob prazo apertado.
- **Requisito mais arriscado / mal definido:** RF-15/US-20 — carregador parametrizável sob a suposição não validada de compatibilidade de schema de RESULTADOS 2024.
- **Suposição mais frágil do PRD:** que escola+nota coabitam em RESULTADOS 2024 com codificação alinhável a 2022–2023 (a aposta inteira do módulo vivo).
- **Backlog resolve o problema certo?** Sim. O módulo vivo é honesto, não "teatro de produto": ele só promete o que o dado permite (escola×região×nota via RESULTADOS, eixos que comprovadamente sobrevivem à quebra) e prova com 2024 real em disco — não simula usabilidade onde ela é impossível. A fronteira SES-impossível resistiu à tentação de marketing ("produto que nunca morre"): nenhum doc estica o módulo vivo para reabrir SES. É um add-on de escopo restrito mas factível, não frágil por desonestidade — frágil só na dependência técnica (schema), que está documentada.
- **Complexidade desnecessária a cortar antes do build?** Nenhuma a cortar — mas vigiar: se a validação de headers de 2024 mostrar reconciliação pesada de schema, o MVP do módulo vivo deve ficar na prova de conceito (US-23) e não buscar generalidade prematura para "qualquer edição futura". US-19 segue corretamente não semeada.

## Próximo passo
- **APROVADO** → governança fechada; projeto pronto para desenvolvimento (`/app-build`).
  Recomendação operacional (não-bloqueante): no gate, fechar os 5 avisos — confirmar a cadência do
  módulo vivo (manual vs. automatizada), confirmar a repriorização do dashboard com a dupla, e validar
  os headers reais de RESULTADOS 2024 cedo (US-20/US-23). Nenhum exige re-rodar `/app-prd` ou `/app-stories`
  hoje — só a cadência automatizada, se confirmada, reabriria `/app-stories` para EP-07.
