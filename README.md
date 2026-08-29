# Gender Bias PMI — ERAMIA 2026

Este repositório reúne os códigos, dados auxiliares e arquivos intermediários utilizados no estudo **“Investigando viés de gênero em letras de músicas brasileiras”**, desenvolvido para o ERAMIA 2026.

O trabalho investiga diferenças nas associações contextuais de referentes femininos e masculinos em letras de músicas brasileiras utilizando **Pointwise Mutual Information (PMI)**.

A análise é realizada sobre o **corpus completo de 146.023 músicas** e, separadamente, sobre os cinco gêneros musicais mais frequentes da base:

- Sertanejo: 34.172 músicas
- MPB: 20.277 músicas
- Forró: 13.717 músicas
- Pagode: 9.485 músicas
- Funk: 6.974 músicas

Dessa forma, são considerados o comportamento geral do corpus e os padrões observados individualmente em cada um dos cinco recortes musicais.

---

## Metodologia

A análise utiliza conjuntos de **alvos** femininos e masculinos e seis categorias de **atributos**:

- Agradável
- Desagradável
- Aparência
- Inteligência
- Força
- Fraqueza

Os alvos correspondem a termos que representam referentes femininos ou masculinos nas letras.

Como a lista utilizada por Chen et al. (2025) foi originalmente construída para letras em inglês, sua tradução não contempla integralmente formas coloquiais, expressões culturais e variações lexicais características do português brasileiro.

Por esse motivo, os alvos utilizados neste trabalho combinam:

1. termos traduzidos de Chen et al. (2025);
2. candidatos identificados nas frases predicativas de Lopes et al. (2025);
3. nomes próprios provenientes do ranking de nomes do Censo 2022 do IBGE;
4. expansões manuais de gênero, número, aumentativo e diminutivo.

A versão final utilizada na análise possui:

- **1.569 alvos**
  - 759 femininos
  - 810 masculinos

Entre esses alvos, **1.367 são nomes próprios provenientes do IBGE**:

- 658 femininos
- 709 masculinos

Os atributos totalizam **421 termos**, distribuídos entre as seis categorias semânticas utilizadas na análise.

---

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

---

# Scripts

## `nomes_ibge_2022.py`

Obtém os **1.000 nomes femininos e os 1.000 nomes masculinos mais frequentes** segundo o ranking de nomes do Censo 2022 do IBGE.

O script também verifica a presença desses nomes no corpus de letras.

O arquivo gerado por essa etapa está disponível em:

```text
dados_auxiliares/1000_nomes_femininos_1000_masculinos_ibge.csv
```

Esse arquivo contém os 2.000 candidatos obtidos do ranking do IBGE antes da consolidação da lista final de alvos.

---

## `preprocessar_frases_lopes.py`

Realiza o pré-processamento das frases predicativas provenientes do trabalho de Lopes et al. (2025).

Lopes et al. desenvolveram **120 padrões de busca** para localizar, no corpus de letras, sentenças que qualificassem referentes femininos ou masculinos.

Esses padrões combinam elementos como:

- sujeitos e nomes próprios;
- verbos auxiliares;
- advérbios;
- determinantes;
- adjetivos;
- substantivos.

Neste trabalho, as frases recuperadas por esses padrões foram reutilizadas como fonte de candidatos a novos alvos e atributos.

O pré-processamento inclui:

- remoção de AUX, ADV, DET e PRONOUN conforme a estrutura do padrão;
- remoção de números, pontuação e caracteres especiais;
- remoção de letras isoladas;
- aplicação de stopwords do NLTK;
- aplicação de stopwords do spaCy;
- aplicação do ISO Stopwords Project;
- aplicação de listas adicionais de exclusão;
- remoção de termos já contemplados pela tradução de Chen et al. (2025);
- remoção de registros vazios;
- remoção de frases duplicadas.

O conjunto utilizado nesta etapa foi reduzido de **31.183 para 9.116 frases**, posteriormente destinadas à inspeção de novos alvos e atributos.

O resultado está disponível em:

```text
dados_auxiliares/df_uniao_limpo_lopes_4.csv
```

---

## `01_preprocessamento.py`

Realiza o pré-processamento do corpus de letras musicais e cria os recortes utilizados na análise.

O corpus original de Lopes et al. (2025) possui **146.612 músicas**.

