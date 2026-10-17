"""Consulta Lista GVI - versão web (Flask).

Roda no computador (python app.py) ou num servidor como o PythonAnywhere.

- O PDF mais recente da pasta é a lista usada.
- Cada acesso e cada consulta é contado num banco SQLite (estatisticas.db).
- /estatisticas mostra os números; só abre com a senha definida em GVI_SENHA.
"""

import hashlib
import hmac
import os
import sqlite3
from datetime import datetime, timedelta, timezone

from flask import Flask, Response, render_template, request

from lista_gvi import (
    BASES_VALIDAS,
    buscar_por_nome,
    fila_de,
    ler_lista,
    pdf_mais_recente,
    posicao_na_fila,
)

PASTA = os.path.dirname(os.path.abspath(__file__))
BANCO = os.path.join(PASTA, 'estatisticas.db')
FUSO_BRASILIA = timezone(timedelta(hours=-3))

# Senha da página de estatísticas. No PythonAnywhere ela é definida no
# arquivo WSGI (veja o PASSO_A_PASSO.md). Sem senha, a página fica fechada.
SENHA = os.environ.get('GVI_SENHA', '')

app = Flask(__name__)


# ---------------------------------------------------------------- lista ---

_cache = {'arquivo': None, 'mtime': None, 'pessoas': [], 'data': ''}


def carregar():
    """Lê o PDF mais recente, mas só de novo quando o arquivo muda."""
    arquivo = pdf_mais_recente(PASTA)
    if arquivo is None:
        return None, [], ''

    mtime = os.path.getmtime(arquivo)
    if arquivo != _cache['arquivo'] or mtime != _cache['mtime']:
        pessoas, data_extracao = ler_lista(arquivo)
        _cache.update(arquivo=arquivo, mtime=mtime,
                      pessoas=pessoas, data=data_extracao)

    return os.path.basename(arquivo), _cache['pessoas'], _cache['data']


def resumo_filas(pessoas):
    linhas = []
    for base in BASES_VALIDAS:
        linhas.append({
            'base': base,
            'aux': len(fila_de(pessoas, 'AUX', base)),
            'chc': len(fila_de(pessoas, 'CHC', base)),
            'vencido': sum(1 for p in pessoas
                           if p['base'] == base and p['idioma'] == 'VENCIDO'),
        })
    return linhas


# --------------------------------------------------------- estatísticas ---

def conectar():
    con = sqlite3.connect(BANCO)
    con.execute('''CREATE TABLE IF NOT EXISTS eventos (
                       quando  TEXT NOT NULL,   -- data e hora de Brasília
                       dia     TEXT NOT NULL,   -- AAAA-MM-DD
                       tipo    TEXT NOT NULL,   -- 'acesso' ou 'consulta'
                       visitante TEXT NOT NULL  -- código anônimo do visitante no dia
                   )''')
    return con


def visitante_anonimo(dia):
    """Código que identifica o visitante sem guardar o IP dele.

    O IP passa por um hash junto com o dia, então dá para contar
    visitantes diferentes, mas não dá para saber quem é.
    """
    ip = request.headers.get('X-Real-IP') or request.remote_addr or ''
    navegador = request.headers.get('User-Agent', '')
    bruto = f'{dia}|{ip}|{navegador}'.encode()
    return hashlib.sha256(bruto).hexdigest()[:16]


def registrar(tipo):
    agora = datetime.now(FUSO_BRASILIA)
    dia = agora.strftime('%Y-%m-%d')
    try:
        with conectar() as con:
            con.execute('INSERT INTO eventos VALUES (?, ?, ?, ?)',
                        (agora.strftime('%Y-%m-%d %H:%M'), dia, tipo,
                         visitante_anonimo(dia)))
    except sqlite3.Error:
        pass  # contar acesso nunca pode derrubar a consulta


