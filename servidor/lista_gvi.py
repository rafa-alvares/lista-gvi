"""Leitura e consulta da lista de espera GVI (PDF).

Módulo usado tanto pelo programa de terminal (main.py)
quanto pela versão web (app.py).
"""

import os
import re
import unicodedata

from pypdf import PdfReader

BASES_VALIDAS = ['SP', 'RIO', 'POA', 'BSB', 'FOR']

# Uma linha de pessoa no PDF tem sempre este formato:
# NOME DE GUERRA  DD/MM/AAAA HH:MM  CARGO  SEN  BASE  IDIOMA VÁLIDO|VENCIDO
# O cargo pode vir abreviado (CHC/AUX, listas até ago/26) ou por extenso
# (Chefe de Cabine/Auxiliar, a partir de out/26).
PADRAO_LINHA = re.compile(
    r'^(?P<nome>.+?) '
    r'(?P<data>\d{2}/\d{2}/\d{4}) (?P<hora>\d{2}:\d{2}) '
    r'(?P<cargo>AUX|CHC|Auxiliar|Chefe de Cabine) '
    r'(?P<sen>\d+) '
    r'(?P<base>SP|RIO|POA|BSB|FOR) '
    r'IDIOMA (?P<idioma>VÁLIDO|VENCIDO)$'
)

# Converte o cargo por extenso para a sigla usada no resto do sistema
CARGOS = {'CHEFE DE CABINE': 'CHC', 'AUXILIAR': 'AUX', 'CHC': 'CHC', 'AUX': 'AUX'}

PADRAO_EXTRACAO = re.compile(
    r'Dados extra[ií]dos em (\d{2}/\d{2}/\d{4}) às (\d{2}h\d{2})',
    re.IGNORECASE,
)


def normalizar(texto):
    """Maiúsculas, sem acentos, sem espaços repetidos e com apóstrofo simples."""
    texto = texto.replace('’', "'").replace('‘', "'")
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return ' '.join(texto.upper().split())


def pdf_mais_recente(pasta):
    """Devolve o caminho do PDF modificado mais recentemente na pasta, ou None."""
    pdfs = [
        os.path.join(pasta, arquivo)
        for arquivo in os.listdir(pasta)
        if arquivo.lower().endswith('.pdf')
    ]
    if not pdfs:
        return None
    return max(pdfs, key=os.path.getmtime)


def ler_lista(caminho_pdf):
    """Lê o PDF e devolve (pessoas, data_extracao).

    pessoas é uma lista de dicionários, na ordem do PDF (ordem de SEN).
    data_extracao é um texto como '11/08/2026 às 08h55' (ou '' se não achar).
    """
    leitor = PdfReader(caminho_pdf)
    texto = '\n'.join(pagina.extract_text() or '' for pagina in leitor.pages)

    data_extracao = ''
    achou = PADRAO_EXTRACAO.search(texto)
    if achou:
        data_extracao = f'{achou.group(1)} às {achou.group(2)}'

    pessoas = []
    for linha in texto.splitlines():
        combinou = PADRAO_LINHA.match(linha.strip())
        if combinou:
            pessoa = combinou.groupdict()
            pessoa['cargo'] = CARGOS[pessoa['cargo'].upper()]
            pessoa['nome_normalizado'] = normalizar(pessoa['nome'])
            pessoas.append(pessoa)

    return pessoas, data_extracao


def buscar_por_nome(pessoas, nome, base=None):
    """Procura pelo nome de guerra.

    Primeiro tenta o nome exato; se não houver, devolve quem contém o texto
    digitado (para o usuário escolher). Se a base for informada, filtra por ela.
    """
    nome = normalizar(nome)
    candidatas = [p for p in pessoas if base is None or p['base'] == base]

    exatas = [p for p in candidatas if p['nome_normalizado'] == nome]
    if exatas:
        return exatas

    # Busca parcial: cada palavra digitada precisa ser o começo de uma
    # palavra do nome ("ANA" acha "ANA KARINA", mas não "ROSANA").
    palavras_digitadas = nome.split()

    def combina(pessoa):
        palavras_nome = pessoa['nome_normalizado'].split()
        return all(
            any(palavra.startswith(digitada) for palavra in palavras_nome)
            for digitada in palavras_digitadas
        )

    return [p for p in candidatas if combina(p)]


def fila_de(pessoas, cargo, base):
    """Fila de quem disputa a vaga: mesmo cargo, mesma base e idioma válido."""
    return [
        p for p in pessoas
        if p['cargo'] == cargo and p['base'] == base and p['idioma'] == 'VÁLIDO'
    ]


def posicao_na_fila(pessoas, pessoa):
    """Calcula a posição da pessoa na fila do cargo/base dela.

    Para quem está com idioma vencido, informa a posição que teria
    se o idioma estivesse válido (quantos válidos têm SEN menor).
    """
    fila = fila_de(pessoas, pessoa['cargo'], pessoa['base'])

    if pessoa['idioma'] == 'VÁLIDO':
        posicao = fila.index(pessoa) + 1
    else:
        a_frente = [p for p in fila if int(p['sen']) < int(pessoa['sen'])]
        posicao = len(a_frente) + 1

    return {
        'posicao': posicao,
        'a_frente': posicao - 1,
        'total_fila': len(fila),
        'idioma_valido': pessoa['idioma'] == 'VÁLIDO',
    }
