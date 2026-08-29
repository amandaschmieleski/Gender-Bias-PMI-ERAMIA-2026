from __future__ import annotations

import math
import re
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PASTA = Path(r"D:\Downloads")
PASTA_SAIDA_LOTE = PASTA / "pmi contexto 2 outputs"
PASTA_SAIDA_LOTE.mkdir(parents=True, exist_ok=True)

ARQUIVOS_ENTRADA = {
    "forro": PASTA / "forro_pmi_substituido.csv",
    "funk": PASTA / "funk_pmi_substituido.csv",
    "mpb": PASTA / "mpb_pmi_substituido.csv",
    "sertanejo": PASTA / "sertanejo_pmi_substituido.csv",
    "merged_df": PASTA / "merged_df_pmi_substituido.csv",
    "pagode": PASTA / "pagode_pmi_substituido.csv",
}

COLUNA_TEXTO = "Letra da Música"
COLUNA_MUSICA = "Nome da Música"
COLUNA_ARTISTA = "Artista"

USAR_PRIMEIRAS_N_MUSICAS = None
JANELA_CONTEXTO = 2
REMOVER_ALVO_DO_CONTEXTO = True
DEDUPLICAR_CONTEXTOS = False

EPSILON = 0.5
MIN_OCORRENCIA_ATRIBUTO = 1

MODELO_SPACY = "pt_core_news_sm"
NLP_PIPE_BATCH_SIZE = 500

ORDEM_CATEGORIAS = [
    "Agradável",
    "Desagradável",
    "Aparência",
    "Inteligência",
    "Força",
    "Fraqueza",
]

_NLP = None
_ALVOS_NORM_CACHE = None
_ATRIBUTOS_NORM_CACHE = None


