"""Testes para salvamento e carregamento de progresso (quadrix_progresso.json).

Usa um objeto mock em vez de uma instância completa de Tetris para não
depender de pygame inicializado.
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quadrix import save as save_module
from quadrix.save import salvar_progresso, carregar_progresso


class FakeJogo:
    """Mock do objeto Tetris apenas com os campos usados por save.py."""
    def __init__(self):
        self.conquistas = {
            "primeira_linha": {"desbloqueada": True},
            "dupla": {"desbloqueada": False},
            "tetris": {"desbloqueada": True},
        }
        self.recordes = {"CLÁSSICO": 1000, "SPRINT": 500, "ULTRA": 0}


def test_salvar_e_carregar_progresso():
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = os.path.join(tmpdir, "quadrix_progresso.json")
        save_module.PROGRESSO_SAVE_FILE = save_path

        jogo = FakeJogo()
        salvar_progresso(jogo)

        assert os.path.exists(save_path)

        with open(save_path, "r", encoding="utf-8") as f:
            dados = json.load(f)
        assert "conquistas" in dados
        assert "recordes" in dados
        assert dados["conquistas"]["primeira_linha"] is True
        assert dados["conquistas"]["dupla"] is False
        assert dados["recordes"]["CLÁSSICO"] == 1000

        jogo2 = FakeJogo()
        jogo2.conquistas = {
            "primeira_linha": {"desbloqueada": False},
            "dupla": {"desbloqueada": False},
            "tetris": {"desbloqueada": False},
        }
        jogo2.recordes = {"CLÁSSICO": 0, "SPRINT": 0, "ULTRA": 0}
        carregar_progresso(jogo2)

        assert jogo2.conquistas["primeira_linha"]["desbloqueada"] is True
        assert jogo2.conquistas["dupla"]["desbloqueada"] is False
        assert jogo2.conquistas["tetris"]["desbloqueada"] is True
        assert jogo2.recordes["CLÁSSICO"] == 1000


def test_carregar_arquivo_inexistente_nao_falha():
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = os.path.join(tmpdir, "nao_existe.json")
        save_module.PROGRESSO_SAVE_FILE = save_path

        jogo = FakeJogo()
        carregar_progresso(jogo)
        assert jogo.recordes["CLÁSSICO"] == 1000


if __name__ == "__main__":
    test_salvar_e_carregar_progresso()
    test_carregar_arquivo_inexistente_nao_falha()
    print("Todos os testes de save passaram.")
