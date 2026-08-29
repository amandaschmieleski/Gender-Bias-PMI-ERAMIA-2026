import re
import time
import unicodedata
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

import pandas as pd
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ============================================================
# CONFIGURAÇÕES
# ============================================================

URL_IBGE = "https://censo2022.ibge.gov.br/nomes/rankings"

ARQUIVO_ENTRADA = "merged_df.txt"

ARQUIVO_SAIDA = (
    "1000_nomes_femininos_1000_masculinos_ibge.csv"
)

COLUNA_LETRA = "Letra da Música"

QUANTIDADE_POR_SEXO = 1000


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar(texto):

    if pd.isna(texto):
        return ""

    texto = str(texto).lower()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        c
        for c in texto
        if unicodedata.category(c) != "Mn"
    )

    return texto


# ============================================================
# CARREGAR merged_df.txt
# ============================================================

def carregar_arquivo(caminho):

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1"
    ]

    for encoding in encodings:

        try:

            df = pd.read_csv(
                caminho,
                sep=None,
                engine="python",
                encoding=encoding
            )

            print(
                f"Arquivo carregado com encoding: "
                f"{encoding}"
            )

            return df

        except Exception:
            pass

    raise RuntimeError(
        "Não foi possível carregar merged_df.txt"
    )


# ============================================================
# CRIAR NAVEGADOR
# ============================================================

def criar_navegador():

    options = webdriver.ChromeOptions()

    options.add_argument(
        "--start-maximized"
    )

    options.add_argument(
        "--disable-notifications"
    )

    driver = webdriver.Chrome(
        options=options
    )

    return driver


# ============================================================
# CLICAR EM ELEMENTO PELO TEXTO
# ============================================================

def clicar_texto(driver, texto):

    script = """
    const alvo = arguments[0]
        .trim()
        .toLowerCase();

    const elementos =
        Array.from(
            document.querySelectorAll("*")
        );

    const candidatos = [];

    for (const el of elementos) {

        const txt =
            (
                el.innerText ||
                el.textContent ||
                ""
            )
            .trim()
            .replace(/\\s+/g, " ")
            .toLowerCase();

        if (txt === alvo) {
            candidatos.push(el);
        }
    }

    // Prefere elemento clicável
    for (const el of candidatos) {

        const clicavel =
            el.closest(
                "button, a, label, [role='button']"
            );

        if (clicavel) {

            clicavel.scrollIntoView({
                block: "center"
            });

            clicavel.click();

            return true;
        }
    }

    // Última tentativa
    if (candidatos.length > 0) {

        const el =
            candidatos[
                candidatos.length - 1
            ];

        el.scrollIntoView({
            block: "center"
        });

        el.click();

        return true;
    }

    return false;
    """

    return driver.execute_script(
        script,
        texto
    )


# ============================================================
# PEGAR URLs CARREGADAS PELA PÁGINA
# ============================================================

def pegar_urls_recursos(driver):

    urls = driver.execute_script(
        """
        return performance
            .getEntriesByType("resource")
            .map(x => x.name);
        """
    )

    return list(
        dict.fromkeys(urls)
    )


# ============================================================
# EXTRAIR NOMES QUE ESTÃO VISÍVEIS NA TABELA
# ============================================================

def nomes_visiveis_tabela(driver):

    linhas = driver.find_elements(
        By.CSS_SELECTOR,
        "table tbody tr"
    )

    if not linhas:

        linhas = driver.find_elements(
            By.XPATH,
            "//tr[td]"
        )

    nomes = []

    for linha in linhas:

        try:

            celulas = linha.find_elements(
                By.TAG_NAME,
                "td"
            )

            # Pela página do IBGE:
            #
            # coluna 0 = posição
            # coluna 1 = nome
            # coluna 2 = percentual
            # coluna 3 = frequência

            if len(celulas) >= 2:

                nome = (
                    celulas[1]
                    .text
                    .strip()
                )

                if nome:
                    nomes.append(nome)

        except Exception:
            pass

    return nomes


# ============================================================
# SELECIONAR SEXO NA PÁGINA
# ============================================================

