import pandas as pd
import re
import nltk

from nltk.corpus import stopwords
from spacy.lang.pt.stop_words import STOP_WORDS as SPACY_STOP_WORDS
from stopwordsiso import stopwords as iso_stopwords


# ============================================================
# ARQUIVOS
# ============================================================

ARQUIVO_ENTRADA = "df_uniao.csv"
ARQUIVO_SAIDA = "df_uniao_limpo_lopes_4.csv"


# ============================================================
# STOPWORDS NLTK - PORTUGUÊS
# ============================================================

try:
    lista_stopwords_nltk = stopwords.words("portuguese")

except LookupError:
    nltk.download("stopwords")
    lista_stopwords_nltk = stopwords.words("portuguese")


# ============================================================
# STOPWORDS SPACY - PORTUGUÊS
# ============================================================

lista_stopwords_spacy = list(SPACY_STOP_WORDS)


# ============================================================
# STOPWORDS ISO - PORTUGUÊS
# ============================================================

lista_stopwords_iso = list(
    iso_stopwords("pt")
)


# ============================================================
# PRONOMES
# ============================================================

lista_pronomes = [
    "meu", "minha", "meus", "minhas", "teu", "tua", "teus", "tuas",
    "seu", "sua", "seus", "suas", "nosso", "nossa", "nossos", "nossas",
    "vosso", "vossa", "vossos", "vossas",
    "eu", "tu", "nós", "vós", "comigo", "mim", "nois", "nóis",
]


# ============================================================
# PRONOMES DE TRATAMENTO / FORMAS DE SUJEITO
# ============================================================

lista_pronomes_tratamento = [
    "você", "vocês",
    "cê", "cês",
    "vc", "voce",
    "voc", "voçê", "vacê",
]


# ============================================================
# TERMOS ESTRANGEIROS / INTERJEIÇÕES JÁ EXCLUÍDOS NO CÓDIGO
# ANTERIOR
# ============================================================

lista_termos_estrangeiros_interjeicoes = [
    "they", "I", "bye",
    "yeah", "ahn", "hey", "oooo", "la", "pam", "lalá", "uáááá",
    "bis",
]


# ============================================================
# ALFABETO
# ============================================================

alfabeto = [
    "a", "b", "c", "d", "e", "f", "g", "h",
    "i", "j", "k", "l", "m", "n", "o", "p",
    "q", "r", "s", "t", "u", "v", "w", "x",
    "y", "z", "ô", "á", "ê",
]


# ============================================================
# CHEN ET AL. (2025) - TRADUÇÃO EXATA DOS ALVOS E ATRIBUTOS
#
# Tradução 1:1 das Tables 3 e 4 do artigo:
# mesma quantidade, mesma ordem e uma tradução por termo.
# Não são acrescentados sinônimos, flexões, plurais extras,
# grafias alternativas ou variantes inventadas.
#
# REGRA PRINCIPAL:
# todo termo presente nesta lista entra obrigatoriamente no
# critério de exclusão.
# ============================================================

