import sys, os
from pathlib import Path
# isso aq resolveu gabi!!
file = Path(__file__).resolve()
parente, root = file.parent, file.parents[1]
sys.path.append(str(root))

from services import connection

# # Usa a função do módulo
# # connection.conectar()

print('arquivo importado')
