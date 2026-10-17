import os

from flask import Flask, render_template, request

from lista_gvi import (
    BASES_VALIDAS,
    buscar_por_nome,
    ler_lista,
    pdf_mais_recente,
    posicao_na_fila,
)

PASTA = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


def carregar():
    """Lê o PDF mais recente da pasta do projeto."""
    arquivo = pdf_mais_recente(PASTA)
    if arquivo is None:
        return None, [], ''
    pessoas, data_extracao = ler_lista(arquivo)
    return os.path.basename(arquivo), pessoas, data_extracao


def pagina(**dados):
    arquivo, pessoas, data_extracao = carregar()
    return render_template(
        'index.html',
        bases=BASES_VALIDAS,
        arquivo=arquivo,
        total=len(pessoas),
        data_extracao=data_extracao,
        **dados,
    )


@app.route('/')
def inicio():
    return pagina()


@app.route('/consultar', methods=['POST'])
def consultar():
    nome = request.form.get('nome', '').strip()
    base = request.form.get('base', '').upper().strip()
    sen = request.form.get('sen', '').strip()  # usado quando há nomes repetidos

    if not nome:
        return pagina(erro='Digite o nome de guerra.', base=base)
    if base not in BASES_VALIDAS:
        return pagina(erro='Escolha uma base válida.', nome=nome)

    arquivo, pessoas, _ = carregar()
    if arquivo is None:
        return pagina(erro='Nenhum arquivo PDF encontrado na pasta do projeto.')

    encontradas = buscar_por_nome(pessoas, nome, base)
    if sen:
        encontradas = [p for p in encontradas if p['sen'] == sen]

    if not encontradas:
        outras = buscar_por_nome(pessoas, nome)
        if outras:
            bases = ', '.join(sorted({p['base'] for p in outras}))
            erro = f'Nome não encontrado na base {base}. Ele aparece em: {bases}.'
        else:
            erro = 'Nome não existente na lista.'
        return pagina(erro=erro, nome=nome, base=base)

    if len(encontradas) > 1:
        return pagina(opcoes=encontradas, nome=nome, base=base)

    pessoa = encontradas[0]
    fila = posicao_na_fila(pessoas, pessoa)
    return pagina(pessoa=pessoa, fila=fila, nome=nome, base=base)


if __name__ == '__main__':
    app.run(debug=True)
