import os
import sys

from lista_gvi import (
    BASES_VALIDAS,
    buscar_por_nome,
    ler_lista,
    pdf_mais_recente,
    posicao_na_fila,
)


def pasta_do_programa():
    # Quando vira .exe (PyInstaller), o PDF fica ao lado do executável
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def sair(mensagem=''):
    if mensagem:
        print(mensagem)
    input('\nPressione Enter para sair...')
    sys.exit()


def escolher_pessoa(encontradas):
    """Se o nome digitado bater com mais de uma pessoa, pede para escolher."""
    if len(encontradas) == 1:
        return encontradas[0]

    print(f'\nEncontrei {len(encontradas)} pessoas com esse nome:')
    for i, p in enumerate(encontradas, start=1):
        print(f"  {i}. {p['nome']} - {p['cargo']} - SEN {p['sen']} - {p['base']}")

    while True:
        opcao = input('Digite o número da pessoa: ').strip()
        if opcao.isdigit() and 1 <= int(opcao) <= len(encontradas):
            return encontradas[int(opcao) - 1]
        print('Opção inválida.')


def mostrar_resultado(pessoa, fila, arquivo, data_extracao):
    print()
    print('==============================')
    print('       RESULTADO DA FILA')
    print('==============================')
    print('Nome:  ', pessoa['nome'])
    print('Cargo: ', pessoa['cargo'])
    print('SEN:   ', pessoa['sen'])
    print('Base:  ', pessoa['base'])
    print('Idioma:', pessoa['idioma'])
    print()

    if fila['idioma_valido']:
        print('Posição na fila: ', fila['posicao'])
        print('Pessoas à frente:', fila['a_frente'])
    else:
        print('ATENÇÃO: com idioma vencido você não entra na fila.')
        print('Com idioma válido, sua posição seria:', fila['posicao'])
        print('Pessoas à frente:', fila['a_frente'])

    print(f"Total na fila ({pessoa['cargo']} {pessoa['base']}, idioma válido):",
          fila['total_fila'])
    print()
    print('Arquivo analisado:', os.path.basename(arquivo))
    if data_extracao:
        print('Lista atualizada em:', data_extracao)
    print('==============================')


def main():
    print('Sistema de análise da lista GVI\n')

    arquivo = pdf_mais_recente(pasta_do_programa())
    if arquivo is None:
        sair('Nenhum arquivo PDF encontrado na pasta do programa.')

    pessoas, data_extracao = ler_lista(arquivo)
    if not pessoas:
        sair('Não consegui ler nenhuma pessoa nesse PDF. O formato da lista mudou?')

    print(f'Lista carregada: {len(pessoas)} pessoas', end='')
    print(f' (extraída em {data_extracao})' if data_extracao else '')
    print()

    nome = input('Digite seu nome de guerra: ').strip()
    if not nome:
        sair('Nome não informado.')

    base = input('Digite sua base (SP, RIO, POA, BSB, FOR): ').upper().strip()
    if base not in BASES_VALIDAS:
        sair('Base inválida. Escolha: ' + ', '.join(BASES_VALIDAS) + '.')

    encontradas = buscar_por_nome(pessoas, nome, base)
    if not encontradas:
        outras_bases = buscar_por_nome(pessoas, nome)
        if outras_bases:
            bases = sorted({p['base'] for p in outras_bases})
            sair(f'Nome não encontrado na base {base}. '
                 f'Ele aparece em: {", ".join(bases)}.')
        sair('Nome não existente na lista.')

    pessoa = escolher_pessoa(encontradas)
    fila = posicao_na_fila(pessoas, pessoa)
    mostrar_resultado(pessoa, fila, arquivo, data_extracao)
    sair()


if __name__ == '__main__':
    main()