Nesta etapa são realizadas operações como:

- normalização textual;
- conversão do conteúdo para letras minúsculas;
- limpeza das letras;
- remoção de registros duplicados;
- separação dos cinco gêneros musicais mais frequentes.

Foram removidas **589 músicas duplicadas**, considerando título, artista e gênero musical, resultando em um corpus geral de:

**146.023 músicas**

A partir desse corpus são produzidos os recortes:

| Recorte | Número de músicas |
|---|---:|
| Corpus completo | 146.023 |
| Sertanejo | 34.172 |
| MPB | 20.277 |
| Forró | 13.717 |
| Pagode | 9.485 |
| Funk | 6.974 |

Os cinco recortes por gênero disponíveis no repositório estão em:

```text
dados_processados/
```

O arquivo correspondente ao corpus completo também é produzido pelo script, mas não foi incluído no GitHub devido ao seu tamanho.

---

## `02_substituir_alvos.py`

Substitui, nas letras, os termos identificados como alvos por suas respectivas classificações utilizadas posteriormente no cálculo da PMI.

As oito classificações utilizadas são:

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

Os **1.569 alvos utilizados na análise estão codificados diretamente no script**.

Por esse motivo, essa etapa não depende de uma planilha externa para localizar ou classificar os alvos.

Os arquivos gerados estão disponíveis em:

```text
dados_substituidos/
```

Por exemplo:

```text
dados_processados/sertanejo_pmi.csv
```

é transformado em:

```text
dados_substituidos/sertanejo_pmi_substituido.csv
```

---

## `03_calcular_pmi_contexto_2.py`

Realiza o cálculo da **Pointwise Mutual Information (PMI)** entre os conjuntos de referentes femininos e masculinos e as seis categorias de atributos.

São consideradas as categorias:

```text
Agradável
Desagradável
Aparência
Inteligência
Força
Fraqueza
```

Os **421 atributos utilizados na análise estão codificados diretamente neste script**.

A análise utiliza uma janela contextual de dois tokens anteriores e dois posteriores a cada ocorrência de alvo:

```text
token -2 | token -1 | ALVO | token +1 | token +2
```

O próprio alvo é retirado do contexto utilizado para a contagem.

Os contextos e atributos são processados com o modelo em português:

```text
pt_core_news_sm
```

do spaCy.

A PMI é calculada individualmente para cada atributo. Em seguida, os valores dos atributos pertencentes à mesma categoria são agregados pela média.

O script executa a análise tanto para:

- o corpus completo;
- sertanejo;
- MPB;
- forró;
- pagode;
- funk.

---

# Dados auxiliares

## `1000_nomes_femininos_1000_masculinos_ibge.csv`

Contém os:

- 1.000 nomes femininos mais frequentes;
- 1.000 nomes masculinos mais frequentes;

obtidos a partir do ranking de nomes do Censo 2022 do IBGE.

O arquivo registra também a presença dos nomes no corpus de letras.

Após o cruzamento com o corpus, a consolidação e a remoção de ambiguidades, **1.367 nomes próprios** integram a lista final de alvos:

- 658 femininos;
- 709 masculinos.

---

## `df_uniao_limpo_lopes_4.csv`

Contém as **9.116 frases predicativas** resultantes do pré-processamento realizado sobre o conjunto utilizado a partir de Lopes et al. (2025).

Essas frases foram utilizadas para a inspeção de candidatos a novos alvos e atributos.

---

## `eramia_pmi_atributos_alvos.xlsx`

Contém a versão consolidada das listas de alvos e atributos utilizadas no estudo.

A planilha possui:

- **1.569 alvos**
- **421 atributos**

Os alvos estão distribuídos nas classificações:

| Classificação | Feminino | Masculino | Total |
|---|---:|---:|---:|
| nomes | 658 | 709 | 1.367 |
| similares | 44 | 50 | 94 |
| família | 41 | 37 | 78 |
| outros | 16 | 14 | 30 |
| **Total** | **759** | **810** | **1.569** |

Os atributos estão distribuídos da seguinte forma:

| Categoria | Total |
|---|---:|
| Agradável | 106 |
| Desagradável | 139 |
| Aparência | 70 |
| Inteligência | 35 |
| Força | 37 |
| Fraqueza | 34 |
| **Total** | **421** |