def remover_acentos(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", str(texto).lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def normalizar_nome_coluna(valor) -> str:
    texto = remover_acentos(str(valor).strip().lower())
    return re.sub(r"[^a-z0-9]+", "", texto)


def achar_coluna(colunas, nomes_possiveis: str | list[str]) -> str:
    if isinstance(nomes_possiveis, str):
        nomes_possiveis = [nomes_possiveis]

    mapa = {normalizar_nome_coluna(coluna): coluna for coluna in colunas}

    for nome in nomes_possiveis:
        chave = normalizar_nome_coluna(nome)
        if chave in mapa:
            return mapa[chave]

    raise ValueError


def normalizar_alvo(texto: str) -> str:
    texto = str(texto).lower().strip()
    texto = re.sub(r"[^a-zà-öø-ÿ0-9_]", "", texto)
    return texto


def normalizar_atributo(texto: str) -> str:
    texto = remover_acentos(texto)
    texto = re.sub(r"[^a-z0-9]", "", texto)
    return texto.strip()


# -------------------------------------------------------------------------
# LISTAS CODIFICADAS NO PRÓPRIO SCRIPT
#
# ALVOS:
# Neste segundo código, os CSVs de entrada já passaram pelo script 01.
# Por isso, ele NÃO precisa das 1.569 palavras-alvo originais; ele procura
# somente as oito classificações PMI inseridas no texto pelo script 01.
#
# ATRIBUTOS:
# As 421 palavras de atributos ficam codificadas abaixo.
# -------------------------------------------------------------------------
ALVOS = {
    "Feminino": [
        "ela_similares",
        "familia_fem",
        "nome_fem",
        "outros_fem",
    ],
    "Masculino": [
        "ele_similares",
        "familia_masc",
        "nome_masc",
        "outros_masc",
    ],
}

ATRIBUTOS = {
    "Agradável": [
        "abraçar",
        "abraço",
        "adorar",
        "alegre",
        "alegria",
        "amado",
        "amar",
        "amigo",
        "amor",
        "animação",
        "anjo",
        "apaixonar",
        "apegado",
        "arco-íris",
        "bacana",
        "beijar",
        "beijo",
        "bom",
        "brilho",
        "brincalhão",
        "carinho",
        "carinhoso",
        "certo",
        "céu",
        "cheirosa",
        "companheira",
        "confiar",
        "contente",
        "coração",
        "cuidar",
        "curar",
        "curtir",
        "decente",
        "desejo",
        "deusa",
        "diamante",
        "diploma",
        "disposição",
        "doce",
        "empolgada",
        "escolhida",
        "especial",
        "espetacular",
        "estrela",
        "faceiro",
        "família",
        "famosa",
        "felicidade",
        "feliz",
        "férias",
        "fiel",
        "flor",
        "gentil",
        "honesto",
        "honra",
        "incrível",
        "inocente",
        "joia",
        "lealdade",
        "legal",
        "liberdade",
        "ligado",
        "luz",
        "maneira",
        "manso",
        "maravilha",
        "maravilhoso",
        "medicinal",
        "meigo",
        "milagre",
        "moderna",
        "nascer",
        "nascer do sol",
        "nobre",
        "ouro",
        "paixão",
        "paraíso",
        "parceiro",
        "paz",
        "perfeição",
        "perfeito",
        "prazer",
        "presente",
        "puro",
        "remédio",
        "respeito",
        "responsa",
        "rico",
        "riqueza",
        "rir",
        "riso",
        "romance",
        "saudade",
        "saúde",
        "sensacional",
        "simpatia",
        "simpático",
        "sincero",
        "sonhar",
        "sonho",
        "sorrir",
        "sorriso",
        "sorte",
        "ternura",
        "união",
        "verdadeiro",
    ],
    "Desagradável": [
        "abandonar",
        "abusar",
        "acidente",
        "agonia",
        "agressão",
        "algoz",
        "amargo",
        "assassinato",
        "assassino",
        "babaca",
        "bagaceira",
        "bagunça",
        "bandido",
        "barraqueira",
        "barreira",
        "bastardo",
        "bêbado",
        "bipolar",
        "bomba",
        "brigar",
        "burro",
        "cafajeste",
        "câncer",
        "castigo",
        "chato",
        "chifrudo",
        "chumbinho",
        "ciumenta",
        "colisão",
        "conspirador",
        "corno",
        "corrupto",
        "crime",
        "criminoso",
        "cruel",
        "delator",
        "desastre",
        "desconfiar",
        "desobediente",
        "desprezível",
        "difícil",
        "divórcio",
        "doença",
        "doer",
        "doido",
        "dor",
        "droga",
        "enganar",
        "errado",
        "esquisito",
        "exagerada",
        "fácil",
        "falso",
        "fanático",
        "fatal",
        "fedor",
        "ferir",
        "frio",
        "frustrado",
        "fuleiro",
        "fúria",
        "fútil",
        "guerra",
        "horrível",
        "hostil",
        "implicar",
        "indigesta",
        "indisciplinado",
        "infiel",
        "ingrata",
        "inimigo",
        "invejar",
        "irresponsável",
        "ladrão",
        "libidinosa",
        "ligeira",
        "lobo",
        "louco",
        "luto",
        "machucar",
        "magoar",
        "mal",
        "malandro",
        "maldosa",
        "maloqueiro",
        "maltratar",
        "maluco",
        "malvada",
        "mandona",
        "manhosa",
        "maroto",
        "matar",
        "mau",
        "mentir",
        "mentira",
        "morrer",
        "morte",
        "nojento",
        "ódio",
        "ofender",
        "patricinha",
        "perversa",
        "péssimo",
        "piranha",
        "piriguete",
        "pobre",
        "pobreza",
        "podre",
        "poluir",
        "prisão",
        "problema",
        "puta",
        "racista",
        "revoltado",
        "ruim",
        "safado",
        "sapeca",
        "sofrer",
        "sofrimento",
        "solidão",
        "soltinha",
        "sombrio",
        "sozinho",
        "sujeira",
        "terrível",
        "tormento",
        "tóxico",
        "traficante",
        "tragédia",
        "trair",
        "trapaceiro",
        "triste",
        "tristeza",
        "vacilona",
        "vagabundo",
        "veneno",
        "vômito",
        "vulgar",
        "zangado",
    ],
    "Aparência": [
        "atlético",
        "atraente",
        "baixo",
        "barbado",
        "barriga",
        "boca",
        "bombado",
        "bonito",
        "branco",
        "bumbum",
        "bundão",
        "bunduda",
        "buzanfão",
        "cabelo",
        "cabeludo",
        "calor",
        "careca",
        "cheia",
        "cheiro",
        "cigana",
        "cigano",
        "cinderela",
        "corado",
        "corpo",
        "donzela",
        "elegante",
        "estilosa",
        "excitar",
        "feio",
        "formosa",
        "franzino",
        "gata",
        "gatinha",
        "gato",
        "gordo",
        "gostoso",
        "lindo",
        "loiro",
        "magra",
        "molhada",
        "morena",
        "musa",
        "negro",
        "nua",
        "olhar",
        "olho",
        "peituda",
        "pelada",
        "pele",
        "perfume",
        "popotão",
        "pretinho",
        "preto",
        "princesa",
        "provocar",
        "quente",
        "rebolar",
        "saliente",
        "saudável",
        "sedução",
        "sedutor",
        "seduzir",
        "sensual",
        "sereia",
        "sexy",
        "simples",
        "tanajura",
        "tentação",
        "tesão",
        "turbinada",
    ],
    "Inteligência": [
        "adaptar",
        "analítico",
        "aprender",
        "apto",
        "atualizado",
        "brilhante",
        "compreender",
        "conhecer",
        "curioso",
        "educado",
        "engenhoso",
        "engraçado",
        "ensinar",
        "esperto",
        "estudar",
        "estudioso",
        "ética",
        "gênio",
        "habilidoso",
        "imaginar",
        "inteligente",
        "intuitivo",
        "inventar",
        "investigativo",
        "lógico",
        "pensar",
        "perceber",
        "ponderado",
        "potente",
        "precoce",
        "refletir",
        "sábio",
        "sagaz",
        "sensato",
        "venerável",
    ],
    "Força": [
        "afirmar",
        "alto",
        "atitude",
        "campeão",
        "comandar",
        "competidor",
        "confiança",
        "confiante",
        "consciente",
        "controle",
        "coragem",
        "destemido",
        "dominar",
        "forte",
        "grito",
        "guerreiro",
        "herói",
        "imbatível",
        "independente",
        "invencível",
        "justo",
        "líder",
        "liderança",
        "lutar",
        "maduro",
        "ousadia",
        "ousado",
        "potência",
        "proteger",
        "protetor",
        "representante",
        "resistente",
        "seguro",
        "valente",
        "vencedor",
        "vencer",
        "vitória",
    ],
    "Fraqueza": [
        "ansioso",
        "cabisbaixo",
        "carente",
        "ceder",
        "chorar",
        "covarde",
        "defeito",
        "delicado",
        "dependente",
        "deprimido",
        "derrota",
        "dificuldade",
        "doente",
        "errar",
        "fracasso",
        "fraco",
        "frágil",
        "fraqueza",
        "fudido",
        "indefeso",
        "inseguro",
        "irrelevante",
        "medo",
        "nervoso",
        "otário",
        "perdedor",
        "perder",
        "quieto",
        "recuar",
        "seguir",
        "timidez",
        "tolo",
        "tonto",
        "vulnerável",
    ],
}


def validar_listas_codificadas() -> None:
    alvos_fem = set(ALVOS["Feminino"])
    alvos_masc = set(ALVOS["Masculino"])

    colisoes_alvos = alvos_fem & alvos_masc
    if colisoes_alvos:
        raise ValueError

    todas_palavras = [
        palavra.strip().lower()
        for categoria in ORDEM_CATEGORIAS
        for palavra in ATRIBUTOS[categoria]
        if palavra.strip()
    ]

    duplicados = sorted({
        palavra
        for palavra in todas_palavras
        if todas_palavras.count(palavra) > 1
    })

    if duplicados:
        raise ValueError

    if len(todas_palavras) != 421:
        raise ValueError


validar_listas_codificadas()


def detectar_encoding(caminho_csv: Path) -> str:
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]

    for enc in encodings:
        try:
            pd.read_csv(caminho_csv, encoding=enc, nrows=0)
            return enc
        except UnicodeDecodeError:
            continue
        except Exception:
            return enc

    return "latin1"


