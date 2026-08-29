# Gender Bias PMI-ERAMIA-2026


# Gender Bias PMI — ERAMIA 2026

Repositório com códigos, dados auxiliares e arquivos intermediários utilizados no trabalho **“Investigando viés de gênero em letras de músicas brasileiras”**, desenvolvido para o ERAMIA 2026.

O estudo investiga diferenças nas associações contextuais de referentes femininos e masculinos em letras de músicas brasileiras utilizando **Pointwise Mutual Information (PMI)**.

A análise considera o corpus geral e os cinco gêneros musicais mais frequentes da base:

- Sertanejo
- MPB
- Forró
- Pagode
- Funk

## Metodologia

A análise utiliza conjuntos de **alvos** femininos e masculinos e seis categorias de **atributos**:

- Agradável
- Desagradável
- Aparência
- Inteligência
- Força
- Fraqueza

Os conjuntos lexicais foram construídos a partir de três fontes principais:

1. termos traduzidos e adaptados de Chen et al. (2025);
2. candidatos extraídos das frases predicativas identificadas por Lopes et al. (2025);
3. nomes próprios provenientes do ranking de nomes do Censo 2022 do IBGE.

A lista foi ampliada para contemplar melhor formas coloquiais, expressões culturais e variações lexicais características do português brasileiro.

A versão final contém:

- **1.569 alvos**
  - 759 femininos
  - 810 masculinos
- **421 atributos**

Entre os alvos, **1.367 são nomes próprios provenientes do IBGE**, sendo 658 femininos e 709 masculinos.

## Estrutura do repositório

```text
.
├── scripts/
│   ├── nomes_ibge_2022.py
│   ├── preprocessar_frases_lopes.py
│   ├── 01_preprocessamento.py
│   ├── 02_substituir_alvos.py
│   └── 03_calcular_pmi_contexto_2.py
│
├── dados_auxiliares/
│   ├── 1000_nomes_femininos_1000_masculinos_ibge.csv
│   ├── df_uniao_limpo_lopes_4.csv
│   └── eramia_pmi_atributos_alvos.xlsx
│
├── dados_processados/
│   ├── forro_pmi.csv
│   ├── funk_pmi.csv
│   ├── mpb_pmi.csv
│   ├── pagode_pmi.csv
│   └── sertanejo_pmi.csv
│
└── dados_substituidos/
    ├── forro_pmi_substituido.csv
    ├── funk_pmi_substituido.csv
    ├── mpb_pmi_substituido.csv
    ├── pagode_pmi_substituido.csv
    └── sertanejo_pmi_substituido.csv
```

## Scripts

### `nomes_ibge_2022.py`

Obtém os **1.000 nomes femininos e 1.000 nomes masculinos mais frequentes** segundo o ranking do Censo 2022 do IBGE.

O script também verifica quais desses nomes estão presentes no corpus de letras.

O resultado correspondente está disponível em:

```text
dados_auxiliares/1000_nomes_femininos_1000_masculinos_ibge.csv
```

### `preprocessar_frases_lopes.py`

Realiza o pré-processamento das frases predicativas derivadas de Lopes et al. (2025).

Lopes et al. desenvolveram **120 padrões de busca** para localizar sentenças que qualificam referentes femininos ou masculinos em letras de músicas brasileiras.

Nesta etapa são realizadas, entre outras operações:

- remoção de AUX, ADV, DET e PRONOUN conforme os padrões;
- remoção de pontuação, números e caracteres especiais;
- aplicação de stopwords do NLTK, spaCy e ISO Stopwords;
- aplicação de listas adicionais de exclusão;
- remoção de termos já contemplados pela lista traduzida de Chen et al. (2025);
- remoção de registros vazios e frases duplicadas.

O processamento utilizado neste estudo resulta em **9.116 frases** destinadas à inspeção de novos alvos e atributos.

Arquivo correspondente:

```text
dados_auxiliares/df_uniao_limpo_lopes_4.csv
```

### `01_preprocessamento.py`

Realiza o pré-processamento do corpus de letras.

Entre as principais operações estão:

- normalização textual;
- conversão para letras minúsculas;
- remoção de caracteres não alfabéticos;
- remoção de músicas duplicadas;
- criação dos recortes por gênero musical.

O corpus original possui **146.612 músicas**. Após a remoção de 589 registros duplicados, são mantidas **146.023 músicas**.

Também são produzidos os recortes:

| Gênero | Músicas |
|---|---:|
| Sertanejo | 34.172 |
| MPB | 20.277 |
| Forró | 13.717 |
| Pagode | 9.485 |
| Funk | 6.974 |

