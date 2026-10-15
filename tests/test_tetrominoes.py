"""Testes para os dados de tetrominos (TETROMINOS e WALL_KICKS)."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quadrix.tetrominoes import TETROMINOS, WALL_KICKS
from quadrix.config import CORES_TETROMINOS


def test_tetrominos_tem_7_pecas():
    assert set(TETROMINOS.keys()) == {"I", "O", "T", "S", "Z", "J", "L"}


def test_cada_peca_tem_pelo_menos_uma_rotacao():
    for peca, rotacoes in TETROMINOS.items():
        assert len(rotacoes) >= 1, f"Peça {peca} sem rotações"


def test_piece_O_sem_wall_kicks():
    assert WALL_KICKS["O"] == {}


def test_todas_pecas_tem_cor():
    for peca in TETROMINOS:
        assert peca in CORES_TETROMINOS, f"Peça {peca} sem cor"
        cor = CORES_TETROMINOS[peca]
        assert len(cor) == 3
        assert all(0 <= c <= 255 for c in cor)


def test_forma_nao_vazia():
    for peca, rotacoes in TETROMINOS.items():
        for rotacao in rotacoes:
            tem_bloco = any(celula for linha in rotacao for celula in linha)
            assert tem_bloco, f"Peça {peca} rotação vazia"


if __name__ == "__main__":
    test_tetrominos_tem_7_pecas()
    test_cada_peca_tem_pelo_menos_uma_rotacao()
    test_piece_O_sem_wall_kicks()
    test_todas_pecas_tem_cor()
    test_forma_nao_vazia()
    print("Todos os testes de tetrominos passaram.")