lista_chen_traduzida = [

    # AGRADÁVEL
    'amigo', 'alegria', 'maravilhoso', 'férias', 'amor', 'honesto', 'honra',
    'prazer', 'leal', 'família', 'paz', 'céu', 'ânimo', 'liberdade',
    'diploma', 'gentil', 'feliz', 'paraíso', 'diamante', 'riso', 'nascer do sol',
    'presente', 'saúde', 'arco-íris', 'carícia', 'sortudo', 'milagre',

    # DESAGRADÁVEL
    'terrível', 'prisão', 'divórcio', 'guerra', 'pobreza', 'doença', 'abuso',
    'tragédia', 'ódio', 'batida', 'acidente', 'veneno', 'nojento', 'horrível',
    'luto', 'desastre', 'fedor', 'poluir', 'feio', 'podre', 'sujeira',
    'fracasso', 'bomba', 'horrível', 'cadeia', 'matar', 'câncer', 'morte',
    'assassinato', 'mal', 'vômito', 'agonia', 'agressão',

    # APARÊNCIA
    'sensual', 'magro', 'bonito', 'fraco', 'careca', 'na moda', 'esbelto',
    'deslumbrante', 'gordo', 'rechonchudo', 'musculoso', 'lindo', 'forte', 'fraco',
    'feio', 'esbelto', 'sem graça', 'saudável', 'corado', 'atlético', 'voluptuoso',
    'corpulento', 'belo', 'sedutor', 'atraente',

    # INTELIGÊNCIA
    'inteligente', 'venerável', 'adaptável', 'reflexivo', 'ponderado', 'habilidoso', 'gênio',
    'lógico', 'esperto', 'astuto', 'sensato', 'imaginativo', 'intuitivo', 'perspicaz',
    'engenhoso', 'apto', 'precoce', 'inventivo', 'analítico', 'investigativo', 'curioso',
    'discernente', 'brilhante', 'esperto', 'sábio',

    # FORÇA
    'potente', 'ousado', 'líder', 'forte', 'triunfo', 'comando', 'grito',
    'vencedor', 'dominante', 'poder', 'ter sucesso', 'confiante', 'dinâmico', 'barulhento',
    'assertivo',

    # FRAQUEZA
    'franzino', 'perdedor', 'fracasso', 'tímido', 'perder', 'fraco', 'fraqueza',
    'tímido', 'rendição', 'seguir', 'frágil', 'recuar', 'vulnerável', 'ceder',
    'amedrontado',

    # ALVOS FEMININOS
    'tia', 'titia', 'filha', 'nora', 'feminina', 'garota', 'menina',
    'namorada', 'avó', 'avó por afinidade', 'dela', 'dela', 'dama', 'senhora',
    'mamãe', 'senhorita', 'mãe', 'mãe', 'sobrinha', 'rainha', 'ela',
    'mana', 'irmã', 'esposa', 'mulher',

    # ALVOS MASCULINOS
    'menino', 'namorado', 'irmão', 'pai', 'pai', 'sogro', 'avô',
    'vovô', 'cara', 'ele', 'ele', 'dele', 'marido', 'rei',
    'masculino', 'homem', 'sobrinho', 'papai', 'senhor', 'filho', 'genro',
    'tio',
]


# ============================================================
# EXCLUSÕES ADICIONAIS QUE NÃO SÃO DE CHEN
# ============================================================

lista_seres_celestiais_religiosos = [
    "cristo", "jesus", "deus", "judas", "oxossi", "oxum", "iemanjá", "aleluia",
]

lista_verbo_ficar = [
    "fica", "ficou", "ficar", "ficam",
]


# ============================================================
# FUNÇÃO PARA REMOVER AUX, ADV, DET E PRONOUN CONFORME O PADRÃO
# ============================================================

def remover_aux_adv_det_pronoun(frase, padrao):

    if pd.isna(frase):
        return ""

    if pd.isna(padrao):
        return str(frase).strip()

    frase = str(frase).strip()
    padrao = str(padrao).strip()

    palavras = frase.split()

    # Aceita padrões separados por "_", "+" ou espaço.
    elementos = [
        elemento
        for elemento in re.split(
            r"[_+\s]+",
            padrao
        )
        if elemento
    ]

    elementos = [
        elemento.lower()
        for elemento in elementos
    ]

    # Mantém NOUN e todas as demais classes.
    # Remove somente AUX, ADV, DET e PRONOUN.
    classes_remover = {
        "aux",
        "adv",
        "det",
        "pronoun",
    }

    if not any(
        elemento in classes_remover
        for elemento in elementos
    ):
        return frase

    # ADV pode representar mais de uma palavra no texto.
    extras = len(palavras) - len(elementos)

    if extras < 0:
        extras = 0

    resultado = []
    indice_palavra = 0

    for elemento in elementos:

        # ----------------------------------------------------
        # AUX
        # ----------------------------------------------------

        if elemento == "aux":

            if indice_palavra < len(palavras):
                indice_palavra += 1

            continue

        # ----------------------------------------------------
        # ADV
        # ----------------------------------------------------

        if elemento == "adv":

            quantidade_adv = 1 + extras

            indice_palavra += quantidade_adv

            extras = 0

            continue

        # ----------------------------------------------------
        # DET
        # ----------------------------------------------------

        if elemento == "det":

            if indice_palavra < len(palavras):
                indice_palavra += 1

            continue

        # ----------------------------------------------------
        # PRONOUN
        # ----------------------------------------------------

        if elemento == "pronoun":

            if indice_palavra < len(palavras):
                indice_palavra += 1

            continue

        # ----------------------------------------------------
        # DEMAIS ELEMENTOS
        #
        # Inclui NOUN: NOUN NÃO é removido.
        # ----------------------------------------------------

        if indice_palavra < len(palavras):

            resultado.append(
                palavras[indice_palavra]
            )

            indice_palavra += 1

    # Preserva eventuais palavras restantes.
    if indice_palavra < len(palavras):

        resultado.extend(
            palavras[indice_palavra:]
        )

    return " ".join(resultado)