def selecionar_sexo(driver, sexo):

    print()
    print("=" * 60)
    print(
        f"Selecionando sexo: {sexo}"
    )
    print("=" * 60)

    driver.get(
        URL_IBGE
    )

    WebDriverWait(
        driver,
        30
    ).until(
        EC.presence_of_element_located(
            (
                By.TAG_NAME,
                "body"
            )
        )
    )

    # A página é dinâmica
    time.sleep(4)

    # --------------------------------------------------------
    # Tenta fechar cookies
    # --------------------------------------------------------

    for texto in [
        "Aceitar todos",
        "Aceitar",
        "Concordo",
        "OK"
    ]:

        try:
            clicar_texto(
                driver,
                texto
            )
        except Exception:
            pass

    # --------------------------------------------------------
    # Guarda URLs que já haviam sido carregadas
    # --------------------------------------------------------

    urls_antes = pegar_urls_recursos(
        driver
    )

    # --------------------------------------------------------
    # Abre o painel Sexo
    # --------------------------------------------------------

    clicar_texto(
        driver,
        "Sexo"
    )

    time.sleep(1)

    # --------------------------------------------------------
    # Clica Feminino ou Masculino
    # --------------------------------------------------------

    resultado = clicar_texto(
        driver,
        sexo
    )

    if not resultado:

        raise RuntimeError(
            f'Não consegui clicar em "{sexo}".'
        )

    print(
        f"✓ Botão encontrado: {sexo}"
    )

    # Dá tempo para o ranking atualizar
    time.sleep(4)

    # --------------------------------------------------------
    # Nomes que aparecem visualmente
    # --------------------------------------------------------

    nomes_tela = nomes_visiveis_tabela(
        driver
    )

    print()
    print(
        f"Primeiros nomes visíveis "
        f"para {sexo}:"
    )

    print(
        nomes_tela[:5]
    )

    if len(nomes_tela) < 5:

        raise RuntimeError(
            "Não consegui ler os nomes "
            "da tabela do IBGE."
        )

    # --------------------------------------------------------
    # URLs depois do clique
    # --------------------------------------------------------

    urls_depois = pegar_urls_recursos(
        driver
    )

    todas_urls = list(
        dict.fromkeys(
            urls_antes
            +
            urls_depois
        )
    )

    # --------------------------------------------------------
    # Mantém chamadas relacionadas ao ranking de nomes
    # --------------------------------------------------------

    candidatas = []

    for url in todas_urls:

        url_lower = url.lower()

        if (
            "servicodados.ibge.gov.br"
            in url_lower
            and
            "ranking"
            in url_lower
            and
            "nome"
            in url_lower
        ):

            candidatas.append(
                url
            )

    print()
    print(
        "Chamadas de ranking encontradas:",
        len(candidatas)
    )

    for url in candidatas:
        print("  ", url)

    if not candidatas:

        raise RuntimeError(
            "Não encontrei a chamada de ranking "
            "do IBGE entre os recursos da página."
        )

    return (
        candidatas,
        nomes_tela
    )


# ============================================================
# CRIAR SESSÃO HTTP
# ============================================================

def criar_sessao(driver):

    sessao = requests.Session()

    # User-Agent igual ao navegador aberto
    user_agent = driver.execute_script(
        "return navigator.userAgent;"
    )

    sessao.headers.update(
        {
            "User-Agent":
                user_agent,

            "Referer":
                "https://censo2022.ibge.gov.br/",

            "Accept":
                "application/json, text/plain, */*"
        }
    )

    # Copia cookies do navegador
    for cookie in driver.get_cookies():

        sessao.cookies.set(
            cookie["name"],
            cookie["value"]
        )

    return sessao


# ============================================================
# CONSULTAR UMA URL
# ============================================================

def consultar_json(sessao, url):

    resposta = sessao.get(
        url,
        timeout=30
    )

    resposta.raise_for_status()

    return resposta.json()


# ============================================================
# PEGAR ITEMS DE UMA RESPOSTA
# ============================================================

def extrair_items(dados):

    if isinstance(
        dados,
        dict
    ):

        if (
            "items"
            in dados
            and
            isinstance(
                dados["items"],
                list
            )
        ):

            return dados[
                "items"
            ]

    return []


# ============================================================
# COMPARAR NOMES DA API COM NOMES VISÍVEIS
# ============================================================

def assinatura_nomes(
    nomes
):

    return [
        normalizar(nome)
        for nome in nomes
    ]


def descobrir_url_correta(
    sessao,
    urls,
    nomes_tela,
    sexo
):

    assinatura_tela = assinatura_nomes(
        nomes_tela[:5]
    )

    print()
    print(
        f"Identificando chamada correta "
        f"para {sexo}..."
    )

    for url in urls:

        try:

            dados = consultar_json(
                sessao,
                url
            )

            items = extrair_items(
                dados
            )

            if len(items) < 5:
                continue

            nomes_api = []

            for item in items[:5]:

                if (
                    isinstance(
                        item,
                        dict
                    )
                    and
                    "nome"
                    in item
                ):

                    nomes_api.append(
                        item["nome"]
                    )

            if len(nomes_api) < 5:
                continue

            assinatura_api = assinatura_nomes(
                nomes_api
            )

            print(
                "Testando:"
            )

            print(
                " API :",
                nomes_api
            )

            print(
                " Tela:",
                nomes_tela[:5]
            )

            if (
                assinatura_api
                ==
                assinatura_tela
            ):

                print()
                print(
                    f"✓ URL correta encontrada "
                    f"para {sexo}"
                )

                print(
                    url
                )

                return url

        except Exception as erro:

            print(
                "Não foi possível testar:",
                url
            )

            print(
                "Motivo:",
                erro
            )

    raise RuntimeError(
        f"Não consegui identificar "
        f"a URL do ranking {sexo}."
    )


