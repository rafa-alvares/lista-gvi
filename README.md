# Lista GVI

Consulta da posição na lista de espera Standby GVI. A pessoa digita o nome de guerra e a base e vê a posição na fila, quantas pessoas estão à frente e a situação do idioma.

Site no ar: https://raphaalvares.pythonanywhere.com

## Como funciona

A lista chega em PDF. O `lista_gvi.py` lê o PDF com a biblioteca `pypdf`, separa cada linha em colunas (nome, data, cargo, SEN, base, idioma) com uma expressão regular e monta a fila de cada cargo e base. Entram na fila só as pessoas com idioma válido, na ordem de SEN.

A busca primeiro procura o nome exato. Se não achar, mostra quem tem uma palavra começando pelo que foi digitado ("ANA" encontra "ANA KARINA", mas não "ROSANA"). Acentos e apóstrofos são ignorados.

## Versões

| Pasta / arquivo | O que é |
|---|---|
| `main.py` | Versão de terminal. Vira o `Sistema_GVI.exe` com o PyInstaller. |
| `app.py` + `templates/` | Primeira versão web, para rodar no próprio computador. |
| `servidor/` | Versão web publicada no PythonAnywhere, com contador de acessos e página de estatísticas protegida por senha. |
| `lista_gvi.py` | Leitura do PDF e cálculo da fila, usado por todas as versões. |

## Rodar no computador

```
pip install pypdf flask
python main.py          # versão de terminal
python app.py           # versão web em http://127.0.0.1:5000
```

Coloque o PDF da lista na mesma pasta. O programa usa sempre o PDF mais recente.

## Gerar o executável

```
pip install pyinstaller
pyinstaller Sistema_GVI.spec
```

Ou dê dois cliques em `atualizar_sistema.bat`. O executável fica em `dist/`; coloque o PDF ao lado dele.

## Publicar

O passo a passo para o PythonAnywhere está em `servidor/PASSO_A_PASSO.md`. A senha das estatísticas fica só no arquivo WSGI do servidor, nunca neste repositório.

## Privacidade

Os PDFs da lista têm dados de outras pessoas e não fazem parte do repositório (veja o `.gitignore`). As estatísticas não guardam IP nem os nomes pesquisados.

---

Desenvolvido por Raphael Alvares
