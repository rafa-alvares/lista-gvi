# Colocar a Consulta Lista GVI no ar (PythonAnywhere)

O site vai ficar em `https://SEU_USUARIO.pythonanywhere.com`.
As estatísticas ficam em `https://SEU_USUARIO.pythonanywhere.com/estatisticas`
(pede usuário e senha: no usuário digite qualquer coisa, a senha é a que você definir).

## 1. Criar a conta
1. Acesse pythonanywhere.com e clique em **Pricing & signup**.
2. Escolha **Create a Beginner account** (gratuito).
3. O nome de usuário escolhido vira o endereço do site. Ex.: `raphaelgvi` → `raphaelgvi.pythonanywhere.com`.

## 2. Enviar os arquivos
1. No painel, abra a aba **Files**.
2. Em **Upload a file**, envie o `servidor_gvi.zip` (está na pasta `projeto_gvi\servidor`).
3. Abra a aba **Consoles** e clique em **Bash**. Na tela preta, digite:

```
unzip -o servidor_gvi.zip -d projeto_gvi
pip install --user pypdf
```

## 3. Criar o site
1. Abra a aba **Web** e clique em **Add a new web app** → **Next**.
2. Escolha **Manual configuration** (não escolha "Flask") e a versão mais nova do Python.
3. Na página que abre, procure **WSGI configuration file** e clique no link do arquivo.
4. Apague tudo o que estiver lá e cole o conteúdo do `wsgi_pythonanywhere.py`.
5. Troque `SEU_USUARIO` pelo seu usuário e `SUA_SENHA` pela senha que você quiser. Clique em **Save**.
6. Volte na aba **Web** e clique no botão verde **Reload**.
7. Abra o seu endereço. Pronto.

## Atualizar a lista
1. Aba **Files** → pasta `projeto_gvi` → **Upload a file** → envie o PDF novo.
2. Aba **Web** → **Reload**.

O site sempre usa o PDF enviado por último. Pode apagar os antigos pela aba Files.

## Atualizar o código
Envie o arquivo alterado para a pasta `projeto_gvi` (ou `projeto_gvi/templates`) e clique em **Reload**.

## Cuidados
- **Conta gratuita:** a cada 3 meses entre no painel, aba **Web**, e clique em
  **Run until 3 months from today**. Senão o site sai do ar (nada é apagado).
- **Senha:** fica só no arquivo WSGI, dentro da sua conta. Não coloque no GitHub.
- **Estatísticas:** ficam no arquivo `estatisticas.db`. Não apague se quiser manter o histórico.
- Ninguém além de você consegue ver o código Python, o PDF ou as estatísticas:
  os visitantes recebem só a página com o resultado da busca deles.