# ============================================================
# NORMALIZAR TEXTO ANTES DAS LISTAS
# ============================================================

def normalizar_texto_para_exclusao(texto):

    if pd.isna(texto):
        return ""

    texto = str(texto)

    # --------------------------------------------------------
    # REMOVER PONTUAÇÃO / CARACTERES ESPECIAIS
    # --------------------------------------------------------
    #
        # arco-íris -> arco íris
    # render-se -> render se

    texto = re.sub(
        r"[^\w\s]",
        " ",
        texto
    )

    # --------------------------------------------------------
    # REMOVER NÚMEROS
    # --------------------------------------------------------
    #
        # 2025 -> ""

    texto = re.sub(
        r"\d+",
        "",
        texto
    )

    # --------------------------------------------------------
    # REMOVER UNDERLINE
    # --------------------------------------------------------

    texto = texto.replace(
        "_",
        " "
    )

    # --------------------------------------------------------
    # NORMALIZAR ESPAÇOS
    # --------------------------------------------------------

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# ============================================================
# FUNÇÃO PARA CRIAR REGEX DE EXCLUSÃO
# ============================================================

def criar_padrao_regex(lista):

    lista_normalizada = []

    for termo in lista:

        termo_normalizado = (
            normalizar_texto_para_exclusao(
                termo
            )
        )

        if termo_normalizado:
            lista_normalizada.append(
                termo_normalizado
            )

    # Remove repetições e coloca expressões maiores primeiro.
    lista_normalizada = sorted(
        set(lista_normalizada),
        key=len,
        reverse=True
    )

    if not lista_normalizada:
        return re.compile(
            r"(?!x)x"
        )

    return re.compile(
        r"(?<!\w)(?:"
        + "|".join(
            re.escape(termo)
            for termo in lista_normalizada
        )
        + r")(?!\w)",
        flags=re.IGNORECASE
    )


# ============================================================
# CARREGAR CSV
# ============================================================

df = pd.read_csv(
    ARQUIVO_ENTRADA
)

linhas_originais = len(df)


print("========================================")
print("ARQUIVO ORIGINAL")
print("========================================")

print(
    f"Linhas: "
    f"{linhas_originais}"
)

print(
    f"Colunas: "
    f"{len(df.columns)}"
)


# ============================================================
# VERIFICAR COLUNAS
# ============================================================

if "Frase" not in df.columns:

    raise ValueError(
        'A coluna "Frase" não foi encontrada.'
    )


if "Padrão" not in df.columns:

    raise ValueError(
        'A coluna "Padrão" não foi encontrada.'
    )


# ============================================================
# CONTAR PADRÕES DISTINTOS NO INÍCIO
# ============================================================

padroes_antes = df["Padrão"].nunique(
    dropna=True
)


print(
    f"Padrões distintos no início: "
    f"{padroes_antes}"
)


# ============================================================
# IDENTIFICAR LINHAS COM AUX, ADV, DET OU PRONOUN
# ============================================================

mascara_aux_adv_det_pronoun = (
    df["Padrão"]
    .fillna("")
    .astype(str)
    .str.contains(
        r"(^|[_+\s])(aux|adv|det|pronoun)(?=[_+\s]|$)",
        case=False,
        regex=True
    )
)


