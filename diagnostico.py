from __future__ import annotations

import importlib
import py_compile

ARQUIVOS = (
    "configuracoes.py",
    "ambiente.py",
    "organismos.py",
    "quadtree.py",
    "mundo.py",
    "main.py",
)

for arquivo in ARQUIVOS:
    print(f"[diagnostico] compilando {arquivo}")
    py_compile.compile(arquivo, doraise=True)

for modulo in (
    "configuracoes",
    "ambiente",
    "organismos",
    "quadtree",
    "mundo",
):
    print(f"[diagnostico] importando {modulo}")
    importlib.import_module(modulo)

from mundo import Mundo

print("[diagnostico] criando Mundo")
mundo = Mundo(semente=1)

print("[diagnostico] executando primeiro passo")
mundo.atualizar()

print("[diagnostico] estatisticas")
print(mundo.obter_estatisticas())
print("[diagnostico] OK")