As listas presentes nessa planilha correspondem às listas codificadas nos scripts utilizados na execução final.

---

# Dados processados

A pasta:

```text
dados_processados/
```

contém os cinco recortes por gênero musical após a etapa inicial de pré-processamento:

```text
forro_pmi.csv
funk_pmi.csv
mpb_pmi.csv
pagode_pmi.csv
sertanejo_pmi.csv
```

Esses arquivos ainda apresentam os alvos em sua forma textual original.

---

# Dados com alvos substituídos

A pasta:

```text
dados_substituidos/
```

contém os cinco recortes após a substituição dos alvos por suas classificações de gênero:

```text
forro_pmi_substituido.csv
funk_pmi_substituido.csv
mpb_pmi_substituido.csv
pagode_pmi_substituido.csv
sertanejo_pmi_substituido.csv
```

Esses arquivos constituem as entradas utilizadas pelo script de cálculo da PMI para os cinco gêneros musicais.

---

# Corpus completo

Embora o estudo também analise o **corpus completo de 146.023 músicas**, seus arquivos intermediários não estão armazenados neste repositório devido ao tamanho.

Os arquivos produzidos localmente são:

```text
merged_df_pmi.csv
merged_df_pmi_substituido.csv
```

O primeiro corresponde ao corpus completo após o pré-processamento.

O segundo corresponde ao mesmo corpus após a substituição dos alvos pelas classificações utilizadas na PMI.

Ambos são gerados pelos mesmos scripts disponibilizados neste repositório.

Portanto, a ausência desses dois arquivos no GitHub **não significa que o corpus completo tenha sido excluído da análise**. Os resultados do estudo consideram:

```text
Corpus completo
+ Sertanejo
+ MPB
+ Forró
+ Pagode
+ Funk
```

---

# Fluxo principal da análise

O pipeline principal pode ser representado da seguinte forma:

```text
Corpus original
146.612 músicas
        │
        ▼
01_preprocessamento.py
        │
        ├── Corpus completo: 146.023 músicas
        │
        ├── Sertanejo
        ├── MPB
        ├── Forró
        ├── Pagode
        └── Funk
        │
        ▼
02_substituir_alvos.py
        │
        ▼
Substituição dos 1.569 alvos
pelas classificações PMI
        │
        ▼
03_calcular_pmi_contexto_2.py
        │
        ▼
PMI por categoria
para feminino e masculino
        │
        ▼
Resultados para:
Corpus completo + 5 gêneros musicais
```

Os scripts:

```text
nomes_ibge_2022.py
preprocessar_frases_lopes.py
```

correspondem a etapas auxiliares utilizadas durante a construção e validação dos conjuntos lexicais.

---

# Dependências

O projeto utiliza Python e, entre outras, as seguintes bibliotecas:

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

As principais dependências podem ser instaladas com:

```bash
pip install pandas numpy matplotlib spacy nltk stopwordsiso requests selenium
```

Também é necessário instalar o modelo de português do spaCy:

```bash
python -m spacy download pt_core_news_sm
```

---

# Caminhos dos arquivos

Os scripts foram desenvolvidos para execução local.

Alguns códigos utilizam caminhos definidos no início do arquivo, por exemplo:

```python
PASTA = Path(r"D:\Downloads")
```

Antes de executar o projeto em outro computador, esses caminhos devem ser ajustados para o local em que os arquivos estiverem armazenados.

---

# Referências principais

- Betti, L., Abrate, C. e Kaltenbrunner, A. (2023). *Large scale analysis of gender bias and sexism in song lyrics*. EPJ Data Science.

- Chen, D. et al. (2025). *Tuning into Bias: A Computational Study of Gender Bias in Song Lyrics*. LaTeCH-CLfL 2025.

- Lopes, J. N. S., Firmino, V. P. e Reis, V. Q. (2025). *Muses or Stereotypes? Identifying Historical Patterns of Sexism in a Corpus of Brazilian Lyrics*. Journal on Interactive Systems.

- Stanczak, K. e Augenstein, I. (2021). *A Survey on Gender Bias in Natural Language Processing*.



Este repositório disponibiliza os materiais computacionais e dados derivados utilizados no estudo sobre **viés de gênero em letras de músicas brasileiras por meio de PMI**, considerando conjuntamente o corpus completo e análises específicas dos gêneros sertanejo, MPB, forró, pagode e funk.
