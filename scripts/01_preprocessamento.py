from pathlib import Path
import pandas as pd
import unicodedata
import re
import csv

PASTA = Path(r"D:\Downloads")

musicas_146k = PASTA / "merged_df.txt"

CHUNKSIZE = 10000

ARQUIVO_SAIDA_LIMPO = PASTA / "merged_df_pmi.csv"
ARQUIVO_SAIDA_DUPLICADAS = PASTA / "merged_df_duplicadas_removidas_pmi.csv"

GENEROS_FILTRAR = {
    "pagode": "pagode",
    "sertanejo": "sertanejo",
    "forro": "forró",
    "funk": "funk",
    "mpb": "mpb",
}

ARQUIVOS_SAIDA_GENEROS = {
    "pagode": PASTA / "pagode_pmi.csv",
    "sertanejo": PASTA / "sertanejo_pmi.csv",
    "forro": PASTA / "forro_pmi.csv",
    "funk": PASTA / "funk_pmi.csv",
    "mpb": PASTA / "mpb_pmi.csv",
}


def normalizar_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )
    texto = re.sub(r"\s+", " ", texto)

    return texto


def normalizar_nome_coluna(coluna):
    return normalizar_texto(coluna).replace(" ", "")


def achar_coluna(df, nome_desejado):
    alvo = normalizar_nome_coluna(nome_desejado)

    for coluna in df.columns:
        if normalizar_nome_coluna(coluna) == alvo:
            return coluna


def para_minusculo(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().lower()
    texto = re.sub(r"\s+", " ", texto)

    return texto


def limpar_letra(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).lower()

    texto = "".join(
        caractere
        if caractere.isalpha() or caractere.isspace()
        else " "
        for caractere in texto
    )

    return texto


def normalizar_para_chave(valor):
    return normalizar_texto(valor)


def detectar_encoding(caminho):
    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin1"
    ]

    for enc in encodings:
        try:
            pd.read_csv(
                caminho,
                sep=",",
                encoding=enc,
                nrows=20,
                dtype=str,
                engine="python"
            )

            return enc

        except UnicodeDecodeError:
            continue

        except Exception:
            return enc

    return "latin1"


def separar_generos(genero):
    genero_norm = normalizar_texto(genero)

    partes = re.split(
        r"[,;/|]+",
        genero_norm
    )

    partes = [
        parte.strip()
        for parte in partes
        if parte.strip()
    ]

    return partes


def contem_genero(genero, genero_alvo):
    genero_norm = normalizar_texto(genero)
    genero_alvo_norm = normalizar_texto(genero_alvo)

    return bool(
        re.search(
            rf"(^|[^a-z])"
            rf"{re.escape(genero_alvo_norm)}"
            rf"([^a-z]|$)",
            genero_norm
        )
    )


def apagar_saidas_antigas():
    arquivos = [
        ARQUIVO_SAIDA_LIMPO,
        ARQUIVO_SAIDA_DUPLICADAS,
        *ARQUIVOS_SAIDA_GENEROS.values(),
    ]

    for arquivo in arquivos:
        if arquivo.exists():
            arquivo.unlink()


encoding = detectar_encoding(musicas_146k)

print("=" * 80)
print("PREPROCESSAMENTO + FILTRAGEM POR GÊNERO")
print("=" * 80)
print(f"Arquivo: {musicas_146k}")
print(f"Encoding: {encoding}")
print("=" * 80)

apagar_saidas_antigas()

reader = pd.read_csv(
    musicas_146k,
    sep=",",
    encoding=encoding,
    chunksize=CHUNKSIZE,
    dtype=str,
    engine="python",
    on_bad_lines="skip"
)

chaves_vistas = set()

primeira_escrita_limpo = True
primeira_escrita_duplicadas = True

primeira_escrita_genero = {
    genero: True
    for genero in GENEROS_FILTRAR
}

total_lidas = 0
total_mantidas = 0
total_duplicadas = 0

totais_generos = {
    genero: 0
    for genero in GENEROS_FILTRAR
}