linhas_com_aux_adv_det_pronoun = int(
    mascara_aux_adv_det_pronoun.sum()
)


print()

print("========================================")
print("AUX / ADV / DET / PRONOUN")
print("========================================")

print(
    f"Linhas com AUX, ADV, DET ou PRONOUN no padrão: "
    f"{linhas_com_aux_adv_det_pronoun}"
)


# ============================================================
# REMOVER AUX, ADV, DET E PRONOUN
#
# NOUN É MANTIDO.
# ============================================================

df["Frase"] = df.apply(

    lambda linha: remover_aux_adv_det_pronoun(
        linha["Frase"],
        linha["Padrão"]
    ),

    axis=1
)


# ============================================================
# REMOVER PONTUAÇÃO E NÚMEROS
#
# Isso acontece ANTES das listas de exclusão.
#
# "(2x" -> "x"
# e depois "x" é eliminado pela lista "alfabeto".
# ============================================================

df["Frase"] = (
    df["Frase"]
    .apply(
        normalizar_texto_para_exclusao
    )
)


# ============================================================
# MOSTRAR TAMANHO DAS LISTAS DE STOPWORDS
# ============================================================

print()

print("========================================")
print("LISTAS DE STOPWORDS")
print("========================================")

print(
    f"NLTK: "
    f"{len(set(lista_stopwords_nltk))}"
)

print(
    f"spaCy: "
    f"{len(set(lista_stopwords_spacy))}"
)

print(
    f"ISO: "
    f"{len(set(lista_stopwords_iso))}"
)


# ============================================================
# MOSTRAR A LISTA DE CHEN
# ============================================================

print()

print("========================================")
print("CHEN ET AL. (2025) - TRADUÇÃO EXATA")
print("========================================")

print("Agradável: 27")
print("Desagradável: 33")
print("Aparência: 25")
print("Inteligência: 25")
print("Força: 15")
print("Fraqueza: 15")
print("Feminino: 25")
print("Masculino: 22")
print("Total de entradas das Tables 3 e 4: 187")


# ============================================================
# JUNTAR TODAS AS LISTAS DE EXCLUSÃO
#
# A lista Chen agora é construída exclusivamente a partir das
# Tables 3 e 4 do artigo e traduzida para português.
#
# As exclusões religiosas e do verbo "ficar" continuam sendo
# aplicadas, mas aparecem separadas para deixar claro que NÃO
# pertencem a Chen et al. (2025).
# ============================================================

lista_exclusao = (

    lista_chen_traduzida

    + lista_stopwords_nltk

    + lista_stopwords_spacy

    + lista_stopwords_iso

    + lista_pronomes

    + lista_pronomes_tratamento

    + lista_termos_estrangeiros_interjeicoes

    + alfabeto

    + lista_seres_celestiais_religiosos

    + lista_verbo_ficar
)


# ============================================================
# REMOVER REPETIÇÕES DA LISTA
# ============================================================

lista_exclusao_unica = sorted(
    set(lista_exclusao),
    key=len,
    reverse=True
)


print()

print("========================================")
print("LISTA FINAL DE EXCLUSÃO")
print("========================================")

print(
    f"Total de termos únicos na união das listas: "
    f"{len(lista_exclusao_unica)}"
)


# ============================================================
# CRIAR REGEX DE EXCLUSÃO
# ============================================================

padrao_exclusao = criar_padrao_regex(
    lista_exclusao_unica
)


# ============================================================
# CONTAR TERMOS A SEREM REMOVIDOS
# ============================================================

ocorrencias_exclusao = int(

    df["Frase"]
    .fillna("")
    .astype(str)
    .str.count(
        padrao_exclusao
    )
    .sum()
)


# ============================================================
# REMOVER TODAS AS LISTAS DE EXCLUSÃO
#
# IMPORTANTE:
# A ocorrência é removida DA FRASE.
# A linha inteira só é eliminada depois, caso "Frase" fique
# completamente vazia.
# ============================================================

