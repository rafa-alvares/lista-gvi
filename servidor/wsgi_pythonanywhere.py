# Copie TODO este conteúdo para o arquivo WSGI do PythonAnywhere
# (aba Web > "WSGI configuration file"), apagando o que estiver lá.
# Troque SEU_USUARIO e SUA_SENHA.

import os
import sys

os.environ['GVI_SENHA'] = 'SUA_SENHA'   # senha da página /estatisticas

pasta = '/home/SEU_USUARIO/projeto_gvi'
if pasta not in sys.path:
    sys.path.insert(0, pasta)

from app import app as application