def carregar_dataframe_csv(caminho_csv: Path) -> pd.DataFrame:
    encoding = detectar_encoding(caminho_csv)
    print(f"Encoding usado: {encoding}")

    df = pd.read_csv(
        caminho_csv,
        encoding=encoding,
        dtype=str,
        low_memory=False,
    )

    coluna_texto = achar_coluna(df.columns, COLUNA_TEXTO)

    if coluna_texto != COLUNA_TEXTO:
        df = df.rename(columns={coluna_texto: COLUNA_TEXTO})

    for nome_coluna in [COLUNA_MUSICA, COLUNA_ARTISTA]:
        try:
            coluna_real = achar_coluna(df.columns, nome_coluna)
            if coluna_real != nome_coluna:
                df = df.rename(columns={coluna_real: nome_coluna})
        except ValueError:
            df[nome_coluna] = ""

    if USAR_PRIMEIRAS_N_MUSICAS is not None:
        df = df.head(USAR_PRIMEIRAS_N_MUSICAS).copy()

    return df


def carregar_spacy():
    global _NLP

    if _NLP is not None:
        return _NLP

    try:
        import spacy
    except ImportError as exc:
        raise RuntimeError from exc

    try:
        _NLP = spacy.load(MODELO_SPACY, disable=["parser", "ner"])
    except OSError as exc:
        raise RuntimeError from exc

    _NLP.tokenizer.token_match = re.compile(
        r"^[A-Za-zÀ-ÖØ-öø-ÿ0-9_]+$"
    ).match

    return _NLP