Os arquivos desses recortes estão em:

```text
dados_processados/
```

### `02_substituir_alvos.py`

Substitui os alvos encontrados nas letras por suas respectivas classificações utilizadas no cálculo da PMI.

As classificações são:

```text
ela_similares
ele_similares
familia_fem
familia_masc
nome_fem
nome_masc
outros_fem
outros_masc
```

Os **1.569 alvos estão codificados diretamente no script**, portanto essa etapa não depende de uma planilha externa para execução.

Os arquivos resultantes estão em:

```text
dados_substituidos/
```

### `03_calcular_pmi_contexto_2.py`

Calcula a **Pointwise Mutual Information (PMI)** entre os conjuntos de alvos femininos e masculinos e as seis categorias de atributos.

A análise utiliza uma janela de contexto de:

```text
2 tokens anteriores + alvo + 2 tokens posteriores
```

O alvo é removido do contexto antes da contagem.

Os atributos são lematizados utilizando:

```text
spaCy: pt_core_news_sm
```

Os **421 atributos utilizados na análise estão codificados diretamente neste script**.

A PMI é calculada inicialmente para cada atributo e, posteriormente, os resultados são agregados pela média de cada categoria.

## Lista consolidada de alvos e atributos

O arquivo:

```text
dados_auxiliares/eramia_pmi_atributos_alvos.xlsx
```

contém a versão consolidada das listas utilizadas no estudo.

Ele possui:

- **1.569 alvos**
- **421 atributos**

Os valores dessa planilha correspondem às listas codificadas nos scripts utilizados na análise final.

## Arquivos processados e substituídos

A pasta:

```text
dados_processados/
```

contém as letras após o pré-processamento e separação dos cinco gêneros musicais analisados.

A pasta:

```text
dados_substituidos/
```

contém os mesmos recortes após a substituição dos alvos por suas classificações PMI.

Por exemplo:

```text
sertanejo_pmi.csv
```

é transformado em:

```text
sertanejo_pmi_substituido.csv
```

antes do cálculo da PMI.

## Corpus geral

Os arquivos intermediários correspondentes ao **corpus completo de 146.023 músicas** não estão armazenados neste repositório devido ao seu tamanho.

São eles:

```text
merged_df_pmi.csv
merged_df_pmi_substituido.csv
```

Esses arquivos são gerados localmente pelos mesmos scripts utilizados para produzir os recortes por gênero.

Os códigos permanecem preparados para executar tanto a análise do corpus completo quanto a dos cinco gêneros musicais.

## Ordem de execução

Para reproduzir o fluxo principal da análise:

```text
Corpus original
      ↓
01_preprocessamento.py
      ↓
dados_processados/
      ↓
02_substituir_alvos.py
      ↓
dados_substituidos/
      ↓
03_calcular_pmi_contexto_2.py
      ↓
Resultados de PMI
```

Os scripts `nomes_ibge_2022.py` e `preprocessar_frases_lopes.py` correspondem às etapas auxiliares utilizadas durante a construção das listas de alvos e atributos.

## Dependências

O projeto utiliza Python e as seguintes bibliotecas principais:

```text
pandas
numpy
matplotlib
spacy
nltk
stopwordsiso
requests
selenium
```

Instalação das bibliotecas:

```bash
pip install pandas numpy matplotlib spacy nltk stopwordsiso requests selenium
```

Instalação do modelo de português do spaCy:

```bash
python -m spacy download pt_core_news_sm
```

## Observação sobre os caminhos dos arquivos

Os scripts foram desenvolvidos para execução local e alguns deles utilizam caminhos definidos no início do código, como:

```python
PASTA = Path(r"D:\Downloads")
```

Antes da execução em outro computador, esses caminhos devem ser ajustados para o diretório onde os dados estiverem armazenados.

## Referências principais

- Betti, L., Abrate, C. e Kaltenbrunner, A. (2023). *Large scale analysis of gender bias and sexism in song lyrics*. EPJ Data Science.
- Chen, D. et al. (2025). *Tuning into Bias: A Computational Study of Gender Bias in Song Lyrics*. LaTeCH-CLfL 2025.
- Lopes, J. N. S., Firmino, V. P. e Reis, V. Q. (2025). *Muses or Stereotypes? Identifying Historical Patterns of Sexism in a Corpus of Brazilian Lyrics*. Journal on Interactive Systems.
- Stanczak, K. e Augenstein, I. (2021). *A Survey on Gender Bias in Natural Language Processing*.


Este repositório contém os materiais utilizados no artigo submetido ao **ERAMIA 2026** sobre análise de viés de gênero em letras de músicas brasileiras por meio de PMI.
