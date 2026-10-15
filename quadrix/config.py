"""Configurações e constantes do Quadrix."""

from pathlib import Path

# Diretórios do projeto (resolvidos relativos ao pacote, funciona em qualquer máquina)
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
ICON_PATH = ASSETS_DIR / "images" / "icon.png"

# Arquivo de salvamento unificado (conquistas + recordes)
PROGRESSO_SAVE_FILE = "quadrix_progresso.json"

# Configurações da janela
LARGURA_JANELA = 800
ALTURA_JANELA = 700
LARGURA_GRADE = 10
ALTURA_GRADE = 20
TAMANHO_BLOCO = 30
MARGEM_X = (LARGURA_JANELA - LARGURA_GRADE * TAMANHO_BLOCO) // 2
MARGEM_Y = 50

# Cores (R, G, B)
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
CINZA_CLARO = (200, 200, 200)
CINZA = (128, 128, 128)
CINZA_ESCURO = (64, 64, 64)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARELO = (255, 255, 0)
CIANO = (0, 255, 255)
MAGENTA = (255, 0, 255)
LARANJA = (255, 165, 0)
ROSA = (255, 192, 203)
AMARELO_CLARO = (255, 255, 150)

# Cores das peças do Tetris
CORES_TETROMINOS = {
    "I": CIANO,
    "O": AMARELO,
    "T": MAGENTA,
    "S": VERDE,
    "Z": VERMELHO,
    "J": AZUL,
    "L": LARANJA,
}

# Cores da interface (UI) - paleta expandida para uma aparência mais moderna
UI_FUNDO = (15, 20, 30)       # Fundo escuro dos painéis
UI_PAINEL = (35, 45, 65)      # Corpo dos painéis de interface
UI_BORDA = (110, 170, 240)    # Borda dos painéis
UI_TEXTO = (235, 240, 250)    # Texto primário da interface
UI_TEXTO_SUAVE = (170, 185, 215)  # Texto secundário / descrição
UI_DESTAQUE = (0, 240, 220)   # Destaque ciano (títulos / valores importantes)
UI_ACAO = (255, 90, 130)      # Destaque de ação (botões importantes / alertas)
UI_SUCESSO = (90, 245, 160)   # Destaque positivo (concluído / ativo)
UI_AVISO = (255, 210, 90)     # Destaque de aviso

# Configurações dos modos de jogo
MODO_CONFIG = {
    "CLÁSSICO": {
        "descricao": "O Tetris tradicional. Jogue até não haver mais espaço.",
        "velocidade_inicial": 0.5,
        "linhas_objetivo": None,
        "tempo_limite": None,
        "caos": False,
    },
    "MARATONA": {
        "descricao": "Jogo contínuo sem fim. A velocidade aumenta gradualmente.",
        "velocidade_inicial": 0.4,
        "linhas_objetivo": None,
        "tempo_limite": None,
        "caos": False,
    },
    "SPRINT": {
        "descricao": "Limpe 40 linhas o mais rápido possível.",
        "velocidade_inicial": 0.3,
        "linhas_objetivo": 40,
        "tempo_limite": None,
        "caos": False,
    },
    "ULTRA": {
        "descricao": "Jogue por 2 minutos e maximize sua pontuação.",
        "velocidade_inicial": 0.3,
        "linhas_objetivo": None,
        "tempo_limite": 120,
        "caos": False,
    },
    "BLITZ": {
        "descricao": "Velocidade muito rápida desde o início. Reflexos em ação!",
        "velocidade_inicial": 0.1,
        "linhas_objetivo": None,
        "tempo_limite": None,
        "caos": False,
    },
    "PRACTICE": {
        "descricao": "Modo treino. Sem game over, pratique à vontade.",
        "velocidade_inicial": 0.5,
        "linhas_objetivo": None,
        "tempo_limite": None,
        "caos": False,
    },
}