# ============================================================
# ALTERAR APENAS O PARÂMETRO page
# ============================================================

def trocar_pagina(
    url,
    pagina
):

    partes = urlsplit(
        url
    )

    parametros = dict(
        parse_qsl(
            partes.query,
            keep_blank_values=True
        )
    )

    parametros[
        "page"
    ] = str(
        pagina
    )

    nova_query = urlencode(
        parametros
    )

    return urlunsplit(
        (
            partes.scheme,
            partes.netloc,
            partes.path,
            nova_query,
            partes.fragment
        )
    )


# ============================================================
# BAIXAR 1000 NOMES
# ============================================================

def baixar_1000_nomes(
    sessao,
    url_base,
    sexo
):

    resultados = []

    pagina = 1

    while (
        len(resultados)
        <
        QUANTIDADE_POR_SEXO
    ):

        url = trocar_pagina(
            url_base,
            pagina
        )

        dados = consultar_json(
            sessao,
            url
        )

        items = extrair_items(
            dados
        )

        if not items:

            raise RuntimeError(
                f"Página {pagina} "
                f"de {sexo} não retornou nomes."
            )

        for item in items:

            if not isinstance(
                item,
                dict
            ):
                continue

            nome = item.get(
                "nome"
            )

            if not nome:
                continue

            resultados.append(
                {
                    "genero":
                        sexo.lower(),

                    "ranking":
                        item.get(
                            "rank",
                            len(resultados) + 1
                        ),

                    "nome":
                        nome,

                    "percentual_ibge":
                        item.get(
                            "percent"
                        ),

                    "frequencia_ibge":
                        item.get(
                            "frequencia"
                        )
                }
            )

            if (
                len(resultados)
                >=
                QUANTIDADE_POR_SEXO
            ):
                break

        print(
            f"{sexo}: "
            f"{len(resultados)}/"
            f"{QUANTIDADE_POR_SEXO}"
        )

        # ----------------------------------------------------
        # Segurança:
        # se a API disser que acabaram as páginas
        # antes de 1000, para.
        # ----------------------------------------------------

        total_paginas = (
            dados.get(
                "totalPages"
            )
            if isinstance(
                dados,
                dict
            )
            else None
        )

        if (
            total_paginas is not None
            and
            pagina >= int(
                total_paginas
            )
            and
            len(resultados)
            <
            QUANTIDADE_POR_SEXO
        ):

            raise RuntimeError(
                f"A API terminou em "
                f"{len(resultados)} nomes "
                f"para {sexo}."
            )

        pagina += 1

        # Não dispara chamadas agressivamente
        time.sleep(
            0.15
        )

    resultados = resultados[
        :QUANTIDADE_POR_SEXO
    ]

    return resultados


# ============================================================
# COLETAR UM SEXO COMPLETO
# ============================================================

def coletar_sexo(
    driver,
    sexo
):

    candidatas, nomes_tela = selecionar_sexo(
        driver,
        sexo
    )

    sessao = criar_sessao(
        driver
    )

    url_correta = descobrir_url_correta(
        sessao,
        candidatas,
        nomes_tela,
        sexo
    )

    resultados = baixar_1000_nomes(
        sessao,
        url_correta,
        sexo
    )

    if (
        len(resultados)
        !=
        QUANTIDADE_POR_SEXO
    ):

        raise RuntimeError(
            f"Esperava 1000 nomes "
            f"{sexo}, mas obtive "
            f"{len(resultados)}."
        )

    return resultados


# ============================================================
# CRIAR VOCABULÁRIO DA COLUNA Letra da Música
# ============================================================