def limpar_texto_para_spacy(texto: str) -> str:
    texto = str(texto).lower()
    texto = re.sub(r"[^a-zA-ZÀ-ÖØ-öø-ÿ0-9_\s]", " ", texto)
    texto = re.sub(r"\d+", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tokens_from_doc(doc) -> list[dict]:
    saida = []

    for tok in doc:
        if tok.is_space or tok.is_punct:
            continue

        raw = tok.text.lower()
        lema = tok.lemma_.lower() if tok.lemma_ else raw

        alvo_norm = normalizar_alvo(raw)
        attr_raw_norm = normalizar_atributo(raw)
        attr_lemma_norm = normalizar_atributo(lema)

        if alvo_norm or attr_raw_norm or attr_lemma_norm:
            saida.append({
                "raw": raw,
                "lemma": lema,
                "alvo_norm": alvo_norm,
                "attr_raw_norm": attr_raw_norm,
                "attr_lemma_norm": attr_lemma_norm,
            })

    return saida


def tokenizar_dataframe_uma_vez(df: pd.DataFrame) -> list[dict]:
    nlp = carregar_spacy()

    textos_limpos = []
    metadados = []

    for idx_linha, row in df.iterrows():
        textos_limpos.append(
            limpar_texto_para_spacy(
                row.get(COLUNA_TEXTO, "")
            )
        )

        metadados.append({
            "idx_linha_csv": idx_linha,
            "musica": row.get(COLUNA_MUSICA, ""),
            "artista": row.get(COLUNA_ARTISTA, ""),
        })

    registros_tokenizados = []

    print("Tokenizando corpus uma única vez com spaCy...")

    for meta, doc in zip(
        metadados,
        nlp.pipe(
            textos_limpos,
            batch_size=NLP_PIPE_BATCH_SIZE,
        ),
    ):
        tokens = tokens_from_doc(doc)

        if not tokens:
            continue

        registros_tokenizados.append({
            "idx_linha_csv": meta["idx_linha_csv"],
            "musica": meta["musica"],
            "artista": meta["artista"],
            "tokens": tokens,
        })

    print(
        f"Registros com tokens: "
        f"{len(registros_tokenizados)} de {len(df)}"
    )

    return registros_tokenizados


def lematizar_palavra_atributo(palavra: str) -> str:
    texto_limpo = limpar_texto_para_spacy(palavra)

    if not texto_limpo:
        return normalizar_atributo(palavra)

    nlp = carregar_spacy()
    doc = nlp(texto_limpo)

    for tok in doc:
        if tok.is_space or tok.is_punct:
            continue

        lema = (
            tok.lemma_.lower()
            if tok.lemma_
            else tok.text.lower()
        )

        return (
            normalizar_atributo(lema)
            or normalizar_atributo(tok.text)
        )

    return normalizar_atributo(palavra)


def preparar_alvos() -> dict[str, set[str]]:
    resultado = {}

    for genero, palavras in ALVOS.items():
        formas = set()

        for palavra in palavras:
            forma = normalizar_alvo(palavra)

            if forma:
                formas.add(forma)

        resultado[genero] = formas

    return resultado


def preparar_atributos() -> dict[str, dict[str, set[str]]]:
    resultado = {}

    for categoria, palavras in ATRIBUTOS.items():
        resultado[categoria] = {}

        for palavra in palavras:
            canonica = normalizar_atributo(palavra)

            if not canonica:
                continue

            variantes = {canonica}

            lema = lematizar_palavra_atributo(palavra)

            if lema:
                variantes.add(lema)

            resultado[categoria][canonica] = variantes

    return resultado


def obter_listas_preparadas() -> tuple[
    dict[str, set[str]],
    dict[str, dict[str, set[str]]],
]:
    global _ALVOS_NORM_CACHE, _ATRIBUTOS_NORM_CACHE

    if _ALVOS_NORM_CACHE is None:
        _ALVOS_NORM_CACHE = preparar_alvos()

    if _ATRIBUTOS_NORM_CACHE is None:
        _ATRIBUTOS_NORM_CACHE = preparar_atributos()

    return _ALVOS_NORM_CACHE, _ATRIBUTOS_NORM_CACHE


def extrair_contextos_de_tokens(
    registros_tokenizados: list[dict],
    alvos_norm: dict[str, set[str]],
) -> list[dict]:
    contextos = []

    for registro in registros_tokenizados:
        tokens = registro["tokens"]
        musica = registro["musica"]
        artista = registro["artista"]
        idx_linha = registro["idx_linha_csv"]

        for i, token in enumerate(tokens):
            token_alvo = token["alvo_norm"]

            for genero, alvos_genero in alvos_norm.items():
                if token_alvo not in alvos_genero:
                    continue

                ini = max(
                    0,
                    i - JANELA_CONTEXTO,
                )

                fim = min(
                    len(tokens),
                    i + JANELA_CONTEXTO + 1,
                )

                if REMOVER_ALVO_DO_CONTEXTO:
                    tokens_contexto = (
                        tokens[ini:i]
                        + tokens[i + 1:fim]
                    )
                else:
                    tokens_contexto = tokens[ini:fim]

                if not tokens_contexto:
                    continue

                contextos.append({
                    "idx_linha_csv": idx_linha,
                    "genero": genero,
                    "alvo": token["raw"],
                    "alvo_norm": token_alvo,
                    "alvo_lema_apenas_auditoria": token["lemma"],
                    "contexto": " ".join(
                        t["raw"]
                        for t in tokens_contexto
                    ),
                    "contexto_lematizado": " ".join(
                        t["lemma"]
                        for t in tokens_contexto
                    ),
                    "contexto_attr_raw": [
                        t["attr_raw_norm"]
                        for t in tokens_contexto
                        if t["attr_raw_norm"]
                    ],
                    "contexto_attr_lemas": [
                        t["attr_lemma_norm"]
                        for t in tokens_contexto
                        if t["attr_lemma_norm"]
                    ],
                    "musica": musica,
                    "artista": artista,
                })

    if not DEDUPLICAR_CONTEXTOS:
        return contextos

    vistos = set()
    unicos = []

    for contexto in contextos:
        chave = (
            contexto["genero"],
            contexto["alvo_norm"],
            contexto["contexto"],
            contexto["musica"],
            contexto["artista"],
        )

        if chave in vistos:
            continue

        vistos.add(chave)
        unicos.append(contexto)

    return unicos


def contar_variantes_no_contexto(
    contexto: dict,
    variantes: set[str],
) -> int:
    total = 0

    raws = contexto.get(
        "contexto_attr_raw",
        [],
    )

    lemas = contexto.get(
        "contexto_attr_lemas",
        [],
    )

    for raw, lema in zip(raws, lemas):
        if raw in variantes or lema in variantes:
            total += 1

    return total


def contexto_tem_variantes(
    contexto: dict,
    variantes: set[str],
) -> bool:
    return contar_variantes_no_contexto(
        contexto,
        variantes,
    ) > 0


def pmi_suavizada(
    n_total: int,
    n_genero: int,
    n_attr_total: int,
    n_attr_genero: int,
) -> float:
    p_y_dado_x = (
        n_attr_genero + EPSILON
    ) / (
        n_genero + 2 * EPSILON
    )

    p_y = (
        n_attr_total + EPSILON
    ) / (
        n_total + 2 * EPSILON
    )

    return math.log2(
        p_y_dado_x / p_y
    )


def plotar_barras_genero(
    ax,
    df: pd.DataFrame,
    coluna: str,
    titulo: str,
    ylabel: str,
) -> None:
    pivot = (
        df.pivot(
            index="categoria",
            columns="genero",
            values=coluna,
        )
        .reindex(ORDEM_CATEGORIAS)
    )

    x = np.arange(
        len(ORDEM_CATEGORIAS)
    )

    largura = 0.35

    ax.bar(
        x - largura / 2,
        pivot.get(
            "Masculino",
            pd.Series(
                index=ORDEM_CATEGORIAS,
                dtype=float,
            ),
        ),
        largura,
        label="Masculino",
    )

    ax.bar(
        x + largura / 2,
        pivot.get(
            "Feminino",
            pd.Series(
                index=ORDEM_CATEGORIAS,
                dtype=float,
            ),
        ),
        largura,
        label="Feminino",
    )

    ax.axhline(
        0,
        linestyle="--",
        linewidth=1,
    )

    ax.set_title(titulo)
    ax.set_xlabel("Categoria")
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)

    ax.set_xticklabels(
        ORDEM_CATEGORIAS,
        rotation=45,
        ha="right",
    )

    ax.legend(
        title="Gênero"
    )


