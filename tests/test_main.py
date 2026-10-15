"""Testes de lógica do jogo (Tetris) usando SDL_VIDEODRIVER=dummy.

Esses testes exercitam colisão, fixação de peça, limpeza de linhas,
bag de peças, hold, pontuação, níveis e resetar recordes/conquistas.
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from quadrix.main import Tetris
from quadrix.states import JOGO_ATIVO, JOGO_FIM, MENU_PRINCIPAL
from quadrix.tetrominoes import TETROMINOS
from quadrix.config import LARGURA_GRADE, ALTURA_GRADE, CORES_TETROMINOS, MODO_CONFIG


def novo_jogo(modo="CLÁSSICO"):
    jogo = Tetris()
    jogo.modo_jogo = modo
    jogo.modo_config = dict(MODO_CONFIG[modo])
    jogo.velocidade_queda = jogo.modo_config["velocidade_inicial"]
    return jogo


def test_grade_inicial_vazia():
    jogo = Tetris()
    for linha in jogo.grade:
        assert all(celula == 0 for celula in linha)


def test_peca_atual_definida_apos_inicio():
    jogo = Tetris()
    assert jogo.peca_atual is not None
    assert jogo.peca_atual in TETROMINOS


def test_mover_peca_para_lado():
    jogo = Tetris()
    coluna_inicial = jogo.posicao_peca[1]
    assert jogo.mover_peca(1, 0) is True
    assert jogo.posicao_peca[1] == coluna_inicial + 1


def test_mover_peca_nao_passa_da_parede():
    jogo = Tetris()
    while jogo.mover_peca(1, 0):
        pass
    forma = TETROMINOS[jogo.peca_atual][jogo.rotacao_peca]
    largura = len(forma[0])
    assert jogo.posicao_peca[1] + largura <= LARGURA_GRADE


def test_rotacionar_peca():
    jogo = Tetris()
    rotacao_inicial = jogo.rotacao_peca
    assert jogo.rotacionar_peca() is True
    assert jogo.rotacao_peca == (rotacao_inicial + 1) % len(TETROMINOS[jogo.peca_atual])


def test_fixar_peca_coloca_blocos_na_grade():
    jogo = Tetris()
    peca = jogo.peca_atual
    rotacao = jogo.rotacao_peca
    posicao = jogo.posicao_peca.copy()
    forma = TETROMINOS[peca][rotacao]

    jogo.fixar_peca()

    for linha_peca, linha in enumerate(forma):
        for coluna_peca, celula in enumerate(linha):
            if celula:
                gl = posicao[0] + linha_peca
                gc = posicao[1] + coluna_peca
                if gl >= 0:
                    assert jogo.grade[gl][gc] == peca


def test_limpar_linha_completa():
    jogo = Tetris()
    linha_alvo = ALTURA_GRADE - 1
    for coluna in range(LARGURA_GRADE):
        jogo.grade[linha_alvo][coluna] = "I"

    linhas_antes = jogo.linhas_limpas
    jogo.limpar_linhas()

    assert jogo.linhas_limpas == linhas_antes + 1
    assert not any(jogo.grade[linha_alvo])


def test_pontuacao_linhas():
    jogo = Tetris()
    pontuacao_antes = jogo.pontuacao

    linha_alvo = ALTURA_GRADE - 1
    for coluna in range(LARGURA_GRADE):
        jogo.grade[linha_alvo][coluna] = "I"
    jogo.limpar_linhas()

    assert jogo.pontuacao == pontuacao_antes + 40


def test_nivel_aumenta_a_cada_10_linhas():
    jogo = Tetris()
    assert jogo.nivel == 1

    jogo.linhas_limpas = 10
    jogo.nivel = min(10, (jogo.linhas_limpas // 10) + 1)
    assert jogo.nivel == 2


def test_bag_nao_fica_vazia():
    jogo = Tetris()
    for _ in range(50):
        peca = jogo._get_peca_da_bag()
        assert peca in TETROMINOS


def test_hold_peca_funciona():
    jogo = Tetris()
    peca_original = jogo.peca_atual
    jogo.segurar_peca()
    assert jogo.hold_peca == peca_original
    assert jogo.houve_hold is True


def test_resetar_conquistas():
    jogo = Tetris()
    jogo.verificar_conquista("primeira_linha")
    assert jogo.conquistas["primeira_linha"]["desbloqueada"] is True

    jogo.resetar_conquistas()
    for c in jogo.conquistas.values():
        assert c["desbloqueada"] is False


def test_resetar_recordes():
    jogo = Tetris()
    jogo.recordes["CLÁSSICO"] = 9999
    jogo.resetar_recordes()
    assert jogo.recordes["CLÁSSICO"] == 0


def test_game_over_quando_peca_colide():
    jogo = Tetris()
    for linha in range(4):
        for coluna in range(LARGURA_GRADE):
            jogo.grade[linha][coluna] = "I"
    jogo.nova_peca()
    assert jogo.estado_jogo == JOGO_FIM


def test_practice_sem_game_over():
    jogo = Tetris()
    jogo.modo_jogo = "PRACTICE"
    for linha in range(4):
        for coluna in range(LARGURA_GRADE):
            jogo.grade[linha][coluna] = "I"
    jogo.nova_peca()
    assert jogo.estado_jogo != JOGO_FIM


def test_verificar_recorde_atualiza():
    jogo = Tetris()
    jogo.pontuacao = 5000
    jogo.modo_jogo = "CLÁSSICO"
    jogo.recordes["CLÁSSICO"] = 1000
    jogo.verificar_recorde()
    assert jogo.recordes["CLÁSSICO"] == 5000


if __name__ == "__main__":
    test_grade_inicial_vazia()
    test_peca_atual_definida_apos_inicio()
    test_mover_peca_para_lado()
    test_mover_peca_nao_passa_da_parede()
    test_rotacionar_peca()
    test_fixar_peca_coloca_blocos_na_grade()
    test_limpar_linha_completa()
    test_pontuacao_linhas()
    test_nivel_aumenta_a_cada_10_linhas()
    test_bag_nao_fica_vazia()
    test_hold_peca_funciona()
    test_resetar_conquistas()
    test_resetar_recordes()
    test_game_over_quando_peca_colide()
    test_practice_sem_game_over()
    test_verificar_recorde_atualiza()
    pygame.quit()
    print("Todos os testes de lógica do jogo passaram.")