def criar_vocabulario_letras(
    df
):

    print()
    print("=" * 60)
    print(
        'Analisando "Letra da Música"...'
    )
    print("=" * 60)

    vocabulario = set()

    total = len(
        df
    )

    for numero, letra in enumerate(
        df[COLUNA_LETRA]
        .fillna("")
        .astype(str),
        start=1
    ):

        letra = normalizar(
            letra
        )

        # Somente palavras inteiras.
        #
        # Portanto:
        #
        # ana != banana
        # lia != familia
        #
        palavras = re.findall(
            r"[a-z]+",
            letra
        )

        vocabulario.update(
            palavras
        )

        if (
            numero
            % 10000
            == 0
        ):

            print(
                f"{numero:,}/"
                f"{total:,} letras processadas"
            )

    print()
    print(
        f"Palavras únicas encontradas: "
        f"{len(vocabulario):,}"
    )

    return vocabulario


# ============================================================
# VERIFICAR SE CADA NOME APARECE
# ============================================================

def verificar_presenca(
    df_nomes,
    vocabulario
):

    presente = []

    for nome in df_nomes[
        "nome"
    ]:

        nome_normalizado = normalizar(
            nome
        )

        # Se eventualmente existir nome composto,
        # analisa cada nome como expressão inteira.
        #
        # Para nomes simples, usa o vocabulário.

        palavras_nome = re.findall(
            r"[a-z]+",
            nome_normalizado
        )

        if len(
            palavras_nome
        ) == 1:

            achou = (
                palavras_nome[0]
                in
                vocabulario
            )

        else:

            # Situação rara para esse ranking.
            # Exige que todas as partes existam.
            achou = all(
                palavra
                in
                vocabulario
                for palavra
                in palavras_nome
            )

        presente.append(
            "sim"
            if achou
            else "não"
        )

    df_nomes[
        "presente_na_Letra_da_Musica"
    ] = presente

    return df_nomes


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # 1. LER CORPUS
    # --------------------------------------------------------

    df = carregar_arquivo(
        ARQUIVO_ENTRADA
    )

    print()
    print(
        "Colunas encontradas:"
    )

    print(
        df.columns.tolist()
    )

    if (
        COLUNA_LETRA
        not in
        df.columns
    ):

        raise RuntimeError(
            f'A coluna "{COLUNA_LETRA}" '
            f"não foi encontrada."
        )

    print()
    print(
        f"Quantidade de músicas: "
        f"{len(df):,}"
    )

    # --------------------------------------------------------
    # 2. NAVEGADOR
    # --------------------------------------------------------

    driver = criar_navegador()

    try:

        # ----------------------------------------------------
        # 3. FEMININO
        # ----------------------------------------------------

        femininos = coletar_sexo(
            driver,
            "Feminino"
        )

        print()
        print(
            "✓ 1000 nomes femininos coletados."
        )

        # ----------------------------------------------------
        # 4. MASCULINO
        # ----------------------------------------------------

        masculinos = coletar_sexo(
            driver,
            "Masculino"
        )

        print()
        print(
            "✓ 1000 nomes masculinos coletados."
        )

    finally:

        driver.quit()

    # --------------------------------------------------------
    # 5. UNIR
    # --------------------------------------------------------

    df_nomes = pd.DataFrame(
        femininos
        +
        masculinos
    )

    # --------------------------------------------------------
    # 6. ORDENAR
    # --------------------------------------------------------

    df_nomes["ordem_genero"] = (
        df_nomes[
            "genero"
        ].map(
            {
                "feminino": 0,
                "masculino": 1
            }
        )
    )

    df_nomes = (
        df_nomes
        .sort_values(
            [
                "ordem_genero",
                "ranking"
            ]
        )
        .drop(
            columns=[
                "ordem_genero"
            ]
        )
        .reset_index(
            drop=True
        )
    )

    # --------------------------------------------------------
    # 7. VOCABULÁRIO DAS LETRAS
    # --------------------------------------------------------

    vocabulario = criar_vocabulario_letras(
        df
    )

    # --------------------------------------------------------
    # 8. VERIFICAR PRESENÇA
    # --------------------------------------------------------

    df_nomes = verificar_presenca(
        df_nomes,
        vocabulario
    )

    # --------------------------------------------------------
    # 9. SALVAR
    # --------------------------------------------------------

    df_nomes.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        encoding="utf-8-sig"
    )

    # --------------------------------------------------------
    # 10. RESULTADO
    # --------------------------------------------------------

    print()
    print("=" * 60)

    print(
        f"Arquivo salvo: "
        f"{ARQUIVO_SAIDA}"
    )

    print(
        f"Total de registros: "
        f"{len(df_nomes):,}"
    )

    print("=" * 60)

    print()
    print(
        "Quantidade por sexo:"
    )

    print(
        df_nomes[
            "genero"
        ].value_counts()
    )

    print()
    print(
        "Presença nas letras:"
    )

    print(
        df_nomes.groupby(
            [
                "genero",
                "presente_na_Letra_da_Musica"
            ]
        ).size()
    )


if __name__ == "__main__":
    main()