def gerar_grafico_contexto_2(
    df_consolidado: pd.DataFrame,
    nome_csv: str,
) -> Path | None:
    df_csv = df_consolidado[
        df_consolidado[
            "csv_origem"
        ] == nome_csv
    ].copy()

    if df_csv.empty:
        return None

    fig, ax = plt.subplots(
        1,
        1,
        figsize=(10, 5),
    )

    nome_exibicao = (
        nome_csv
        .replace("_", " ")
        .upper()
    )

    plotar_barras_genero(
        ax=ax,
        df=df_csv,
        coluna="pmi_medio_palavras",
        titulo=(
            f"{nome_exibicao}, "
            f"janela de contexto (alvo+atributo) = 2\n"
            f"PMI médio por atributo"
        ),
        ylabel="PMI médio",
    )

    plt.tight_layout()

    caminho_saida = (
        PASTA_SAIDA_LOTE
        / f"{nome_csv}_pmi_medio_contexto_2.png"
    )

    plt.savefig(
        caminho_saida,
        dpi=200,
    )

    plt.close()

    return caminho_saida


def limpar_outputs_antigos_contexto_2() -> None:
    padroes = [
        "*_pmi_medio_contexto_2.png",
        "resumo_consolidado_categorias_todos_csvs_contexto2.csv",
    ]

    for padrao in padroes:
        for caminho in PASTA_SAIDA_LOTE.glob(padrao):
            if caminho.is_file():
                caminho.unlink()