for chunk in reader:

    chunk = chunk.copy()

    coluna_musica = achar_coluna(
        chunk,
        "Nome da Música"
    )

    coluna_artista = achar_coluna(
        chunk,
        "Artista"
    )

    coluna_genero = achar_coluna(
        chunk,
        "Gênero Musical"
    )

    coluna_letra = achar_coluna(
        chunk,
        "Letra da Música"
    )

    inicio_linha_original = total_lidas + 2

    if "linha_original_aproximada" not in chunk.columns:

        chunk.insert(
            0,
            "linha_original_aproximada",
            range(
                inicio_linha_original,
                inicio_linha_original + len(chunk)
            )
        )

    else:

        colunas = [
            "linha_original_aproximada"
        ] + [
            coluna
            for coluna in chunk.columns
            if coluna != "linha_original_aproximada"
        ]

        chunk = chunk[colunas]

    total_lidas += len(chunk)

    chunk[coluna_musica] = (
        chunk[coluna_musica]
        .apply(para_minusculo)
    )

    chunk[coluna_artista] = (
        chunk[coluna_artista]
        .apply(para_minusculo)
    )

    chunk[coluna_genero] = (
        chunk[coluna_genero]
        .apply(para_minusculo)
    )

    chunk[coluna_letra] = (
        chunk[coluna_letra]
        .apply(limpar_letra)
    )

    chunk["_chave_duplicata"] = (
        chunk[coluna_artista]
        .apply(normalizar_para_chave)
        + " || "
        + chunk[coluna_musica]
        .apply(normalizar_para_chave)
        + " || "
        + chunk[coluna_genero]
        .apply(normalizar_para_chave)
    )

    manter_indices = []
    duplicada_indices = []

    for idx, chave in chunk["_chave_duplicata"].items():

        if chave in chaves_vistas:
            duplicada_indices.append(idx)

        else:
            chaves_vistas.add(chave)
            manter_indices.append(idx)

    df_limpo = (
        chunk
        .loc[manter_indices]
        .copy()
    )

    df_duplicadas = (
        chunk
        .loc[duplicada_indices]
        .copy()
    )

    if "_chave_duplicata" in df_limpo.columns:

        df_limpo = df_limpo.drop(
            columns=["_chave_duplicata"]
        )

    if not df_duplicadas.empty:

        df_duplicadas = df_duplicadas.rename(
            columns={
                "_chave_duplicata":
                "chave_duplicata"
            }
        )

    total_mantidas += len(df_limpo)
    total_duplicadas += len(df_duplicadas)

    if not df_limpo.empty:

        df_limpo.to_csv(
            ARQUIVO_SAIDA_LIMPO,
            mode=(
                "w"
                if primeira_escrita_limpo
                else "a"
            ),
            header=primeira_escrita_limpo,
            index=False,
            encoding="utf-8-sig",
            quoting=csv.QUOTE_ALL
        )

        primeira_escrita_limpo = False

    if not df_duplicadas.empty:

        df_duplicadas.to_csv(
            ARQUIVO_SAIDA_DUPLICADAS,
            mode=(
                "w"
                if primeira_escrita_duplicadas
                else "a"
            ),
            header=primeira_escrita_duplicadas,
            index=False,
            encoding="utf-8-sig",
            quoting=csv.QUOTE_ALL
        )

        primeira_escrita_duplicadas = False

    for chave_genero, nome_genero in GENEROS_FILTRAR.items():

        arquivo_saida_genero = (
            ARQUIVOS_SAIDA_GENEROS[
                chave_genero
            ]
        )

        mascara = (
            df_limpo[coluna_genero]
            .apply(
                lambda x:
                contem_genero(
                    x,
                    nome_genero
                )
            )
        )

        df_filtrado = (
            df_limpo
            .loc[mascara]
            .copy()
        )

        if df_filtrado.empty:
            continue

        df_filtrado[
            "genero_filtrado"
        ] = nome_genero

        df_filtrado[
            "genero_normalizado"
        ] = (
            df_filtrado[coluna_genero]
            .apply(normalizar_texto)
        )

        df_filtrado[
            "qtd_generos_detectados"
        ] = (
            df_filtrado[coluna_genero]
            .apply(
                lambda x:
                len(separar_generos(x))
            )
        )

        df_filtrado[
            "nome_musica_normalizado"
        ] = (
            df_filtrado[coluna_musica]
            .apply(normalizar_texto)
        )

        df_filtrado[
            "artista_normalizado"
        ] = (
            df_filtrado[coluna_artista]
            .apply(normalizar_texto)
        )

        df_filtrado[
            "chave_musica_artista"
        ] = (
            df_filtrado[
                "nome_musica_normalizado"
            ]
            + " || "
            + df_filtrado[
                "artista_normalizado"
            ]
        )

        totais_generos[
            chave_genero
        ] += len(
            df_filtrado
        )

        df_filtrado.to_csv(
            arquivo_saida_genero,
            mode=(
                "w"
                if primeira_escrita_genero[
                    chave_genero
                ]
                else "a"
            ),
            header=(
                primeira_escrita_genero[
                    chave_genero
                ]
            ),
            index=False,
            encoding="utf-8-sig",
            quoting=csv.QUOTE_ALL
        )

        primeira_escrita_genero[
            chave_genero
        ] = False

    resumo_generos = " | ".join(
        (
            f"{genero}: "
            f"{totais_generos[genero]:,}"
        ).replace(",", ".")
        for genero in GENEROS_FILTRAR
    )

    mensagem = (
        f"Lidas: {total_lidas:,} | "
        f"Mantidas: {total_mantidas:,} | "
        f"Duplicadas: {total_duplicadas:,} | "
        f"{resumo_generos}"
    )

    print(
        mensagem.replace(",", ".")
    )

print("\n" + "=" * 80)
print("FINALIZADO")
print("=" * 80)

print(
    f"Total de linhas lidas: "
    f"{total_lidas}"
)

print(
    f"Total de linhas mantidas sem duplicadas: "
    f"{total_mantidas}"
)

print(
    f"Total de duplicadas removidas: "
    f"{total_duplicadas}"
)

for chave_genero, nome_genero in GENEROS_FILTRAR.items():

    print(
        f"{nome_genero}: "
        f"{totais_generos[chave_genero]}"
    )