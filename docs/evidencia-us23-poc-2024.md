# Evidência — US-23: PoC de ingestão RESULTADOS 2024 (módulo vivo)

> Prova de conceito do módulo vivo (EP-07): ingerir uma edição nova do ENEM
> nos eixos que sobrevivem à quebra de linkage 2024 — P2 (escola×nota) e
> P3 (região×nota) — via `RESULTADOS`, sem reprocessar o núcleo SES.

## Ressalva de amostra (IMPORTANTE)

A PoC foi executada com `--nrows 200000` por edição (amostra, **não** a base
inteira). Os números de P2/P3 abaixo — inclusive 2024 — são **indicativos da
mecânica de ingestão, não estimativas definitivas**. Para números finais,
rodar sem `--nrows` (base completa). A US-23 prova que a rotina ingere uma
edição nova ponta a ponta, não publica métricas oficiais.

## Como foi rodado

```bash
# US-20 → US-21 para 2024 (amostra)
python -m src.enem.modulo_vivo_metricas --ano 2024 --nrows 200000

# US-22: consolida 2022+2023+2024 e grava o parquet vivo
python -m src.enem.modulo_vivo_metricas --atualizar --nrows 200000
```

Saída consolidada: `data/processado/modulo_vivo_p2_p3.parquet` (42 linhas, anos
2022 + 2023 + 2024).

## Divergência de header tratada (2024 vs. 2022–2023)

A coluna de escola muda entre edições — tratado como passo explícito em
`modulo_vivo.py` (`_detectar_divergencias`), não silenciado:

| Edição | Coluna escola | Domínio | Normalização aplicada |
|--------|---------------|---------|------------------------|
| 2022/2023 | `TP_ESCOLA` | {1,2,3} = Nao informado / Publica / Privada | direto |
| 2024 | `TP_DEPENDENCIA_ADM_ESC` | {1,2,3,4} = Federal / Estadual / Municipal / Privada | Fed+Est+Mun → "Publica"; 4 → "Privada"; NaN → "Nao informado" |

A granularidade administrativa de 2024 (Federal/Estadual/Municipal) é perdida na
normalização para o eixo binário pública×privada — registrado, não descartado em
silêncio.

## Resultado — P2/P3 lado a lado (amostra de 200k linhas/edição)

| ano | p2_gap | p2_media_publica | p2_media_privada | p3_gap | p3_media_nordeste | p3_media_sul_sudeste |
|-----|--------|------------------|------------------|--------|-------------------|----------------------|
| 2022 | 78.2 | 499.1 | 577.3 | 31.2 | 502.9 | 534.1 |
| 2023 | 82.4 | 500.0 | 582.4 | 31.3 | 502.8 | 534.1 |
| 2024 | 86.7 | 487.5 | 574.2 | 34.5 | 497.5 | 532.0 |

Na amostra, gap de escola e gap regional ambos crescem em 2024 — tendência
**não** extrapolável sem rodar a base inteira (ver ressalva acima).

Proporção "Nao informado" em P2-2024 = 60,1% dos presentes — coerente com 2022
(58,0%) e 2023 (55,5%) e com o achado de `tipo-escola-nao-informado-real`.

## Isolamento do núcleo SES (RNF-07) — confirmado

- `modulo_vivo.py` e `modulo_vivo_metricas.py` **não** importam `carga`,
  `tratamento` nem `eda` (só reaproveitam a constante estática `MAPA_UF_REGIAO`).
- O parquet SES `data/processado/enem_2022_2023.parquet` **não** foi modificado
  por esta execução (mtime anterior à corrida da PoC).
