# Roteiro de Apresentação — Entrega 1

**Projeto:** Análise dos Microdados do ENEM — Desigualdade Socioeconômica e Desempenho
**Equipe:** Augusto Blois · Pedro Flávio
**Duração-alvo:** 10 minutos · 7 slides
**Divisão:** Augusto slides 1–4 · Pedro slides 5–7

> Tópicos exigidos pela banca: **1. Problema → Objetivo (Central + Específicos) · 2. Público-alvo · 3. Valor · 4. Viabilidade.**
> Slides no projetor = pouco texto. As notas abaixo são o que vocês **falam**, não o que aparece na tela.

---

## Slide 1 — Capa + Gancho · *Augusto* · ~30s

**Na tela:** título, equipe, disciplina, instituição.

**Fala (gancho — não escrever no slide):**
> "O ENEM tem mais de 3 milhões de inscritos por edição. É a maior porta de entrada pro ensino superior no Brasil. Mas uma pergunta fica: quem realmente passa?"

Objetivo: prender atenção antes do conteúdo.

---

## Slide 2 — Problema · *Augusto* · ~1min30 · (Tópico 1)

**Na tela:**
- Frase central grande: **"A educação brasileira reproduz desigualdade estrutural."**
- Quem sistematicamente vence:
  - Maior renda familiar
  - Filhos de pais com ensino superior
  - Escola privada / região mais rica

**Fala:**
> "Candidatos de maior renda, de escola privada, de regiões ricas superam os demais de forma sistemática. O problema: a magnitude exata dessas diferenças, como variam no tempo e quais fatores mais explicam seguem pouco explorados de forma integrada e visual. É esse buraco que o projeto preenche."

**Por quê o slide:** justifica a existência do projeto. A banca precisa sentir o problema antes da solução.

---

## Slide 3 — Objetivo Central + Específicos · *Augusto* · ~1min30 · (Tópico 1)

**Na tela — Objetivo Central (1 frase):**
> Quantificar, visualizar e comunicar as disparidades socioeconômicas no desempenho do ENEM, identificando quais variáveis mais influenciam — com atenção especial ao Nordeste.

**Na tela — Objetivos Específicos (as 5 perguntas viram verbo de ação):**
1. Medir a relação renda × nota nas 5 áreas
2. Quantificar o gap escola pública vs. privada (2022 vs. 2023)
3. Testar a disparidade regional NE vs. Sul/Sudeste, controlando renda e tipo de escola
4. Modelar os preditores combinados (meta R² ≥ 0,30)
5. Traçar o perfil da nota 1000 em Redação

**Fala:**
> "O objetivo central se desdobra em cinco perguntas analíticas testáveis. Cada uma vira um objetivo específico com critério verificável — não é objetivo vago, é hipótese mensurável."

**Por quê:** mostra rigor. Numa banca de análise de dados, objetivo testável vale ouro.

---

## Slide 4 — Público-alvo · *Augusto* · ~1min15 · (Tópico 2)

**Na tela — tabela enxuta:**

| Perfil | Uso do produto |
|---|---|
| Gestor de política educacional (MEC, secretarias) | Priorizar regiões e perfis para intervenção |
| Pesquisador / docente | Base analítica sobre desigualdade escolar |
| Equipe pedagógica (escola pública) | Contextualizar desempenho vs. perfil socioeconômico |
| Jornalista de dados | Narrativas visuais sobre equidade |

**Fala — destacar o tomador primário:**
> "O tomador de decisão primário é o gestor de política pública educacional: alguém que precisa de evidência quantitativa pra priorizar investimento e ação afirmativa."

**Por quê:** projeto bom tem dono. Dizer quem decide com o resultado = valor real, não exercício solto.

---

## Slide 5 — Valor · *Pedro* · ~1min30 · (Tópico 3)

**Na tela — dois entregáveis:**
- **Dashboard interativo (Streamlit):** filtros por ano/UF/escola/renda · mapa coroplético por estado · comparações entre grupos · correlação renda × nota.
- **Relatório técnico (PDF):** respostas às 5 perguntas · resultado do modelo preditivo (R², MAE) · conclusões e limitações.

**Fala:**
> "O valor está em transformar gigabytes de microdados brutos em evidência visual que o gestor usa pra agir. Dois entregáveis complementares: um dashboard pra explorar e um relatório que fecha as respostas com método."

**Por quê:** valor = ponte entre dado e decisão. Mostrem o produto, não só o método.

---

## Slide 6 — Viabilidade · *Pedro* · ~1min30 · (Tópico 4)

**Na tela:**
- **Dados:** Microdados ENEM (INEP) — públicos, irrestritos, sem autenticação. Risco de indisponibilidade: nulo.
- **Edições:** 2022 + 2023 (~2–4 GB cada).
- **Stack:** Python · pandas · scikit-learn · Streamlit.
- **Plano em 6 semanas:** Extração → Tratamento → EDA → Modelagem → Visualização → Entrega.

**Fala:**
> "É executável. Os dados são públicos, documentados, com histórico de disponibilidade ininterrupta. A stack é a que dominamos, e o plano cabe em seis semanas, etapa a etapa."

**Por quê:** viabilidade = "isso entrega no prazo". Dado acessível + plano com etapas + ferramenta dominada.

---

## Slide 7 — Fecho · *Pedro* · ~45s

**Na tela — recap de 1 linha por bloco:**
- Problema: desigualdade estrutural pouco medida de forma integrada
- Objetivo: quantificar, visualizar, comunicar
- Quem usa: gestor de política pública
- Valor: dado bruto → evidência acionável
- Viável: dados públicos + 6 semanas

**Fala — frase final:**
> "Desigualdade educacional medida, mapeada e comunicada — pronta pra virar política. Perguntas?"

---

## Reserva (se a banca perguntar) — Hipóteses

Não vão no slide. Tenham na manga:
- **P1 renda × nota:** relação positiva, retornos decrescentes acima de 5 SM; efeito maior em Matemática que em Redação.
- **P2 gap escola:** 80–120 pontos, estável entre 2022 e 2023.
- **P3 região:** disparidade existe, mas efeito residual < 30 pontos ao controlar renda+escola.
- **P4 preditores:** renda e tipo de escola os mais fortes; escolaridade dos pais contribui; R² ≥ 0,30.
- **P5 nota 1000 Redação:** concentra escola privada + renda > 3 SM, mas com mais diversidade regional que o alto desempenho geral.

---

## Checklist pré-apresentação
- [ ] Ensaiar cronometrado pelo menos 1x (10 min estoura fácil)
- [ ] Definir quem clica os slides
- [ ] Slides com pouco texto — a fala carrega o conteúdo
- [ ] Saber de cor o objetivo central e o tomador de decisão primário
- [ ] Hipóteses na cabeça para perguntas