def calcular_pmi(
    contextos: list[dict],
    qtd_musicas: int,
    alvos_norm: dict[str, set[str]],
    atributos_norm: dict[str, dict[str, set[str]]],
) -> pd.DataFrame:
    if not contextos:
        raise ValueError

    colisoes = sorted(
        alvos_norm.get(
            "Feminino",
            set(),
        )
        & alvos_norm.get(
            "Masculino",
            set(),
        )
    )

    n_total_contextos = len(
        contextos
    )

    contextos_por_genero = {
        genero: [
            contexto
            for contexto in contextos
            if contexto["genero"] == genero
        ]
        for genero in ALVOS
    }

    n_genero = {
        genero: len(lista)
        for genero, lista
        in contextos_por_genero.items()
    }

    print(
        f"Músicas analisadas: "
        f"{qtd_musicas}"
    )

    print(
        f"Janela de contexto: "
        f"{JANELA_CONTEXTO}"
    )

    print(
        f"Contextos usados: "
        f"{n_total_contextos}"
    )

    print(
        f"Contextos por gênero: "
        f"{n_genero}"
    )

    print(
        f"Colisões entre alvos normalizados: "
        f"{len(colisoes)}"
    )

    linhas_palavras = []

    for categoria, palavras in atributos_norm.items():
        print(
            f"Contando categoria: "
            f"{categoria}"
        )

        for palavra_canonica, variantes in palavras.items():

            cont_total = sum(
                contar_variantes_no_contexto(
                    contexto,
                    variantes,
                )
                for contexto in contextos
            )

            ctx_total = sum(
                1
                for contexto in contextos
                if contexto_tem_variantes(
                    contexto,
                    variantes,
                )
            )

            entra = (
                cont_total
                >= MIN_OCORRENCIA_ATRIBUTO
            )

            for genero, lista_ctx in contextos_por_genero.items():

                cont_genero = sum(
                    contar_variantes_no_contexto(
                        contexto,
                        variantes,
                    )
                    for contexto in lista_ctx
                )

                ctx_genero = sum(
                    1
                    for contexto in lista_ctx
                    if contexto_tem_variantes(
                        contexto,
                        variantes,
                    )
                )

                pmi = (
                    pmi_suavizada(
                        n_total_contextos,
                        n_genero[genero],
                        ctx_total,
                        ctx_genero,
                    )
                    if entra
                    else np.nan
                )

                linhas_palavras.append({
                    "genero": genero,
                    "categoria": categoria,
                    "palavra_canonica": palavra_canonica,
                    "variantes_consideradas": "; ".join(
                        sorted(variantes)
                    ),
                    "n_total_contextos": n_total_contextos,
                    "contextos_com_atributo_baseline": ctx_total,
                    "contextos_com_atributo_genero": ctx_genero,
                    "ocorrencias_atributo_baseline": cont_total,
                    "ocorrencias_atributo_genero": cont_genero,
                    "p_contexto_atributo_baseline": (
                        ctx_total / n_total_contextos
                        if n_total_contextos
                        else np.nan
                    ),
                    "p_contexto_atributo_genero": (
                        ctx_genero / n_genero[genero]
                        if n_genero[genero]
                        else np.nan
                    ),
                    "ocorrencias_por_100_contextos_genero": (
                        cont_genero
                        / n_genero[genero]
                        * 100
                        if n_genero[genero]
                        else np.nan
                    ),
                    "pmi_por_contexto_binario": pmi,
                    "usada_na_media": entra,
                    "motivo": (
                        "ok"
                        if entra
                        else "nao_ocorre_no_baseline"
                    ),
                })

    df_palavras = pd.DataFrame(
        linhas_palavras
    )

    linhas_cat = []

    for categoria in ORDEM_CATEGORIAS:

        for genero in [
            "Masculino",
            "Feminino",
        ]:

            grupo = df_palavras[
                (
                    df_palavras["categoria"]
                    == categoria
                )
                & (
                    df_palavras["genero"]
                    == genero
                )
                & (
                    df_palavras[
                        "usada_na_media"
                    ]
                )
            ]

            linhas_cat.append({
                "genero": genero,
                "categoria": categoria,
                "pmi_medio_palavras": (
                    grupo[
                        "pmi_por_contexto_binario"
                    ].mean()
                    if not grupo.empty
                    else np.nan
                ),
            })

    df_cat = pd.DataFrame(
        linhas_cat
    )

    df_cat["categoria"] = pd.Categorical(
        df_cat["categoria"],
        categories=ORDEM_CATEGORIAS,
        ordered=True,
    )

    df_cat = df_cat.sort_values(
        [
            "categoria",
            "genero",
        ]
    )

    print(
        "\nResumo por categoria:"
    )

    print(
        df_cat.to_string(
            index=False
        )
    )

    return df_cat


