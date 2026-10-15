"""Testes para as constantes de configuração."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quadrix.config import (
    LARGURA_JANELA,
    ALTURA_JANELA,
    LARGURA_GRADE,
    ALTURA_GRADE,
    TAMANHO_BLOCO,
    MARGEM_X,
    MARGEM_Y,
    MODO_CONFIG,
    ICON_PATH,
    PROGRESSO_SAVE_FILE,
)
from quadrix.states import (
    JOGO_ATIVO,
    JOGO_PAUSADO,
    JOGO_FIM,
    MENU_PRINCIPAL,
    INSTRUCOES,
    OPCOES,
    RECORDES,
    CONQUISTAS,
    SELECIONAR_MODO,
    TUTORIAL,
    EXPLICACAO_MODO,
)


def test_dimensoes_janela():
    assert LARGURA_JANELA == 800
    assert ALTURA_JANELA == 700


def test_dimensoes_grade():
    assert LARGURA_GRADE == 10
    assert ALTURA_GRADE == 20
    assert TAMANHO_BLOCO == 30


def test_margens():
    assert MARGEM_X == (LARGURA_JANELA - LARGURA_GRADE * TAMANHO_BLOCO) // 2
    assert MARGEM_Y == 50


def test_modos_config():
    modos_esperados = {"CLÁSSICO", "MARATONA", "SPRINT", "ULTRA", "BLITZ", "PRACTICE"}
    assert set(MODO_CONFIG.keys()) == modos_esperados
    for modo, cfg in MODO_CONFIG.items():
        assert "descricao" in cfg
        assert "velocidade_inicial" in cfg
        assert cfg["velocidade_inicial"] > 0


def test_estados_unicos():
    estados = [
        JOGO_ATIVO, JOGO_PAUSADO, JOGO_FIM,
        MENU_PRINCIPAL, INSTRUCOES, OPCOES, RECORDES,
        CONQUISTAS, SELECIONAR_MODO, TUTORIAL, EXPLICACAO_MODO,
    ]
    assert len(estados) == len(set(estados)), "Estados devem ser únicos"
    assert JOGO_ATIVO == 0
    assert JOGO_FIM == 2
    assert MENU_PRINCIPAL == 3


def test_save_file_nome():
    assert PROGRESSO_SAVE_FILE == "quadrix_progresso.json"


def test_icon_path_relative():
    partes = ICON_PATH.parts
    assert "assets" in partes
    assert "images" in partes
    assert partes[-1] == "icon.png"


if __name__ == "__main__":
    test_dimensoes_janela()
    test_dimensoes_grade()
    test_margens()
    test_modos_config()
    test_estados_unicos()
    test_save_file_nome()
    test_icon_path_relative()
    print("Todos os testes de config passaram.")