df["Frase"] = (

    df["Frase"]

    .fillna("")

    .astype(str)

    .str.replace(
        padrao_exclusao,
        "",
        regex=True
    )
)


# ============================================================
# CORRIGIR ESPAÇOS APÓS AS REMOÇÕES
# ============================================================

df["Frase"] = (

    df["Frase"]

    .str.replace(
        r"\s+",
        " ",
        regex=True
    )

    .str.strip()
)


# ============================================================
# REMOVER QUALQUER LETRA ISOLADA QUE TENHA SOBRADO
#
# A lista "alfabeto" cobre letras comuns, mas pode deixar
# escapar letras acentuadas isoladas, como "ó".
# Esta etapa remove qualquer caractere alfabético isolado,
# com ou sem acento, antes de eliminar linhas vazias.
# ============================================================

df["Frase"] = (
    df["Frase"]
    .fillna("")
    .astype(str)
    .str.replace(
        r"(?<!\w)[A-Za-zÀ-ÖØ-öø-ÿ](?!\w)",
        "",
        regex=True
    )
    .str.replace(
        r"\s+",
        " ",
        regex=True
    )
    .str.strip()
)


# ============================================================
# REMOVER LINHAS QUE FICARAM EM BRANCO
# ============================================================

antes_brancos = len(df)


df = df[

    df["Frase"]

    .fillna("")

    .str.strip()

    .ne("")

].copy()


linhas_em_branco_removidas = (
    antes_brancos
    - len(df)
)


# ============================================================
# REMOVER DUPLICADAS APÓS TODA A LIMPEZA
#
# O critério de duplicidade continua sendo APENAS "Frase".
# Se duas linhas ficarem com a mesma frase após a limpeza,
# mantém a primeira.
# ============================================================

antes_duplicadas = len(df)


df = df.drop_duplicates(
    subset=["Frase"],
    keep="first"
).copy()


duplicadas_removidas = (
    antes_duplicadas
    - len(df)
)


# ============================================================
# REORGANIZAR ÍNDICE
# ============================================================

df = df.reset_index(
    drop=True
)


# ============================================================
# CONTAR PADRÕES DISTINTOS NO FINAL
# ============================================================

padroes_depois = df["Padrão"].nunique(
    dropna=True
)


# ============================================================
# VERIFICAÇÃO EXTRA
#
# Confere se ainda ficou alguma frase com apenas
# uma letra isolada.
# ============================================================

mascara_letra_isolada = (
    df["Frase"]
    .fillna("")
    .str.strip()
    .str.fullmatch(
        r"[A-Za-zÀ-ÖØ-öø-ÿ]",
        case=False
    )
)


quantidade_letras_isoladas = int(
    mascara_letra_isolada.sum()
)


# ============================================================
# SALVAR CSV
# ============================================================

df.to_csv(
    ARQUIVO_SAIDA,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# RESUMO FINAL
# ============================================================

print()

print("========================================")
print("RESULTADO FINAL")
print("========================================")


print(
    f"Linhas originais: "
    f"{linhas_originais}"
)


print(
    f"Linhas com AUX/ADV/DET/PRONOUN processadas: "
    f"{linhas_com_aux_adv_det_pronoun}"
)


print(
    f"Palavras/expressões removidas pelas listas: "
    f"{ocorrencias_exclusao}"
)


print(
    f"Linhas removidas por ficarem em branco: "
    f"{linhas_em_branco_removidas}"
)


print(
    f"Duplicadas removidas após a limpeza: "
    f"{duplicadas_removidas}"
)


print(
    f"Frases com uma única letra que ainda sobraram: "
    f"{quantidade_letras_isoladas}"
)


print("----------------------------------------")


print(
    f"Padrões distintos antes: "
    f"{padroes_antes}"
)


print(
    f"Padrões distintos depois: "
    f"{padroes_depois}"
)


print("----------------------------------------")


print(
    f"Linhas finais: "
    f"{len(df)}"
)


print(
    f"Colunas finais: "
    f"{len(df.columns)}"
)


print("----------------------------------------")


print(
    f"Arquivo salvo em: "
    f"{ARQUIVO_SAIDA}"
)