def main_lote() -> None:
    resultados_categorias = []

    limpar_outputs_antigos_contexto_2()

    print("=" * 80)
    print("RODANDO PMI - JANELA DE CONTEXTO 2")
    print("=" * 80)

    print(
        f"Pasta de saída: "
        f"{PASTA_SAIDA_LOTE}"
    )

    print(
        f"Janela de contexto: "
        f"{JANELA_CONTEXTO}"
    )

    print(
        "\nCSVs que serão processados:"
    )

    for nome_csv, caminho_csv in ARQUIVOS_ENTRADA.items():
        print(
            f"- {nome_csv}: "
            f"{caminho_csv}"
        )

    print(
        "\nPreparando listas..."
    )

    alvos_norm, atributos_norm = (
        obter_listas_preparadas()
    )

    print(
        "\nAlvos normalizados "
        "que formarão contexto:"
    )

    for genero, alvos in alvos_norm.items():
        print(
            f"- {genero}: "
            f"{sorted(alvos)}"
        )

    for nome_csv, caminho_csv in ARQUIVOS_ENTRADA.items():

        if not caminho_csv.exists():
            continue

        try:

            print(
                "\n"
                + "#"
                * 80
            )

            print(
                f"CSV: "
                f"{nome_csv}"
            )

            print(
                f"Arquivo: "
                f"{caminho_csv}"
            )

            print(
                "#"
                * 80
            )

            df = carregar_dataframe_csv(
                caminho_csv
            )

            registros_tokenizados = (
                tokenizar_dataframe_uma_vez(
                    df
                )
            )

            if not registros_tokenizados:
                continue

            print(
                "Extraindo contextos "
                "da janela 2..."
            )

            contextos = (
                extrair_contextos_de_tokens(
                    registros_tokenizados,
                    alvos_norm,
                )
            )

            if not contextos:
                continue

            df_cat = calcular_pmi(
                contextos=contextos,
                qtd_musicas=len(df),
                alvos_norm=alvos_norm,
                atributos_norm=atributos_norm,
            )

            df_cat.insert(
                0,
                "csv_origem",
                nome_csv,
            )

            resultados_categorias.append(
                df_cat
            )

            print(
                f"\n[OK] Finalizado: "
                f"{nome_csv}"
            )

        except Exception:
            continue

    if resultados_categorias:

        df_consolidado = pd.concat(
            resultados_categorias,
            ignore_index=True,
        )

        caminho_consolidado = (
            PASTA_SAIDA_LOTE
            / "resumo_consolidado_categorias_todos_csvs_contexto2.csv"
        )

        df_consolidado.to_csv(
            caminho_consolidado,
            index=False,
            encoding="utf-8-sig",
        )

        caminhos_graficos = []

        for nome_csv in ARQUIVOS_ENTRADA:

            caminho = (
                gerar_grafico_contexto_2(
                    df_consolidado,
                    nome_csv,
                )
            )

            if caminho is not None:
                caminhos_graficos.append(
                    caminho
                )

        print(
            "\n"
            + "="
            * 80
        )

        print(
            "ARQUIVOS GERADOS"
        )

        print(
            "="
            * 80
        )

        print(
            f"Resumo consolidado: "
            f"{caminho_consolidado}"
        )

        print(
            "\nGráficos do contexto 2:"
        )

        for caminho in caminhos_graficos:
            print(
                f"- {caminho}"
            )

    print(
        "\n"
        + "="
        * 80
    )

    print(
        "PROCESSAMENTO FINALIZADO"
    )

    print(
        "="
        * 80
    )

    print(
        f"Pasta de saída: "
        f"{PASTA_SAIDA_LOTE}"
    )


if __name__ == "__main__":
    main_lote()