def ler_estatisticas():
    with conectar() as con:
        total = dict(con.execute(
            'SELECT tipo, COUNT(*) FROM eventos GROUP BY tipo').fetchall())
        visitantes = con.execute(
            "SELECT COUNT(DISTINCT dia || visitante) FROM eventos").fetchone()[0]

        hoje = datetime.now(FUSO_BRASILIA).date()
        inicio = (hoje - timedelta(days=13)).isoformat()
        por_dia = {}
        for dia, tipo, qtd, unicos in con.execute(
                '''SELECT dia, tipo, COUNT(*), COUNT(DISTINCT visitante)
                   FROM eventos WHERE dia >= ? GROUP BY dia, tipo''', (inicio,)):
            linha = por_dia.setdefault(dia, {'acessos': 0, 'consultas': 0, 'visitantes': 0})
            if tipo == 'acesso':
                linha['acessos'] = qtd
                linha['visitantes'] = unicos
            else:
                linha['consultas'] = qtd

    dias = []
    for i in range(14):
        d = hoje - timedelta(days=i)
        valores = por_dia.get(d.isoformat(), {'acessos': 0, 'consultas': 0, 'visitantes': 0})
        dias.append({'dia': d.strftime('%d/%m'), **valores})

    return {
        'acessos': total.get('acesso', 0),
        'consultas': total.get('consulta', 0),
        'visitantes': visitantes,
        'dias': dias,
        'maior': max([d['acessos'] for d in dias] + [1]),
    }


def senha_correta():
    auth = request.authorization
    return bool(SENHA) and auth is not None and hmac.compare_digest(
        (auth.password or '').encode(), SENHA.encode())


# --------------------------------------------------------------- páginas ---

def pagina(**dados):
    arquivo, pessoas, data_extracao = carregar()
    return render_template(
        'index.html',
        bases=BASES_VALIDAS,
        arquivo=arquivo,
        total=len(pessoas),
        data_extracao=data_extracao,
        resumo=resumo_filas(pessoas),
        **dados,
    )


@app.route('/')
def inicio():
    registrar('acesso')
    return pagina(base='SP')


@app.route('/consultar', methods=['POST'])
def consultar():
    nome = request.form.get('nome', '').strip()
    base = request.form.get('base', '').upper().strip()
    sen = request.form.get('sen', '').strip()  # usado quando há nomes repetidos

    if not nome:
        return pagina(erro='Digite o nome de guerra.', base=base or 'SP')
    if base not in BASES_VALIDAS:
        return pagina(erro='Escolha uma base válida.', nome=nome, base='SP')

    arquivo, pessoas, _ = carregar()
    if arquivo is None:
        return pagina(erro='A lista ainda não foi carregada no servidor.')

    registrar('consulta')

    encontradas = buscar_por_nome(pessoas, nome, base)
    if sen:
        encontradas = [p for p in encontradas if p['sen'] == sen]

    if not encontradas:
        outras = buscar_por_nome(pessoas, nome)
        if outras:
            bases = ', '.join(sorted({p['base'] for p in outras}))
            erro = f'Não encontrei esse nome na base {base}. Ele aparece em: {bases}.'
        else:
            erro = 'Nome não encontrado na lista. Confira a grafia do nome de guerra.'
        return pagina(erro=erro, nome=nome, base=base)

    if len(encontradas) > 1:
        return pagina(opcoes=encontradas[:60], mais=len(encontradas) > 60,
                      total_opcoes=len(encontradas), nome=nome, base=base)

    pessoa = encontradas[0]
    fila = posicao_na_fila(pessoas, pessoa)
    progresso = 100
    if fila['total_fila']:
        progresso = max(2, round((1 - fila['a_frente'] / fila['total_fila']) * 100))
    return pagina(pessoa=pessoa, fila=fila, progresso=progresso, nome=nome, base=base)


@app.route('/estatisticas')
def estatisticas():
    if not SENHA:
        return Response('Página de estatísticas desativada: defina a senha GVI_SENHA.',
                        status=503, mimetype='text/plain; charset=utf-8')
    if not senha_correta():
        return Response('Senha necessária.', status=401,
                        headers={'WWW-Authenticate': 'Basic realm="Estatisticas GVI"'},
                        mimetype='text/plain; charset=utf-8')

    arquivo, pessoas, data_extracao = carregar()
    return render_template('estatisticas.html', est=ler_estatisticas(),
                           arquivo=arquivo, data_extracao=data_extracao)


if __name__ == '__main__':
    app.run(debug=True)
