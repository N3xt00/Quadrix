# Tetris Game in Python using Pygame
#
# Para instalar o pygame, execute:
# pip install pygame --break-system-packages
#
# Este é um jogo completo de Tetris com:
# - Interface gráfica usando pygame
# - Todas as 7 peças do Tetris (I, O, T, S, Z, J, L)
# - Movimentação e rotação das peças
# - Detecção de colisão
# - Sistema de limpeza de linhas com efeitos visuais
# - Pontuação e níveis com aumento de velocidade
# - Funcionalidade de pausa e reinício
# - Controle por teclado
# - Sistema de partículas para efeitos visuais aprimorados

import pygame
import sys
import random
import time
import math
import json


# Classe para representar partículas individuais
class Particle:
    def __init__(self, x, y, color, velocity=None, life=30):
        self.x = x
        self.y = y
        self.color = color
        self.life = life  # frames de vida
        self.max_life = life
        if velocity is None:
            # Velocidade aleatória em todas as direções
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            self.velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
        else:
            self.velocity = velocity

    def update(self):
        """Atualiza a posição e vida da partícula"""
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= 1
        # Aplicar alguma resistência do ar
        self.velocity[0] *= 0.98
        self.velocity[1] *= 0.98
        return self.life > 0

    def draw(self, surface):
        """Desenha a partícula na superfície"""
        if self.life <= 0:
            return

        # Calcular alpha baseado na vida restante (fade out)
        alpha = int(255 * (self.life / self.max_life))
        # Tornar a partícula menor à medida que envelhece
        size = max(1, int(3 * (self.life / self.max_life)))

        # Criar superfície com alpha
        particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (*self.color, alpha), (size, size), size)
        surface.blit(particle_surface, (int(self.x - size), int(self.y - size)))


# Sistema de partículas para gerenciar grupos de partículas
class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_particle(self, particle):
        """Adiciona uma partícula ao sistema"""
        self.particles.append(particle)

    def add_particles(self, count, x, y, color, velocity_range=None):
        """Adiciona múltiplas partículas com propriedades similares"""
        for _ in range(count):
            if velocity_range is None:
                velocity = None  # Velocidade aleatória
            else:
                velocity = [
                    random.uniform(velocity_range[0][0], velocity_range[0][1]),
                    random.uniform(velocity_range[1][0], velocity_range[1][1])
                ]
            particle = Particle(x, y, color, velocity)
            self.add_particle(particle)

    def update(self):
        """Atualiza todas as partículas e remove as mortas"""
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        """Desenha todas as partículas"""
        for particle in self.particles:
            particle.draw(surface)

    def clear(self):
        """Remove todas as partículas"""
        self.particles.clear()

# Configurações iniciais do pygame
pygame.init()

# Constantes do jogo
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
    'I': CIANO,
    'O': AMARELO,
    'T': MAGENTA,
    'S': VERDE,
    'Z': VERMELHO,
    'J': AZUL,
    'L': LARANJA
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

# Arquivo de salvamento unificado (conquistas + recordes)
PROGRESSO_SAVE_FILE = "quadrix_progresso.json"


# Formas das peças do Tetris (cada peça tem 4 rotações)
TETROMINOS = {
    'I': [
        [[0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],

        [[0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0]],

        [[0, 0, 0, 0],
         [0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0]],

        [[0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0]]
    ],

    'O': [
        [[1, 1],
         [1, 1]]
    ],

    'T': [
        [[0, 1, 0],
         [1, 1, 1],
         [0, 0, 0]],

        [[0, 1, 0],
         [0, 1, 1],
         [0, 1, 0]],

        [[0, 0, 0],
         [1, 1, 1],
         [0, 1, 0]],

        [[0, 1, 0],
         [1, 1, 0],
         [0, 1, 0]]
    ],

    'S': [
        [[0, 1, 1],
         [1, 1, 0],
         [0, 0, 0]],

        [[0, 1, 0],
         [0, 1, 1],
         [0, 0, 1]],

        [[0, 0, 0],
         [0, 1, 1],
         [1, 1, 0]],

        [[1, 0, 0],
         [1, 1, 0],
         [0, 1, 0]]
    ],

    'Z': [
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 0]],

        [[0, 0, 1],
         [0, 1, 1],
         [0, 1, 0]],

        [[0, 0, 0],
         [1, 1, 0],
         [0, 1, 1]],

        [[0, 1, 0],
         [1, 1, 0],
         [1, 0, 0]]
    ],

    'J': [
        [[1, 0, 0],
         [1, 1, 1],
         [0, 0, 0]],

        [[0, 1, 1],
         [0, 1, 0],
         [0, 1, 0]],

        [[0, 0, 0],
         [1, 1, 1],
         [0, 0, 1]],

        [[0, 1, 0],
         [0, 1, 0],
         [1, 1, 0]]
    ],

    'L': [
        [[0, 0, 1],
         [1, 1, 1],
         [0, 0, 0]],

        [[0, 1, 0],
         [0, 1, 0],
         [0, 1, 1]],

        [[0, 0, 0],
         [1, 1, 1],
         [1, 0, 0]],

        [[1, 1, 0],
         [0, 1, 0],
         [0, 1, 0]]
    ]
}

# Dados de wall kick para rotações (Sistema de Rotação Simplificado)
# Formato: {tipo_peça: { (rotacao_origem, rotacao_destino): [(dx, dy), ...] }}
WALL_KICKS = {
    'I': {
        (0, 1): [(-1, 0), (2, 0), (-1, 2), (2, -1)],
        (1, 0): [(1, 0), (-2, 0), (1, -2), (-2, 1)],
        (1, 2): [(-1, 0), (2, 0), (-1, 2), (2, -1)],
        (2, 1): [(1, 0), (-2, 0), (1, -2), (-2, 1)],
        (2, 3): [(1, 0), (-1, 0), (1, 2), (-1, -1)],
        (3, 2): [(-1, 0), (1, 0), (-1, -2), (1, 1)],
        (3, 0): [(-1, 0), (2, 0), (-1, 2), (2, -1)],
        (0, 3): [(1, 0), (-2, 0), (1, -2), (-2, 1)],
    },
    'J': {
        (0, 1): [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (1, 0): [(1, 0), (1, -1), (0, 2), (1, 2)],
        (1, 2): [(1, 0), (1, 1), (0, -2), (1, -2)],
        (2, 1): [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (2, 3): [(1, 0), (1, 1), (0, -2), (1, -2)],
        (3, 2): [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (3, 0): [(1, 0), (1, -1), (0, 2), (1, 2)],
        (0, 3): [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
    },
    'L': {
        (0, 1): [(1, 0), (1, -1), (0, 2), (1, 2)],
        (1, 0): [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (1, 2): [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (2, 1): [(1, 0), (1, 1), (0, -2), (1, -2)],
        (2, 3): [(1, 0), (1, -1), (0, 2), (1, 2)],
        (3, 2): [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (3, 0): [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (0, 3): [(1, 0), (1, 1), (0, -2), (1, -2)],
    },
    'S': {
        (0, 1): [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (1, 0): [(1, 0), (1, -1), (0, 2), (1, 2)],
        (1, 2): [(1, 0), (1, -1), (0, 2), (1, 2)],
        (2, 1): [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (2, 3): [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (3, 2): [(1, 0), (1, -1), (0, 2), (1, 2)],
        (3, 0): [(1, 0), (1, -1), (0, 2), (1, 2)],
        (0, 3): [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
    },
    'Z': {
        (0, 1): [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (1, 0): [(1, 0), (1, 1), (0, -2), (1, -2)],
        (1, 2): [(1, 0), (1, 1), (0, -2), (1, -2)],
        (2, 1): [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (2, 3): [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (3, 2): [(1, 0), (1, 1), (0, -2), (1, -2)],
        (3, 0): [(1, 0), (1, 1), (0, -2), (1, -2)],
        (0, 3): [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
    },
    'T': {
        (0, 1): [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
        (1, 0): [(1, 0), (1, -1), (0, 2), (1, 2)],
        (1, 2): [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
        (2, 1): [(1, 0), (1, 1), (0, -2), (1, 2)],
        (2, 3): [(1, 0), (1, -1), (0, 2), (1, 2)],
        (3, 2): [(-1, 0), (-1, -1), (0, 2), (-1, -2)],
        (3, 0): [(1, 0), (1, -1), (0, 2), (1, 2)],
        (0, 3): [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
    },
    # Peças O (quadrado) não precisam de wall kicks pois são simétricas
    'O': {}
}

# Configuração da janela do jogo
janela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
pygame.display.set_caption('Quadrix')
icone = pygame.image.load(r'C:\Users\gigam\AppData\Local\Temp\claude\c--Users-gigam-AppData-Local-Claude-3p-local-agent-mode-sessions-6325c982-00000000-6ad9c93c-outputs\d7e7b685-683c-4117-9412-fa25224f8103\images\2.png')
pygame.display.set_icon(icone)
relogio = pygame.time.Clock()

# Estados do jogo
JOGO_ATIVO = 0
JOGO_PAUSADO = 1
JOGO_FIM = 2
# Estados de menu e navegação
MENU_PRINCIPAL = 3
INSTRUCOES = 4
OPCOES = 5
RECORDES = 6
CONQUISTAS = 7
SELECIONAR_MODO = 8
TUTORIAL = 9
EXPLICACAO_MODO = 10  # Tela de explicação do modo selecionado

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

class Tetris:
    def __init__(self):
        self.grade = [[0 for _ in range(LARGURA_GRADE)] for _ in range(ALTURA_GRADE)]
        self.peca_atual = None
        self.peca_proxima = None
        self.posicao_peca = [0, 0]  # [linha, coluna]
        self.rotacao_peca = 0
        self.pontuacao = 0
        self.nivel = 1
        self.linhas_limpas = 0
        self.estado_jogo = MENU_PRINCIPAL  # Começa no menu principal
        self.tempo_queda_ultima = time.time()
        self.velocidade_queda = 0.5  # segundos por bloco (começa em 0.5s)
        # Sistemas de partículas para efeitos visuais
        self.particulas_linhas = ParticleSystem()  # Para linhas limpando
        self.particulas_impacto = ParticleSystem()  # Para peças fixando
        # Sistema de holding (peça para segurar)
        self.hold_peca = None  # Peça atualmente segurada
        self.hold_usado = False  # Se o holding já foi usado nesta troca (evita uso múltiplo)
        # Fila de peças próximas (mostrar 5 peças em vez de apenas 1)
        self.fila_proximas = []  # Fila com as próximas 5 peças
        # Sistema de peça fantasma (mostra onde a peça atual irá cair)
        self.posicao_fantasma = None  # Posição Y onde a peça atual irá cair
        # Sistema de lock delay suave
        self.lock_delay_timer = 0  # Timer para lock delay
        self.lock_delay_timeout = 0.5  # Lock delay timeout em segundos (500ms padrão)
        self.is_lock_delay_active = False  # Se o lock delay está ativo
        # Sistema de soft drop aprimorado
        self.soft_drop_active = False  # Se o soft drop está ativo (seta para baixo pressionada)
        self.soft_drop_speed = 0.05  # Velocidade do soft drop (mais rápido que queda normal)
        # Sistema de input buffering
        self.input_buffer = []  # Fila de comandos de entrada
        self.input_buffer_max_size = 3  # Tamanho máximo do buffer
        # Sistema de 7-bag para distribuição justa de peças
        self.bag = []  # Bag que contém as 7 peças
        self.refill_bag()  # Inicializa a bag
        # Modo de jogo selecionado (afeta regras e velocidade)
        self.modo_jogo = "CLÁSSICO"  # Modo padrão
        self.modo_config = MODO_CONFIG[self.modo_jogo]
        self.tempo_inicio: float | None = None  # Para modos com tempo (ULTRA)
        self.linhas_objetivo = self.modo_config["linhas_objetivo"]  # Para SPRINT
        self.jogo_vencido = False  # Para SPRINT/ULTRA
        # Variáveis para o menu
        self.menu_selecionado = 0  # Ítem atualmente selecionado no menu
        self.menu_opcoes = ["JOGAR", "INSTRUÇÕES", "RECORDES", "CONQUISTAS", "OPÇÕES", "SAIR"]
        self.modo_jogo_selecionado = 0  # Para o menu de seleção de modo
        self.modo_jogo_opcoes = ["CLÁSSICO", "MARATONA", "SPRINT", "ULTRA", "BLITZ", "PRACTICE"]
        # Menu de pausa
        self.menu_pausa_selecionado = 0  # Ítem selecionado no menu de pausa
        self.opcoes_pausa = ["VOLTAR AO JOGO", "REGRAS DO MODO", "REINICIAR", "SAIR"]
        self.explicacao_origem = SELECIONAR_MODO  # De onde a tela de explicação foi aberta
        self.menu_fim_jogo_selecionado = 0  # Ítem selecionado na tela de fim de jogo
        self.opcoes_fim_jogo = ["JOGAR NOVAMENTE", "VOLTAR AO MENU"]
        # Sistema de conquistas
        self.linhas_uma_vez_max = 0  # Maior quantidade de linhas limpas de uma vez
        self.houve_hold = False  # Se o jogador já usou o hold
        self.conquistas = {}  # id -> {nome, descricao, desbloqueada}
        self._inicializar_conquistas()
        # Alerta visual de conquista desbloqueada
        self.conquista_alerta_nome = None  # Nome da conquista recém-desbloqueada
        self.conquista_alerta_tempo = 0  # Tempo restante do alerta (segundos)
        self.rect_botao_reset_conquistas = None  # Rect do botão de resetar conquistas
        self.rect_botao_reset_recordes = None  # Rect do botão de resetar recordes
        # Variáveis de jogo (inicializadas quando o jogo começa)
        self.nova_peca()

    def _inicializar_conquistas(self):
        """Define todas as conquistas disponíveis no jogo"""
        self.conquistas = {
            "primeira_linha": {
                "nome": "Primeira Linha",
                "descricao": "Limpe sua primeira linha",
                "icone": "🔹",
                "desbloqueada": False,
            },
            "dupla": {
                "nome": "Dupla",
                "descricao": "Limpe 2 linhas de uma vez",
                "icone": "🔸",
                "desbloqueada": False,
            },
            "triplo": {
                "nome": "Triplo",
                "descricao": "Limpe 3 linhas de uma vez",
                "icone": "🔹",
                "desbloqueada": False,
            },
            "tetris": {
                "nome": "Tetris",
                "descricao": "Limpe 4 linhas de uma vez",
                "icone": "🔸",
                "desbloqueada": False,
            },
            "cem_linhas": {
                "nome": "Centurião",
                "descricao": "Limpe 100 linhas no total",
                "icone": "🔹",
                "desbloqueada": False,
            },
            "nivel_5": {
                "nome": "Nível 5",
                "descricao": "Alcance o nível 5",
                "icone": "🔸",
                "desbloqueada": False,
            },
            "nivel_10": {
                "nome": "Mestre",
                "descricao": "Alcance o nível 10",
                "icone": "🔹",
                "desbloqueada": False,
            },
            "hold": {
                "nome": "Segurar",
                "descricao": "Use o recurso de hold (peça segurada)",
                "icone": "🔸",
                "desbloqueada": False,
            },
            "sprint_completo": {
                "nome": "Sprinter",
                "descricao": "Complete o modo SPRINT",
                "icone": "🔹",
                "desbloqueada": False,
            },
            "ultra_sobrevivente": {
                "nome": "Sobrevivente Ultra",
                "descricao": "Sobreviva 2 minutos no modo ULTRA",
                "icone": "🔸",
                "desbloqueada": False,
            },
        }
        # Inicializa recordes por modo de jogo
        self.recordes = {modo: 0 for modo in self.modo_jogo_opcoes}
        # Carrega progresso salvo (conquistas + recordes), se existir
        self.carregar_progresso()

    def salvar_progresso(self):
        """Salva conquistas e recordes em arquivo JSON unificado"""
        dados = {
            "conquistas": {cid: c["desbloqueada"] for cid, c in self.conquistas.items()},
            "recordes": self.recordes,
        }
        try:
            with open(PROGRESSO_SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
        except OSError:
            pass  # Se não conseguir salvar, continua sem salvar

    def carregar_progresso(self):
        """Carrega conquistas e recordes do arquivo JSON unificado, se existir"""
        try:
            with open(PROGRESSO_SAVE_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
            for cid, desbloqueada in dados.get("conquistas", {}).items():
                if cid in self.conquistas:
                    self.conquistas[cid]["desbloqueada"] = desbloqueada
            for modo, recorde in dados.get("recordes", {}).items():
                if modo in self.recordes:
                    self.recordes[modo] = recorde
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass  # Sem arquivo salvo ou corrompido - mantém valores padrão

    def verificar_conquista(self, conquista_id):
        """Marca uma conquista como desbloqueada e salva o progresso"""
        if conquista_id in self.conquistas and not self.conquistas[conquista_id]["desbloqueada"]:
            self.conquistas[conquista_id]["desbloqueada"] = True
            self.conquista_alerta_nome = self.conquistas[conquista_id]["nome"]
            self.conquista_alerta_tempo = 4.0  # Alerta visível por 4 segundos
            self.salvar_progresso()

    def checar_conquistas(self):
        """Verifica todas as conquistas com base no estado atual do jogo"""
        if self.linhas_limpas >= 1:
            self.verificar_conquista("primeira_linha")
        if self.linhas_uma_vez_max >= 2:
            self.verificar_conquista("dupla")
        if self.linhas_uma_vez_max >= 3:
            self.verificar_conquista("triplo")
        if self.linhas_uma_vez_max >= 4:
            self.verificar_conquista("tetris")
        if self.linhas_limpas >= 100:
            self.verificar_conquista("cem_linhas")
        if self.nivel >= 5:
            self.verificar_conquista("nivel_5")
        if self.nivel >= 10:
            self.verificar_conquista("nivel_10")
        if self.houve_hold:
            self.verificar_conquista("hold")
        if self.modo_jogo == "SPRINT" and self.jogo_vencido:
            self.verificar_conquista("sprint_completo")
        if self.modo_jogo == "ULTRA" and self.tempo_inicio is not None:
            if time.time() - self.tempo_inicio >= 120:
                self.verificar_conquista("ultra_sobrevivente")

    def resetar_conquistas(self):
        """Reseta todas as conquistas para desbloqueada=False"""
        for conquista in self.conquistas.values():
            conquista["desbloqueada"] = False
        self.salvar_progresso()

    def resetar_recordes(self):
        """Reseta todos os recordes para 0"""
        for modo in self.recordes:
            self.recordes[modo] = 0
        self.salvar_progresso()

    def verificar_recorde(self):
        """Atualiza o recorde do modo atual se a pontuação atual for maior"""
        modo = self.modo_jogo
        if modo not in self.recordes:
            self.recordes[modo] = 0
        if self.pontuacao > self.recordes[modo]:
            self.recordes[modo] = self.pontuacao
            self.salvar_progresso()

    def refill_bag(self):
        """Reabastece e embaralha a bag com as 7 peças do Tetris"""
        try:
            self.bag = list(TETROMINOS.keys())
            if not self.bag:
                # Fallback if TETROMINOS is empty
                self.bag = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
            random.shuffle(self.bag)
        except Exception as e:
            # Fallback to default bag if anything goes wrong
            self.bag = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
            random.shuffle(self.bag)

    def _get_peca_da_bag(self):
        """Obtém uma peça da bag, reabastecendo se necessário"""
        try:
            if not self.bag:  # Se a bag está vazia, reabastece
                self.refill_bag()
            return self.bag.pop(0)  # Remove e retorna a primeira peça da bag
        except Exception as e:
            # If anything goes wrong, reset the bag and try again
            self.bag = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
            random.shuffle(self.bag)
            if self.bag:
                return self.bag.pop(0)
            else:
                # Last resort - return a default piece
                return 'I'

    def desenhar_menu(self, superficie):
        """Desenha o menu principal com visual moderno"""
        # Painel de fundo escuro
        painel = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
        painel.fill((0, 0, 0, 210))
        superficie.blit(painel, (0, 0))

        # Borda decorativa superior e inferior
        pygame.draw.rect(superficie, UI_BORDA, (0, 0, LARGURA_JANELA, 6))
        pygame.draw.rect(superficie, UI_BORDA, (0, ALTURA_JANELA - 6, LARGURA_JANELA, 6))

        # Título do jogo
        fonte_titulo = pygame.font.Font(None, 110)
        texto_titulo = fonte_titulo.render('QUADRIX', True, UI_DESTAQUE)
        texto_contorno = fonte_titulo.render('QUADRIX', True, PRETO)
        for dx in [-3, 0, 3]:
            for dy in [-3, 0, 3]:
                if dx != 0 or dy != 0:
                    superficie.blit(texto_contorno,
                                   (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2 + dx,
                                    ALTURA_JANELA // 4 - texto_titulo.get_height() // 2 + dy))
        superficie.blit(texto_titulo,
                       (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2,
                        ALTURA_JANELA // 4 - texto_titulo.get_height() // 2))

        # Subtítulo (abaixo do título, com espaçamento)
        fonte_sub = pygame.font.Font(None, 30)
        texto_sub = fonte_sub.render('O clássico dos blocos, com visual renovado', True, UI_TEXTO_SUAVE)
        superficie.blit(texto_sub,
                       (LARGURA_JANELA // 2 - texto_sub.get_width() // 2,
                        ALTURA_JANELA // 4 + 80))

        # Opções do menu (abaixo do subtítulo, espaçadas)
        fonte_opcao = pygame.font.Font(None, 44)
        espacamento = 50
        y_inicial = ALTURA_JANELA // 4 + 155

        for i, opcao in enumerate(self.menu_opcoes):
            y = y_inicial + i * espacamento
            if i == self.menu_selecionado:
                # Pastilha de seleção
                largura_pastilha = 340
                altura_pastilha = 48
                x_pastilha = LARGURA_JANELA // 2 - largura_pastilha // 2
                pygame.draw.rect(superficie, UI_PAINEL, (x_pastilha - 4, y - 14, largura_pastilha + 8, altura_pastilha + 8), border_radius=12)
                pygame.draw.rect(superficie, UI_BORDA, (x_pastilha - 4, y - 14, largura_pastilha + 8, altura_pastilha + 8), 2, border_radius=12)
                cor = UI_DESTAQUE
                indicador = "> "
            else:
                cor = UI_TEXTO
                indicador = "  "

            texto_opcao = fonte_opcao.render(indicador + opcao, True, cor)
            superficie.blit(texto_opcao,
                           (LARGURA_JANELA // 2 - texto_opcao.get_width() // 2,
                            y))

        # Instruções na parte inferior
        fonte_instrucoes = pygame.font.Font(None, 24)
        texto_controles = fonte_instrucoes.render("SETAS: navegar   ENTER: selecionar   ESC: sair", True, UI_TEXTO_SUAVE)
        superficie.blit(texto_controles,
                       (LARGURA_JANELA // 2 - texto_controles.get_width() // 2,
                        ALTURA_JANELA - 40))

    def desenhar_instrucoes(self, superficie):
        """Desenha a tela de instruções sem sobreposição de textos"""
        # Painel de fundo escuro
        painel = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
        painel.fill((0, 0, 0, 210))
        superficie.blit(painel, (0, 0))

        # Borda decorativa superior e inferior
        pygame.draw.rect(superficie, UI_BORDA, (0, 0, LARGURA_JANELA, 6))
        pygame.draw.rect(superficie, UI_BORDA, (0, ALTURA_JANELA - 6, LARGURA_JANELA, 6))

        # Título
        fonte_titulo = pygame.font.Font(None, 72)
        texto_titulo = fonte_titulo.render('COMO JOGAR', True, UI_DESTAQUE)
        superficie.blit(texto_titulo,
                       (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2,
                        30))

        fonte_secao = pygame.font.Font(None, 28)
        fonte_item = pygame.font.Font(None, 23)

        linhas = [
            ("secao", "OBJETIVO", UI_ACAO),
            ("item", "Complete linhas para ganhar pontos e evitar que as peças cheguem ao topo.", UI_TEXTO),
            ("vazio", None, None),
            ("secao", "CONTROLES", UI_ACAO),
            ("item", "SETA ESQUERDA / DIREITA: mover a peça", UI_TEXTO),
            ("item", "SETA BAIXO: soft drop (queda mais rápida)", UI_TEXTO),
            ("item", "SETA CIMA: rotacionar a peça (wall kicks)", UI_TEXTO),
            ("item", "ESPACO: queda rápida (hard drop)", UI_TEXTO),
            ("item", "C: segurar / trocar peça (hold)", UI_TEXTO),
            ("item", "P / ESC: pausar   R: reiniciar   Q: sair", UI_TEXTO),
            ("vazio", None, None),
            ("secao", "REGRAS", UI_ACAO),
            ("item", "Linhas completas somam pontos e somem", UI_TEXTO),
            ("item", "Mais linhas de uma vez = mais pontos (Tetris = 4)", UI_TEXTO),
            ("item", "O jogo acelera a cada nível alcançado", UI_TEXTO),
            ("item", "São mostradas as próximas 5 peças", UI_TEXTO),
            ("item", "Peça fantasma indica onde a peça atual cai", UI_TEXTO),
            ("item", "Lock delay permite ajustes antes de fixar", UI_TEXTO),
            ("item", "Hold troca a peça atual por uma guardada", UI_TEXTO),
        ]

        y = 100
        largura_max = LARGURA_JANELA - 80
        for tipo, texto, cor in linhas:
            if tipo == "vazio":
                y += 14
                continue
            fonte = fonte_secao if tipo == "secao" else fonte_item
            if tipo == "secao":
                texto_surf = fonte.render(texto, True, cor)
                largura = texto_surf.get_width()
                superficie.blit(texto_surf,
                               (LARGURA_JANELA // 2 - largura // 2,
                                y))
                y += 32
            else:
                # Quebra linhas longas para não ultrapassar a janela
                parte = ""
                for palavra in texto.split():
                    teste = (parte + " " + palavra).strip()
                    if fonte.size(teste)[0] <= largura_max:
                        parte = teste
                    else:
                        if parte:
                            ts = fonte.render(parte, True, cor)
                            largura = ts.get_width()
                            superficie.blit(ts,
                                           (LARGURA_JANELA // 2 - largura // 2,
                                            y))
                            y += 24
                        parte = palavra
                if parte:
                    ts = fonte.render(parte, True, cor)
                    largura = ts.get_width()
                    superficie.blit(ts,
                                   (LARGURA_JANELA // 2 - largura // 2,
                                    y))
                    y += 24

        # Rodapé
        fonte_rodape = pygame.font.Font(None, 24)
        texto_voltar = fonte_rodape.render("Pressione ESC para voltar ao menu", True, UI_SUCESSO)
        superficie.blit(texto_voltar,
                       (LARGURA_JANELA // 2 - texto_voltar.get_width() // 2,
                        ALTURA_JANELA - 35))

    def desenhar_opcoes(self, superficie):
        """Desenha a tela de opções com estilo do menu principal"""
        # Painel de fundo escuro
        painel = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
        painel.fill((0, 0, 0, 210))
        superficie.blit(painel, (0, 0))

        # Borda decorativa superior e inferior
        pygame.draw.rect(superficie, UI_BORDA, (0, 0, LARGURA_JANELA, 6))
        pygame.draw.rect(superficie, UI_BORDA, (0, ALTURA_JANELA - 6, LARGURA_JANELA, 6))

        # Título
        fonte_titulo = pygame.font.Font(None, 64)
        texto_titulo = fonte_titulo.render('OPÇÕES', True, UI_DESTAQUE)
        texto_contorno = fonte_titulo.render('OPÇÕES', True, PRETO)
        for dx in [-3, 0, 3]:
            for dy in [-3, 0, 3]:
                if dx != 0 or dy != 0:
                    superficie.blit(texto_contorno,
                                   (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2 + dx,
                                    ALTURA_JANELA // 4 - texto_titulo.get_height() // 2 + dy))
        superficie.blit(texto_titulo,
                       (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2,
                        ALTURA_JANELA // 4 - texto_titulo.get_height() // 2))

        # Subtítulo
        fonte_sub = pygame.font.Font(None, 30)
        texto_sub = fonte_sub.render('Configurações em desenvolvimento', True, UI_TEXTO_SUAVE)
        superficie.blit(texto_sub,
                       (LARGURA_JANELA // 2 - texto_sub.get_width() // 2,
                        ALTURA_JANELA // 4 + 80))

        # Opções de configuração (placeholders para implementação futura)
        fonte_opcao = pygame.font.Font(None, 32)
        opcoes = [
            "VOLUME DE SOM: [ TODO: Implementar slider ]",
            "VOLUME DE MÚSICA: [ TODO: Implementar slider ]",
            "CONTROLES: [ TODO: Implementar remapeamento ]",
            "TEMA VISUAL: [ TODO: Implementar seleção de tema ]",
            "DIFICULDADE: [ TODO: Implementar seleção de dificuldade ]",
            "",
            "ESTAS OPÇÕES ESTÃO EM DESENVOLVIMENTO"
        ]

        y_inicial = ALTURA_JANELA // 4 + 155
        espacamento = 45

        for i, linha in enumerate(opcoes):
            if linha == "":
                continue
            y = y_inicial + i * espacamento
            if "TODO" in linha:
                cor = UI_ACAO
            elif "DESENVOLVIMENTO" in linha:
                cor = UI_AVISO
            else:
                cor = UI_TEXTO

            texto_linha = fonte_opcao.render(linha, True, cor)
            superficie.blit(texto_linha,
                           (LARGURA_JANELA // 2 - texto_linha.get_width() // 2,
                            y))

        # Rodapé
        fonte_rodape = pygame.font.Font(None, 24)
        texto_voltar = fonte_rodape.render("Pressione ESC para voltar ao menu", True, UI_TEXTO_SUAVE)
        superficie.blit(texto_voltar,
                       (LARGURA_JANELA // 2 - texto_voltar.get_width() // 2,
                        ALTURA_JANELA - 40))

    def desenhar_recorde(self, superficie):
        """Desenha a tela de recordes com estilo do menu principal"""
        # Painel de fundo escuro
        painel = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
        painel.fill((0, 0, 0, 210))
        superficie.blit(painel, (0, 0))

        # Borda decorativa superior e inferior
        pygame.draw.rect(superficie, UI_BORDA, (0, 0, LARGURA_JANELA, 6))
        pygame.draw.rect(superficie, UI_BORDA, (0, ALTURA_JANELA - 6, LARGURA_JANELA, 6))

        # Título
        fonte_titulo = pygame.font.Font(None, 64)
        texto_titulo = fonte_titulo.render('RECORDES', True, UI_DESTAQUE)
        texto_contorno = fonte_titulo.render('RECORDES', True, PRETO)
        for dx in [-3, 0, 3]:
            for dy in [-3, 0, 3]:
                if dx != 0 or dy != 0:
                    superficie.blit(texto_contorno,
                                   (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2 + dx,
                                    ALTURA_JANELA // 4 - texto_titulo.get_height() // 2 + dy))
        superficie.blit(texto_titulo,
                       (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2,
                        ALTURA_JANELA // 4 - texto_titulo.get_height() // 2))

        # Subtítulo
        fonte_sub = pygame.font.Font(None, 30)
        texto_sub = fonte_sub.render('Maior pontuação por modo', True, UI_TEXTO_SUAVE)
        superficie.blit(texto_sub,
                       (LARGURA_JANELA // 2 - texto_sub.get_width() // 2,
                        ALTURA_JANELA // 4 + 80))

        # Lista de recordes por modo
        fonte_recorde = pygame.font.Font(None, 28)
        y_inicial = ALTURA_JANELA // 4 + 130
        espacamento = 40

        for i, modo in enumerate(self.modo_jogo_opcoes):
            recorde = self.recordes.get(modo, 0)
            texto_linha = fonte_recorde.render(f'{modo}: {recorde:>6}', True, UI_TEXTO)
            superficie.blit(texto_linha,
                           (LARGURA_JANELA // 2 - texto_linha.get_width() // 2,
                            y_inicial + i * espacamento))

        # Botão de resetar recordes
        largura_botao = 320
        altura_botao = 40
        x_botao = LARGURA_JANELA // 2 - largura_botao // 2
        y_botao = ALTURA_JANELA - 90
        self.rect_botao_reset_recordes = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
        pygame.draw.rect(superficie, UI_ACAO, self.rect_botao_reset_recordes, border_radius=8)
        pygame.draw.rect(superficie, UI_BORDA, self.rect_botao_reset_recordes, 2, border_radius=8)
        fonte_botao = pygame.font.Font(None, 28)
        texto_botao = fonte_botao.render("RESETAR RECORDES", True, BRANCO)
        superficie.blit(texto_botao,
                       (self.rect_botao_reset_recordes.centerx - texto_botao.get_width() // 2,
                        self.rect_botao_reset_recordes.centery - texto_botao.get_height() // 2))

        # Rodapé
        fonte_rodape = pygame.font.Font(None, 24)
        texto_voltar = fonte_rodape.render("ESC: Voltar   R: Resetar recordes", True, UI_TEXTO_SUAVE)
        superficie.blit(texto_voltar,
                       (LARGURA_JANELA // 2 - texto_voltar.get_width() // 2,
                        ALTURA_JANELA - 40))

    def desenhar_conquistas(self, superficie):
        """Desenha a tela de conquistas com estilo do menu principal"""
        # Painel de fundo escuro
        painel = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
        painel.fill((0, 0, 0, 210))
        superficie.blit(painel, (0, 0))

        # Borda decorativa superior e inferior
        pygame.draw.rect(superficie, UI_BORDA, (0, 0, LARGURA_JANELA, 6))
        pygame.draw.rect(superficie, UI_BORDA, (0, ALTURA_JANELA - 6, LARGURA_JANELA, 6))

        # Título
        fonte_titulo = pygame.font.Font(None, 64)
        texto_titulo = fonte_titulo.render('CONQUISTAS', True, UI_DESTAQUE)
        texto_contorno = fonte_titulo.render('CONQUISTAS', True, PRETO)
        for dx in [-3, 0, 3]:
            for dy in [-3, 0, 3]:
                if dx != 0 or dy != 0:
                    superficie.blit(texto_contorno,
                                   (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2 + dx,
                                    ALTURA_JANELA // 4 - texto_titulo.get_height() // 2 + dy))
        superficie.blit(texto_titulo,
                       (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2,
                        ALTURA_JANELA // 4 - texto_titulo.get_height() // 2))

        # Subtítulo com contagem de conquistas
        fonte_sub = pygame.font.Font(None, 30)
        total = len(self.conquistas)
        desbloqueadas = sum(1 for c in self.conquistas.values() if c["desbloqueada"])
        texto_sub = fonte_sub.render(f'Conquistas: {desbloqueadas}/{total}', True, UI_TEXTO_SUAVE)
        superficie.blit(texto_sub,
                       (LARGURA_JANELA // 2 - texto_sub.get_width() // 2,
                        ALTURA_JANELA // 4 + 80))

        # Lista de conquistas
        fonte_conquista = pygame.font.Font(None, 24)
        y_inicial = ALTURA_JANELA // 4 + 120
        espacamento = 30

        for i, (_, conquista) in enumerate(self.conquistas.items()):
            y = y_inicial + i * espacamento
            desbloqueada = conquista["desbloqueada"]
            cor = UI_DESTAQUE if desbloqueada else UI_TEXTO_SUAVE

            prefixo = "[OK] " if desbloqueada else "[  ] "
            texto = prefixo + conquista["nome"] + " - " + conquista["descricao"]
            texto_render = fonte_conquista.render(texto, True, cor)
            superficie.blit(texto_render,
                           (LARGURA_JANELA // 2 - texto_render.get_width() // 2, y))

        # Botão de resetar conquistas
        largura_botao = 320
        altura_botao = 40
        x_botao = LARGURA_JANELA // 2 - largura_botao // 2
        y_botao = ALTURA_JANELA - 90
        self.rect_botao_reset_conquistas = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
        pygame.draw.rect(superficie, UI_ACAO, self.rect_botao_reset_conquistas, border_radius=8)
        pygame.draw.rect(superficie, UI_BORDA, self.rect_botao_reset_conquistas, 2, border_radius=8)
        fonte_botao = pygame.font.Font(None, 28)
        texto_botao = fonte_botao.render("RESETAR CONQUISTAS", True, BRANCO)
        superficie.blit(texto_botao,
                       (self.rect_botao_reset_conquistas.centerx - texto_botao.get_width() // 2,
                        self.rect_botao_reset_conquistas.centery - texto_botao.get_height() // 2))

        # Rodapé
        fonte_rodape = pygame.font.Font(None, 24)
        texto_voltar = fonte_rodape.render("ESC: Voltar   R: Resetar conquistas", True, UI_TEXTO_SUAVE)
        superficie.blit(texto_voltar,
                       (LARGURA_JANELA // 2 - texto_voltar.get_width() // 2,
                        ALTURA_JANELA - 40))

    def desenhar_selecionar_modo(self, superficie):
        """Desenha a tela de seleção de modo de jogo com estilo do menu principal"""
        # Painel de fundo escuro
        painel = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
        painel.fill((0, 0, 0, 210))
        superficie.blit(painel, (0, 0))

        # Borda decorativa superior e inferior
        pygame.draw.rect(superficie, UI_BORDA, (0, 0, LARGURA_JANELA, 6))
        pygame.draw.rect(superficie, UI_BORDA, (0, ALTURA_JANELA - 6, LARGURA_JANELA, 6))

        # Título
        fonte_titulo = pygame.font.Font(None, 64)
        texto_titulo = fonte_titulo.render('SELECIONAR MODO', True, UI_DESTAQUE)
        texto_contorno = fonte_titulo.render('SELECIONAR MODO', True, PRETO)
        for dx in [-3, 0, 3]:
            for dy in [-3, 0, 3]:
                if dx != 0 or dy != 0:
                    superficie.blit(texto_contorno,
                                   (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2 + dx,
                                    ALTURA_JANELA // 4 - texto_titulo.get_height() // 2 + dy))
        superficie.blit(texto_titulo,
                       (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2,
                        ALTURA_JANELA // 4 - texto_titulo.get_height() // 2))

        # Subtítulo
        fonte_sub = pygame.font.Font(None, 30)
        texto_sub = fonte_sub.render('Escolha o modo de jogo', True, UI_TEXTO_SUAVE)
        superficie.blit(texto_sub,
                       (LARGURA_JANELA // 2 - texto_sub.get_width() // 2,
                        ALTURA_JANELA // 4 + 80))

        # Opções de modo com pastilha de seleção
        fonte_opcao = pygame.font.Font(None, 44)
        y_inicial = ALTURA_JANELA // 4 + 155
        espacamento = 40

        for i, modo in enumerate(self.modo_jogo_opcoes):
            y = y_inicial + i * espacamento
            if i == self.modo_jogo_selecionado:
                largura_pastilha = 300
                altura_pastilha = 48
                x_pastilha = LARGURA_JANELA // 2 - largura_pastilha // 2
                pygame.draw.rect(superficie, UI_PAINEL, (x_pastilha - 4, y - 14, largura_pastilha + 8, altura_pastilha + 8), border_radius=12)
                pygame.draw.rect(superficie, UI_BORDA, (x_pastilha - 4, y - 14, largura_pastilha + 8, altura_pastilha + 8), 2, border_radius=12)
                cor = UI_DESTAQUE
                indicador = "> "
            else:
                cor = UI_TEXTO
                indicador = "  "

            texto_modo = fonte_opcao.render(f"{indicador}{modo}", True, cor)
            superficie.blit(texto_modo,
                           (LARGURA_JANELA // 2 - texto_modo.get_width() // 2,
                            y))

        # Rodapé
        fonte_rodape = pygame.font.Font(None, 24)
        texto_voltar = fonte_rodape.render("ESC: Voltar ao menu   ENTER: Confirmar", True, UI_TEXTO_SUAVE)
        superficie.blit(texto_voltar,
                       (LARGURA_JANELA // 2 - texto_voltar.get_width() // 2,
                        ALTURA_JANELA - 40))

    def desenhar_explicacao_modo(self, superficie):
        """Desenha a tela de explicação do modo de jogo selecionado"""
        # Painel de fundo escuro
        painel = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
        painel.fill((0, 0, 0, 210))
        superficie.blit(painel, (0, 0))

        # Borda decorativa superior e inferior
        pygame.draw.rect(superficie, UI_BORDA, (0, 0, LARGURA_JANELA, 6))
        pygame.draw.rect(superficie, UI_BORDA, (0, ALTURA_JANELA - 6, LARGURA_JANELA, 6))

        # Título com o nome do modo
        fonte_titulo = pygame.font.Font(None, 64)
        modo_nome = self.modo_jogo
        texto_titulo = fonte_titulo.render(f'MODO: {modo_nome}', True, UI_DESTAQUE)
        texto_contorno = fonte_titulo.render(f'MODO: {modo_nome}', True, PRETO)
        for dx in [-3, 0, 3]:
            for dy in [-3, 0, 3]:
                if dx != 0 or dy != 0:
                    superficie.blit(texto_contorno,
                                   (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2 + dx,
                                    ALTURA_JANELA // 4 - texto_titulo.get_height() // 2 + dy))
        superficie.blit(texto_titulo,
                       (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2,
                        ALTURA_JANELA // 4 - texto_titulo.get_height() // 2))

        # Descrição do modo
        fonte_desc = pygame.font.Font(None, 32)
        descricao = self.modo_config["descricao"]
        texto_desc = fonte_desc.render(descricao, True, UI_TEXTO)
        superficie.blit(texto_desc,
                       (LARGURA_JANELA // 2 - texto_desc.get_width() // 2,
                        ALTURA_JANELA // 4 + 100))

        # Detalhes adicionais do modo
        fonte_detalhe = pygame.font.Font(None, 24)
        detalhes = []
        if self.modo_config["tempo_limite"]:
            detalhes.append(f"Tempo limite: {self.modo_config['tempo_limite']} segundos")
        if self.modo_config["linhas_objetivo"]:
            detalhes.append(f"Objetivo: limpar {self.modo_config['linhas_objetivo']} linhas")
        if self.modo_config["caos"]:
            detalhes.append("Modo CAOS: peças aparecem de forma imprevisível!")

        y_detalhe = ALTURA_JANELA // 4 + 150
        for detalhe in detalhes:
            texto_detalhe = fonte_detalhe.render(detalhe, True, UI_TEXTO_SUAVE)
            superficie.blit(texto_detalhe,
                           (LARGURA_JANELA // 2 - texto_detalhe.get_width() // 2,
                            y_detalhe))
            y_detalhe += 30

        # Rodapé
        fonte_rodape = pygame.font.Font(None, 24)
        texto_voltar = fonte_rodape.render("ESC: Voltar   ENTER: Iniciar jogo", True, UI_TEXTO_SUAVE)
        superficie.blit(texto_voltar,
                       (LARGURA_JANELA // 2 - texto_voltar.get_width() // 2,
                        ALTURA_JANELA - 40))

    def nova_peca(self):
        if self.peca_atual is None:
            # Primeira chamada - inicializa a fila com 5 peças da bag
            self.peca_atual = self._get_peca_da_bag()
            self.fila_proximas = [self._get_peca_da_bag() for _ in range(5)]
        else:
            # Remove a primeira peça da fila e coloca como peça atual
            self.peca_atual = self.fila_proximas.pop(0)
            # Adiciona uma nova peça da bag no final da fila
            self.fila_proximas.append(self._get_peca_da_bag())

        self.rotacao_peca = 0
        self.hold_usado = False  # Libera o hold novamente para a nova peça
        # Posiciona a peça no topo central da grade
        forma = TETROMINOS[self.peca_atual][self.rotacao_peca]
        self.posicao_peca = [0, (LARGURA_GRADE - len(forma[0])) // 2]

        # Calcula a posição fantasma da nova peça
        self.calcular_posicao_fantasma()

        # Verifica se o jogo acabou (se a nova peça colide imediatamente)
        # No modo PRACTICE não há game over - limpa o tabuleiro e reinicia as peças
        if self.verificar_colisao():
            if self.modo_jogo != "PRACTICE":
                self.verificar_recorde()
                self.estado_jogo = JOGO_FIM
            else:
                # Limpa o tabuleiro para permitir novas peças (sem game over)
                self.grade = [[0 for _ in range(LARGURA_GRADE)] for _ in range(ALTURA_GRADE)]
                self.calcular_posicao_fantasma()

    def segurar_peca(self):
        """Guarda a peça atual para uso futuro ou troca com a peça segurada"""
        # Se esta é a primeira vez segurando nesta troca
        if not self.hold_usado:
            if self.hold_peca is None:
                # Primeira vez segurando - guarda a peça atual e pega a próxima da fila
                self.hold_peca = self.peca_atual
                self.peca_atual = self.fila_proximas.pop(0)
                # Adiciona uma nova peça da bag no final da fila
                self.fila_proximas.append(self._get_peca_da_bag())
                # Reseta rotação e reposiciona a nova peça (evita IndexError se a nova peça
                # tiver menos rotações que a rotação anterior da peça antiga)
                self.rotacao_peca = 0
                self.posicao_peca = [0, (LARGURA_GRADE - len(TETROMINOS[self.peca_atual][0])) // 2]
            else:
                # Troca a peça atual com a peça segurada
                temp_peca = self.peca_atual
                self.peca_atual = self.hold_peca
                self.hold_peca = temp_peca
                # Reseta a rotação e posição da peça trocada
                self.rotacao_peca = 0
                self.posicao_peca = [0, (LARGURA_GRADE - len(TETROMINOS[self.peca_atual][0])) // 2]

                # Verifica se a troca causou colisão (game over se sim)
                # No modo PRACTICE não há game over - limpa o tabuleiro e reinicia as peças
                if self.verificar_colisao():
                    if self.modo_jogo != "PRACTICE":
                        self.verificar_recorde()
                        self.estado_jogo = JOGO_FIM
                    else:
                        # Limpa o tabuleiro para permitir novas peças (sem game over)
                        self.grade = [[0 for _ in range(LARGURA_GRADE)] for _ in range(ALTURA_GRADE)]
                        self.calcular_posicao_fantasma()

            # Marca que o holding foi usado nesta troca
            self.hold_usado = True
            # Marca que o jogador usou hold (para conquista)
            self.houve_hold = True

            # Calcula a posição fantasma após o holding
            self.calcular_posicao_fantasma()

            # Verifica conquistas após usar hold
            self.checar_conquistas()

    def adicionar_input_buffer(self, comando):
        """Adiciona um comando ao buffer de entrada para processamento posterior"""
        if len(self.input_buffer) < self.input_buffer_max_size:
            self.input_buffer.append(comando)
        # Se o buffer estiver cheio, ignora o comando mais antigo (FIFO)
        elif len(self.input_buffer) >= self.input_buffer_max_size:
            # Remove o comando mais antigo e adiciona o novo
            self.input_buffer.pop(0)
            self.input_buffer.append(comando)

    def _processar_input_buffer(self, comando):
        """Processa um comando do buffer de entrada"""
        if comando == 'ESQUERDA':
            self.mover_peca(-1, 0)
        elif comando == 'DIREITA':
            self.mover_peca(1, 0)
        elif comando == 'BAIXO':
            # Movimento para baixo (soft drop)
            if not self.verificar_colisao(posicao_adicional=[1, 0]):
                self.posicao_peca[0] += 1
                # Reseta o lock delay quando a peça se move livremente durante soft drop
                if self.is_lock_delay_active:
                    self.lock_delay_timer = time.time()
            # Se houver colisão, o lock delay será tratado na queda automática
        elif comando == 'CIMA':
            self.rotacionar_peca()
        elif comando == 'SEGURAR':
            self.segurar_peca()
        # Nota: Queda rápida (hard drop) e pausar/reiniciar são tratados diretamente no main()
        # pois são ações imediatas que não se beneficiam tanto do buffering

    def calcular_posicao_fantasma(self):
        """Calcula a posição onde a peça atual irá cair se solta imediatamente"""
        if self.peca_atual is None:
            return

        # Começa na posição atual da peça
        posicao_fantasma = self.posicao_peca.copy()

        # Move a peça fantasma para baixo até colidir.
        # verificar_colisao usa self.posicao_peca como base, portanto o offset
        # deve considerar a distância já percorrida pela fantasma mais a próxima linha.
        while not self.verificar_colisao(
            posicao_adicional=[posicao_fantasma[0] - self.posicao_peca[0] + 1, 0]
        ):
            posicao_fantasma[0] += 1

        self.posicao_fantasma = posicao_fantasma

    def verificar_colisao(self, posicao_adicional=None, rotacao_adicional=None):
        """Verifica se há colisão com as paredes ou outras peças"""
        if posicao_adicional is None:
            posicao_adicional = [0, 0]
        if rotacao_adicional is None:
            rotacao_adicional = 0

        forma = TETROMINOS[self.peca_atual][(self.rotacao_peca + rotacao_adicional) % len(TETROMINOS[self.peca_atual])]

        for linha_peca, linha in enumerate(forma):
            for coluna_peca, celula in enumerate(linha):
                if celula:
                    pos_linha = self.posicao_peca[0] + linha_peca + posicao_adicional[0]
                    pos_coluna = self.posicao_peca[1] + coluna_peca + posicao_adicional[1]

                    # Verifica colisão com as paredes
                    if pos_coluna < 0 or pos_coluna >= LARGURA_GRADE or pos_linha >= ALTURA_GRADE:
                        return True

                    # Verifica colisão com outras peças na grade
                    if pos_linha >= 0 and self.grade[pos_linha][pos_coluna]:
                        return True

        return False

    def fixar_peca(self):
        """Fixa a peça atual na grade e gera uma nova"""
        forma = TETROMINOS[self.peca_atual][self.rotacao_peca]

        for linha_peca, linha in enumerate(forma):
            for coluna_peca, celula in enumerate(linha):
                if celula:
                    pos_linha = self.posicao_peca[0] + linha_peca
                    pos_coluna = self.posicao_peca[1] + coluna_peca
                    if pos_linha >= 0:  # Só fixa se estiver dentro da grade visível
                        self.grade[pos_linha][pos_coluna] = self.peca_atual
                        # Gerar partículas de impacto para este bloco
                        cor = CORES_TETROMINOS[self.peca_atual]
                        # Posição central do bloco em coordenadas de tela
                        center_x = MARGEM_X + pos_coluna * TAMANHO_BLOCO + TAMANHO_BLOCO // 2
                        center_y = MARGEM_Y + pos_linha * TAMANHO_BLOCO + TAMANHO_BLOCO // 2
                        # Gerar pequenas partículas de impacto
                        self.particulas_impacto.add_particles(
                            8, center_x, center_y, cor,
                            velocity_range=[(-2, 2), (-2, 2)]
                        )

        # Limpa a posição fantasma pois a peça atual foi fixada
        self.posicao_fantasma = None
        self.limpar_linhas()
        self.nova_peca()

    def limpar_linhas(self):
        """Remove linhas completas e gera efeitos de partículas"""
        linhas_para_remover = []

        for linha in range(ALTURA_GRADE):
            if all(self.grade[linha]):
                linhas_para_remover.append(linha)

        # Se houver linhas para remover, gera efeitos de partículas
        if linhas_para_remover:
            # Gerar partículas de explosão para cada bloco nas linhas a serem removidas
            for linha in linhas_para_remover:
                for coluna in range(LARGURA_GRADE):
                    if self.grade[linha][coluna]:  # Se há um bloco nesta posição
                        cor = CORES_TETROMINOS[self.grade[linha][coluna]]
                        # Posição central do bloco em coordenadas de tela
                        center_x = MARGEM_X + coluna * TAMANHO_BLOCO + TAMANHO_BLOCO // 2
                        center_y = MARGEM_Y + linha * TAMANHO_BLOCO + TAMANHO_BLOCO // 2
                        # Gerar explosão de partículas
                        self.particulas_linhas.add_particles(
                            20, center_x, center_y, cor,
                            velocity_range=[(-3, 3), (-3, 3)]
                        )

            # Remove as linhas completas e move tudo acima para baixo
            for linha in reversed(linhas_para_remover):
                del self.grade[linha]
                self.grade.insert(0, [0 for _ in range(LARGURA_GRADE)])

            # Atualiza pontuação baseado nas linhas limpas
            self.linhas_limpas += len(linhas_para_remover)
            # Rastreia o máximo de linhas limpas de uma vez (para conquistas)
            if len(linhas_para_remover) > self.linhas_uma_vez_max:
                self.linhas_uma_vez_max = len(linhas_para_remover)
            # Pontuação clássica do Tetris: 40 * nível para 1 linha, 100 * nível para 2 linhas, etc.
            pontuacao_linhas = [0, 40, 100, 300, 1200]
            self.pontuacao += pontuacao_linhas[len(linhas_para_remover)] * self.nivel

            # Aumenta o nível a cada 10 linhas
            self.nivel = min(10, (self.linhas_limpas // 10) + 1)
            # Aumenta a velocidade conforme o nível aumenta (mínimo 0.05s)
            self.velocidade_queda = max(0.05, 0.5 - (self.nivel - 1) * 0.05)

            # Verifica conquistas após limpar linhas
            self.checar_conquistas()

    def mover_peca(self, dx, dy):
        """Tenta mover a peça na direção especificada"""
        if not self.verificar_colisao(posicao_adicional=[0, dx]):
            self.posicao_peca[1] += dx
            self.calcular_posicao_fantasma()
            # Reseta o lock delay quando a peça é movida horizontalmente durante o delay
            if self.is_lock_delay_active:
                self.lock_delay_timer = time.time()
            return True
        return False

    def rotacionar_peca(self):
        """Tenta rotacionar a peça com wall kicks"""
        if self.peca_atual is None:
            return False

        # Determina a nova rotação
        nova_rotacao = (self.rotacao_peca + 1) % len(TETROMINOS[self.peca_atual])

        # Tenta a rotação direta primeiro
        if not self.verificar_colisao(rotacao_adicional=1):
            self.rotacao_peca = nova_rotacao
            self.calcular_posicao_fantasma()
            # Reseta o lock delay quando a peça é rotacionada durante o delay
            if self.is_lock_delay_active:
                self.lock_delay_timer = time.time()
            return True

        # Se a rotação direta falhar, tenta os wall kicks
        if self.peca_atual in WALL_KICKS:
            kick_table = WALL_KICKS[self.peca_atual]
            kick_key = (self.rotacao_peca, nova_rotacao)

            if kick_key in kick_table:
                # Tenta cada offset de wall kick
                for kick_x, kick_y in kick_table[kick_key]:
                    if not self.verificar_colisao(posicao_adicional=[kick_y, kick_x], rotacao_adicional=1):
                        # Aplica o wall kick e a rotação (kick_y = deslocamento vertical/linha, kick_x = horizontal/coluna)
                        self.posicao_peca[0] += kick_y
                        self.posicao_peca[1] += kick_x
                        self.rotacao_peca = nova_rotacao
                        self.calcular_posicao_fantasma()
                        # Reseta o lock delay quando a peça é rotacionada durante o delay
                        if self.is_lock_delay_active:
                            self.lock_delay_timer = time.time()
                        return True

        return False

    def atualizar(self):
        """Atualiza o estado do jogo (queda automática da peça e animações)"""
        # Só atualiza a lógica do jogo quando está ativamente jogando
        if self.estado_jogo != JOGO_ATIVO:
            # Ainda atualiza os sistemas de partículas para efeitos contínuos nos menus
            self.particulas_linhas.update()
            self.particulas_impacto.update()
            return

        tempo_atual = time.time()

        # Atualiza timer do alerta de conquista
        if self.conquista_alerta_tempo > 0:
            self.conquista_alerta_tempo -= 1 / 60
            if self.conquista_alerta_tempo < 0:
                self.conquista_alerta_tempo = 0

        # Modo ULTRA: verifica se o tempo limite foi atingido
        if self.modo_jogo == "ULTRA" and self.tempo_inicio is not None:
            if tempo_atual - self.tempo_inicio >= self.modo_config["tempo_limite"]:
                self.checar_conquistas()  # Sobrevivente Ultra antes de encerrar
                self.verificar_recorde()
                self.estado_jogo = JOGO_FIM
                return

        # Modo SPRINT: verifica se o objetivo de linhas foi atingido
        if self.modo_jogo == "SPRINT" and self.linhas_objetivo is not None:
            if self.linhas_limpas >= self.linhas_objetivo:
                self.jogo_vencido = True
                self.checar_conquistas()  # Sprinter antes de encerrar
                self.verificar_recorde()
                self.estado_jogo = JOGO_FIM
                return

        # Atualiza sistemas de partículas
        self.particulas_linhas.update()
        self.particulas_impacto.update()

        # Processa o buffer de entrada (máximo 1 comando por atualização para evitar movimento muito rápido)
        if self.input_buffer and self.estado_jogo == JOGO_ATIVO:
            comando = self.input_buffer.pop(0)  # FIFO - processa o comando mais antigo primeiro
            self._processar_input_buffer(comando)

        # Determina a velocidade de queda (normal ou soft drop)
        velocidade_queda_atual = self.soft_drop_speed if self.soft_drop_active else self.velocidade_queda

        # Queda automática da peça com lock delay suave
        if tempo_atual - self.tempo_queda_ultima > velocidade_queda_atual:
            if not self.verificar_colisao(posicao_adicional=[1, 0]):
                self.posicao_peca[0] += 1
                # Reseta o lock delay quando a peça se move livremente
                self.is_lock_delay_active = False
                self.lock_delay_timer = 0
            else:
                # Colisão detectada - inicia ou continua o lock delay
                if not self.is_lock_delay_active:
                    # Inicia o lock delay
                    self.is_lock_delay_active = True
                    self.lock_delay_timer = tempo_atual
                else:
                    # Verifica se o lock delay expirou
                    if tempo_atual - self.lock_delay_timer > self.lock_delay_timeout:
                        self.fixar_peca()
                        self.is_lock_delay_active = False
                        self.lock_delay_timer = 0
            self.tempo_queda_ultima = tempo_atual

    def desenhar_grade(self, superficie):
        """Desenha a grade do jogo com bordas, quadriculado e efeitos visuais"""
        # Desenha o fundo da grade com borda dupla
        pygame.draw.rect(superficie, CINZA_ESCURO,
                        (MARGEM_X - 4, MARGEM_Y - 4,
                         LARGURA_GRADE * TAMANHO_BLOCO + 8,
                         ALTURA_GRADE * TAMANHO_BLOCO + 8))
        pygame.draw.rect(superficie, CINZA_CLARO,
                        (MARGEM_X - 2, MARGEM_Y - 2,
                         LARGURA_GRADE * TAMANHO_BLOCO + 4,
                         ALTURA_GRADE * TAMANHO_BLOCO + 4))

        # Desenha o quadriculado (linhas da grade) para melhor visualização
        for linha in range(ALTURA_GRADE + 1):
            pygame.draw.line(superficie, CINZA,
                           (MARGEM_X, MARGEM_Y + linha * TAMANHO_BLOCO),
                           (MARGEM_X + LARGURA_GRADE * TAMANHO_BLOCO, MARGEM_Y + linha * TAMANHO_BLOCO),
                           1)
        for coluna in range(LARGURA_GRADE + 1):
            pygame.draw.line(superficie, CINZA,
                           (MARGEM_X + coluna * TAMANHO_BLOCO, MARGEM_Y),
                           (MARGEM_X + coluna * TAMANHO_BLOCO, MARGEM_Y + ALTURA_GRADE * TAMANHO_BLOCO),
                           1)

        # Desenha os blocos fixos na grade
        for linha in range(ALTURA_GRADE):
            for coluna in range(LARGURA_GRADE):
                if self.grade[linha][coluna]:
                    cor = CORES_TETROMINOS[self.grade[linha][coluna]]
                    # Efeito de brilho nos blocos
                    pygame.draw.rect(superficie, cor,
                                   (MARGEM_X + coluna * TAMANHO_BLOCO,
                                    MARGEM_Y + linha * TAMANHO_BLOCO,
                                    TAMANHO_BLOCO, TAMANHO_BLOCO))
                    pygame.draw.rect(superficie, BRANCO,
                                   (MARGEM_X + coluna * TAMANHO_BLOCO + 2,
                                    MARGEM_Y + linha * TAMANHO_BLOCO + 2,
                                    TAMANHO_BLOCO - 4, TAMANHO_BLOCO - 4))
                    pygame.draw.rect(superficie, BRANCO,
                                   (MARGEM_X + coluna * TAMANHO_BLOCO,
                                    MARGEM_Y + linha * TAMANHO_BLOCO,
                                    TAMANHO_BLOCO, TAMANHO_BLOCO), 1)

        # Desenha a peça fantasma (preview de onde a peça irá cair)
        if self.posicao_fantasma is not None and self.estado_jogo == JOGO_ATIVO:
            forma_fantasma = TETROMINOS[self.peca_atual][self.rotacao_peca]
            cor_fantasma = CORES_TETROMINOS[self.peca_atual]
            # Cor fantasma mais transparente para destacar a posição de pouso
            cor_fantasma_transparente = (*cor_fantasma, 90)  # RGBA com 90/255 de opacidade

            # Superfície temporária para desenhar com transparência
            superficie_fantasma = pygame.Surface(
                (LARGURA_GRADE * TAMANHO_BLOCO, ALTURA_GRADE * TAMANHO_BLOCO), pygame.SRCALPHA)

            for linha_peca, linha in enumerate(forma_fantasma):
                for coluna_peca, celula in enumerate(linha):
                    if celula:
                        x = (self.posicao_fantasma[1] + coluna_peca) * TAMANHO_BLOCO
                        y = (self.posicao_fantasma[0] + linha_peca) * TAMANHO_BLOCO

                        # Bloco fantasma com contorno branco para destacar bordas
                        pygame.draw.rect(superficie_fantasma, cor_fantasma_transparente,
                                       (x, y, TAMANHO_BLOCO, TAMANHO_BLOCO))
                        pygame.draw.rect(superficie_fantasma, BRANCO,
                                       (x, y, TAMANHO_BLOCO, TAMANHO_BLOCO), 2)

            # Desenha a superfície fantasma na tela principal (aplica a margem da grade)
            superficie.blit(superficie_fantasma, (MARGEM_X, MARGEM_Y))

        # Desenha os sistemas de partículas
        self.particulas_linhas.draw(superficie)
        self.particulas_impacto.draw(superficie)

    def desenhar_peca(self, superficie, peca=None, posicao=None, rotacao=None, offset_x=0, offset_y=0):
        """Desenha uma peça na superfície especificada com efeito 3D"""
        if peca is None:
            peca = self.peca_atual
        if posicao is None:
            posicao = self.posicao_peca
        if rotacao is None:
            rotacao = self.rotacao_peca

        forma = TETROMINOS[peca][rotacao]
        cor = CORES_TETROMINOS[peca]

        for linha_peca, linha in enumerate(forma):
            for coluna_peca, celula in enumerate(linha):
                if celula:
                    x = MARGEM_X + (posicao[1] + coluna_peca) * TAMANHO_BLOCO + offset_x
                    y = MARGEM_Y + (posicao[0] + linha_peca) * TAMANHO_BLOCO + offset_y

                    # Efeito 3D: bloco mais claro no topo e esquerda, mais escuro na base e direita
                    pygame.draw.rect(superficie, cor, (x, y, TAMANHO_BLOCO, TAMANHO_BLOCO))
                    # Brilho no topo e esquerda
                    pygame.draw.line(superficie,
                                   tuple(min(255, c + 30) for c in cor),
                                   (x, y), (x + TAMANHO_BLOCO - 1, y), 2)
                    pygame.draw.line(superficie,
                                   tuple(min(255, c + 30) for c in cor),
                                   (x, y), (x, y + TAMANHO_BLOCO - 1), 2)
                    # Sombra na base e direita
                    pygame.draw.line(superficie,
                                   tuple(max(0, c - 30) for c in cor),
                                   (x, y + TAMANHO_BLOCO - 1),
                                   (x + TAMANHO_BLOCO - 1, y + TAMANHO_BLOCO - 1), 2)
                    pygame.draw.line(superficie,
                                   tuple(max(0, c - 30) for c in cor),
                                   (x + TAMANHO_BLOCO - 1, y),
                                   (x + TAMANHO_BLOCO - 1, y + TAMANHO_BLOCO - 1), 2)
                    # Contorno branco
                    pygame.draw.rect(superficie, BRANCO, (x, y, TAMANHO_BLOCO, TAMANHO_BLOCO), 1)

    def desenhar_peca_mini(self, superficie, peca, rotacao, offset_x=0, offset_y=0, tamanho_bloco=8):
        """Desenha uma peça pequena (pré-visualização) em posição de pixels"""
        forma = TETROMINOS[peca][rotacao]
        cor = CORES_TETROMINOS[peca]
        for linha_peca, linha in enumerate(forma):
            for coluna_peca, celula in enumerate(linha):
                if celula:
                    x = offset_x + coluna_peca * tamanho_bloco
                    y = offset_y + linha_peca * tamanho_bloco
                    pygame.draw.rect(superficie, cor, (x, y, tamanho_bloco, tamanho_bloco))
                    pygame.draw.rect(superficie, BRANCO, (x, y, tamanho_bloco, tamanho_bloco), 1)

    def desenhar_interface(self, superficie):
        """Desenha a interface do jogo com painéis organizados e sem sobreposição"""
        # Painel de pontuação (esquerda)
        painel_largura = 200
        painel_altura = 175
        pygame.draw.rect(superficie, UI_PAINEL, (10, 10, painel_largura, painel_altura), border_radius=10)
        pygame.draw.rect(superficie, UI_BORDA, (10, 10, painel_largura, painel_altura), 2, border_radius=10)

        fonte_titulo = pygame.font.Font(None, 28)
        fonte_valor = pygame.font.Font(None, 36)
        fonte_pequena = pygame.font.Font(None, 22)

        # Título
        texto_titulo = fonte_titulo.render('QUADRIX', True, UI_DESTAQUE)
        superficie.blit(texto_titulo, (20, 20))

        # Pontuação
        texto_pontuacao_label = fonte_pequena.render('PONTUAÇÃO', True, UI_TEXTO_SUAVE)
        superficie.blit(texto_pontuacao_label, (20, 58))
        texto_pontuacao_valor = fonte_valor.render(f'{self.pontuacao:>6}', True, UI_DESTAQUE)
        superficie.blit(texto_pontuacao_valor, (20, 84))

        # Nível
        texto_nivel_label = fonte_pequena.render('NÍVEL', True, UI_TEXTO_SUAVE)
        superficie.blit(texto_nivel_label, (20, 124))
        texto_nivel_valor = fonte_valor.render(f'{self.nivel:>2}', True, UI_SUCESSO)
        superficie.blit(texto_nivel_valor, (20, 150))

        # Linhas
        texto_linhas_label = fonte_pequena.render('LINHAS', True, UI_TEXTO_SUAVE)
        superficie.blit(texto_linhas_label, (20, 218))
        texto_linhas_valor = fonte_valor.render(f'{self.linhas_limpas:>3}', True, UI_ACAO)
        superficie.blit(texto_linhas_valor, (20, 244))

        # Tempo (modo ULTRA)
        if self.modo_jogo == "ULTRA" and self.tempo_inicio is not None:
            tempo_restante = max(0, self.modo_config["tempo_limite"] - (time.time() - self.tempo_inicio))
            minutos = int(tempo_restante // 60)
            segundos = int(tempo_restante % 60)
            texto_tempo_label = fonte_pequena.render('TEMPO', True, UI_TEXTO_SUAVE)
            superficie.blit(texto_tempo_label, (20, 278))
            texto_tempo_valor = fonte_valor.render(f'{minutos:02d}:{segundos:02d}', True, UI_AVISO)
            superficie.blit(texto_tempo_valor, (20, 304))

        # --- Próximas peças (zona superior direita) ---
        texto_proximas_label = fonte_titulo.render('PRÓXIMAS', True, UI_DESTAQUE)
        superficie.blit(texto_proximas_label, (LARGURA_JANELA - 160, 20))

        quadro_largura = 46
        quadro_altura = 46
        quadro_x = LARGURA_JANELA - 80
        quadro_y_inicial = 60
        espacamento = 56

        for i, proxima_peca in enumerate(self.fila_proximas[:5]):
            quadro_y = quadro_y_inicial + i * espacamento
            # Fundo do quadro
            pygame.draw.rect(superficie, UI_FUNDO, (quadro_x - 2, quadro_y - 2, quadro_largura + 4, quadro_altura + 4), border_radius=6)
            pygame.draw.rect(superficie, UI_PAINEL, (quadro_x, quadro_y, quadro_largura, quadro_altura), border_radius=6)
            pygame.draw.rect(superficie, UI_BORDA, (quadro_x, quadro_y, quadro_largura, quadro_altura), 2, border_radius=6)

            # Peça centralizada no quadro
            forma_proxima = TETROMINOS[proxima_peca][0]
            bloco_prev = 7
            largura_preview = len(forma_proxima[0]) * bloco_prev
            altura_preview = len(forma_proxima) * bloco_prev
            inicio_x = quadro_x + (quadro_largura - largura_preview) // 2
            inicio_y = quadro_y + (quadro_altura - altura_preview) // 2
            self.desenhar_peca_mini(superficie, proxima_peca, 0, inicio_x, inicio_y, bloco_prev)

        # --- Peça segurada (zona inferior direita, separada das próximas) ---
        texto_held_label = fonte_titulo.render('SEGURAR', True, UI_DESTAQUE)
        superficie.blit(texto_held_label, (LARGURA_JANELA - 160, 370))

        held_quadro_largura = 100
        held_quadro_altura = 100
        held_quadro_x = LARGURA_JANELA - 140
        held_quadro_y = 395
        pygame.draw.rect(superficie, UI_FUNDO, (held_quadro_x - 2, held_quadro_y - 2, held_quadro_largura + 4, held_quadro_altura + 4), border_radius=8)
        pygame.draw.rect(superficie, UI_PAINEL, (held_quadro_x, held_quadro_y, held_quadro_largura, held_quadro_altura), border_radius=8)
        pygame.draw.rect(superficie, UI_BORDA, (held_quadro_x, held_quadro_y, held_quadro_largura, held_quadro_altura), 2, border_radius=8)

        if self.hold_peca is not None:
            forma_held = TETROMINOS[self.hold_peca][0]
            bloco_held = 14
            held_largura_preview = len(forma_held[0]) * bloco_held
            held_altura_preview = len(forma_held) * bloco_held
            held_inicio_x = held_quadro_x + (held_quadro_largura - held_largura_preview) // 2
            held_inicio_y = held_quadro_y + (held_quadro_altura - held_altura_preview) // 2
            self.desenhar_peca_mini(superficie, self.hold_peca, 0, held_inicio_x, held_inicio_y, bloco_held)
        else:
            fonte_vazio = pygame.font.Font(None, 20)
            texto_vazio = fonte_vazio.render("VAZIO", True, UI_TEXTO_SUAVE)
            superficie.blit(texto_vazio,
                           (held_quadro_x + held_quadro_largura // 2 - texto_vazio.get_width() // 2,
                            held_quadro_y + held_quadro_altura // 2 - texto_vazio.get_height() // 2))

def desenhar_tela_pausa(superficie, jogo):
    """Desenha o menu de pausa com estilo do menu principal"""
    # Painel de fundo escuro
    painel = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
    painel.fill((0, 0, 0, 210))
    superficie.blit(painel, (0, 0))

    # Borda decorativa superior e inferior
    pygame.draw.rect(superficie, UI_BORDA, (0, 0, LARGURA_JANELA, 6))
    pygame.draw.rect(superficie, UI_BORDA, (0, ALTURA_JANELA - 6, LARGURA_JANELA, 6))

    # Título "PAUSADO"
    fonte_titulo = pygame.font.Font(None, 96)
    texto_titulo = fonte_titulo.render('PAUSADO', True, UI_DESTAQUE)
    texto_contorno = fonte_titulo.render('PAUSADO', True, PRETO)
    for dx in [-3, 0, 3]:
        for dy in [-3, 0, 3]:
            if dx != 0 or dy != 0:
                superficie.blit(texto_contorno,
                               (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2 + dx,
                                ALTURA_JANELA // 4 - texto_titulo.get_height() // 2 + dy))
    superficie.blit(texto_titulo,
                   (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2,
                    ALTURA_JANELA // 4 - texto_titulo.get_height() // 2))

    # Subtítulo
    fonte_sub = pygame.font.Font(None, 30)
    texto_sub = fonte_sub.render('O jogo está pausado', True, UI_TEXTO_SUAVE)
    superficie.blit(texto_sub,
                   (LARGURA_JANELA // 2 - texto_sub.get_width() // 2,
                    ALTURA_JANELA // 4 + 80))

    # Opções selecionáveis com pastilha de seleção
    fonte_opcao = pygame.font.Font(None, 44)
    y_inicial = ALTURA_JANELA // 4 + 155
    espacamento = 50

    for i, opcao in enumerate(jogo.opcoes_pausa):
        y = y_inicial + i * espacamento
        if i == jogo.menu_pausa_selecionado:
            largura_pastilha = 340
            altura_pastilha = 48
            x_pastilha = LARGURA_JANELA // 2 - largura_pastilha // 2
            pygame.draw.rect(superficie, UI_PAINEL, (x_pastilha - 4, y - 14, largura_pastilha + 8, altura_pastilha + 8), border_radius=12)
            pygame.draw.rect(superficie, UI_BORDA, (x_pastilha - 4, y - 14, largura_pastilha + 8, altura_pastilha + 8), 2, border_radius=12)
            cor = UI_DESTAQUE
            indicador = "> "
        else:
            cor = UI_TEXTO
            indicador = "  "

        texto_opcao = fonte_opcao.render(indicador + opcao, True, cor)
        superficie.blit(texto_opcao,
                       (LARGURA_JANELA // 2 - texto_opcao.get_width() // 2,
                        y))

    # Dica de controles
    fonte_dica = pygame.font.Font(None, 24)
    texto_dica = fonte_dica.render("SETAS: navegar   ENTER: selecionar   ESC: voltar ao jogo", True, UI_TEXTO_SUAVE)
    superficie.blit(texto_dica,
                   (LARGURA_JANELA // 2 - texto_dica.get_width() // 2,
                    ALTURA_JANELA - 40))

def desenhar_tela_fim_jogo(superficie, jogo):
    """Desenha a tela de fim de jogo com estatísticas e menu de opções"""
    # Painel de fundo escuro
    painel = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
    painel.fill((0, 0, 0, 210))
    superficie.blit(painel, (0, 0))

    # Borda decorativa superior e inferior
    pygame.draw.rect(superficie, UI_BORDA, (0, 0, LARGURA_JANELA, 6))
    pygame.draw.rect(superficie, UI_BORDA, (0, ALTURA_JANELA - 6, LARGURA_JANELA, 6))

    # Título "FIM DE JOGO"
    fonte_titulo = pygame.font.Font(None, 96)
    texto_titulo = fonte_titulo.render('FIM DE JOGO', True, UI_DESTAQUE)
    texto_contorno = fonte_titulo.render('FIM DE JOGO', True, PRETO)
    for dx in [-3, 0, 3]:
        for dy in [-3, 0, 3]:
            if dx != 0 or dy != 0:
                superficie.blit(texto_contorno,
                               (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2 + dx,
                                ALTURA_JANELA // 4 - texto_titulo.get_height() // 2 + dy))
    superficie.blit(texto_titulo,
                   (LARGURA_JANELA // 2 - texto_titulo.get_width() // 2,
                    ALTURA_JANELA // 4 - texto_titulo.get_height() // 2))

    # Subtítulo
    fonte_sub = pygame.font.Font(None, 30)
    texto_sub = fonte_sub.render('Sua jornada acabou', True, UI_TEXTO_SUAVE)
    superficie.blit(texto_sub,
                   (LARGURA_JANELA // 2 - texto_sub.get_width() // 2,
                    ALTURA_JANELA // 4 + 80))

    # Painel de estatísticas (stats cards)
    fonte_stats = pygame.font.Font(None, 28)
    stats = [
        ("PONTUAÇÃO", f'{jogo.pontuacao}', UI_DESTAQUE),
        ("MODO", jogo.modo_jogo, UI_SUCESSO),
        ("NÍVEL", str(jogo.nivel), UI_AVISO),
        ("LINHAS LIMPAS", str(jogo.linhas_limpas), UI_TEXTO),
    ]
    card_largura = 170
    card_altura = 50
    card_espacamento = 15
    total_largura = len(stats) * card_largura + (len(stats) - 1) * card_espacamento
    x_inicial = LARGURA_JANELA // 2 - total_largura // 2
    y_stats = ALTURA_JANELA // 2 - 40

    for i, (label, valor, cor) in enumerate(stats):
        x_card = x_inicial + i * (card_largura + card_espacamento)
        # Fundo do card
        pygame.draw.rect(superficie, UI_PAINEL, (x_card, y_stats, card_largura, card_altura), border_radius=10)
        pygame.draw.rect(superficie, UI_BORDA, (x_card, y_stats, card_largura, card_altura), 2, border_radius=10)
        # Label
        texto_label = fonte_stats.render(label, True, UI_TEXTO_SUAVE)
        superficie.blit(texto_label,
                       (x_card + card_largura // 2 - texto_label.get_width() // 2,
                        y_stats + 12))
        # Valor
        texto_valor = fonte_stats.render(valor, True, cor)
        superficie.blit(texto_valor,
                       (x_card + card_largura // 2 - texto_valor.get_width() // 2,
                        y_stats + 30))

    # Opções do menu com pastilha de seleção
    fonte_opcao = pygame.font.Font(None, 44)
    y_inicial = ALTURA_JANELA // 2 + 80
    espacamento = 55

    for i, opcao in enumerate(jogo.opcoes_fim_jogo):
        y = y_inicial + i * espacamento
        if i == jogo.menu_fim_jogo_selecionado:
            largura_pastilha = 320
            altura_pastilha = 48
            x_pastilha = LARGURA_JANELA // 2 - largura_pastilha // 2
            pygame.draw.rect(superficie, UI_PAINEL, (x_pastilha - 4, y - 14, largura_pastilha + 8, altura_pastilha + 8), border_radius=12)
            pygame.draw.rect(superficie, UI_BORDA, (x_pastilha - 4, y - 14, largura_pastilha + 8, altura_pastilha + 8), 2, border_radius=12)
            cor = UI_DESTAQUE
            indicador = "> "
        else:
            cor = UI_TEXTO
            indicador = "  "

        texto_opcao = fonte_opcao.render(indicador + opcao, True, cor)
        superficie.blit(texto_opcao,
                       (LARGURA_JANELA // 2 - texto_opcao.get_width() // 2,
                        y))

    # Rodapé
    fonte_rodape = pygame.font.Font(None, 24)
    texto_dica = fonte_rodape.render("SETAS: navegar   ENTER: selecionar   ESC: voltar ao menu", True, UI_TEXTO_SUAVE)
    superficie.blit(texto_dica,
                   (LARGURA_JANELA // 2 - texto_dica.get_width() // 2,
                    ALTURA_JANELA - 40))

def main():
    """Função principal do jogo"""
    jogo = Tetris()
    fonte = pygame.font.Font(None, 36)

    # Loop principal do jogo
    executando = True
    while executando:
        # Tratamento de eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False

            if evento.type == pygame.KEYDOWN:
                if jogo.estado_jogo == JOGO_ATIVO:
                    if evento.key == pygame.K_LEFT:
                        jogo.soft_drop_active = False
                        jogo.adicionar_input_buffer('ESQUERDA')
                    elif evento.key == pygame.K_RIGHT:
                        jogo.soft_drop_active = False
                        jogo.adicionar_input_buffer('DIREITA')
                    elif evento.key == pygame.K_DOWN:
                        jogo.soft_drop_active = True
                        # Movimento imediato para baixo quando a tecla é pressionada
                        jogo.adicionar_input_buffer('BAIXO')
                    elif evento.key == pygame.K_UP:
                        jogo.adicionar_input_buffer('CIMA')
                    elif evento.key == pygame.K_c:
                        jogo.adicionar_input_buffer('SEGURAR')
                    elif evento.key == pygame.K_SPACE:
                        # Queda rápida
                        while not jogo.verificar_colisao(posicao_adicional=[1, 0]):
                            jogo.posicao_peca[0] += 1
                        jogo.fixar_peca()
                    elif evento.key == pygame.K_p or evento.key == pygame.K_ESCAPE:
                        jogo.estado_jogo = JOGO_PAUSADO

                elif jogo.estado_jogo == JOGO_PAUSADO:
                    if evento.key == pygame.K_UP:
                        jogo.menu_pausa_selecionado = (jogo.menu_pausa_selecionado - 1) % len(jogo.opcoes_pausa)
                    elif evento.key == pygame.K_DOWN:
                        jogo.menu_pausa_selecionado = (jogo.menu_pausa_selecionado + 1) % len(jogo.opcoes_pausa)
                    elif evento.key == pygame.K_RETURN:
                        if jogo.opcoes_pausa[jogo.menu_pausa_selecionado] == "VOLTAR AO JOGO":
                            jogo.estado_jogo = JOGO_ATIVO
                        elif jogo.opcoes_pausa[jogo.menu_pausa_selecionado] == "REGRAS DO MODO":
                            jogo.explicacao_origem = JOGO_PAUSADO
                            jogo.estado_jogo = EXPLICACAO_MODO
                        elif jogo.opcoes_pausa[jogo.menu_pausa_selecionado] == "REINICIAR":
                            modo_atual = jogo.modo_jogo  # Salva o modo em andamento
                            jogo = Tetris()  # Reinicia o jogo
                            jogo.modo_jogo = modo_atual  # Restaura o modo anterior
                            jogo.modo_config = MODO_CONFIG[modo_atual]
                            jogo.velocidade_queda = jogo.modo_config["velocidade_inicial"]
                            jogo.linhas_objetivo = jogo.modo_config["linhas_objetivo"]
                            jogo.tempo_inicio = time.time() if modo_atual == "ULTRA" else None
                            jogo.jogo_vencido = False
                            jogo.estado_jogo = JOGO_ATIVO
                        elif jogo.opcoes_pausa[jogo.menu_pausa_selecionado] == "SAIR":
                            jogo.estado_jogo = MENU_PRINCIPAL
                    elif evento.key == pygame.K_ESCAPE:
                        jogo.estado_jogo = JOGO_ATIVO
                    elif evento.key == pygame.K_p:
                        jogo.estado_jogo = JOGO_ATIVO

                elif jogo.estado_jogo == MENU_PRINCIPAL:
                    if evento.key == pygame.K_UP:
                        jogo.menu_selecionado = (jogo.menu_selecionado - 1) % len(jogo.menu_opcoes)
                    elif evento.key == pygame.K_DOWN:
                        jogo.menu_selecionado = (jogo.menu_selecionado + 1) % len(jogo.menu_opcoes)
                    elif evento.key == pygame.K_RETURN:
                        if jogo.menu_opcoes[jogo.menu_selecionado] == "JOGAR":
                            jogo.estado_jogo = SELECIONAR_MODO
                            jogo.modo_jogo_selecionado = 0
                        elif jogo.menu_opcoes[jogo.menu_selecionado] == "INSTRUÇÕES":
                            jogo.estado_jogo = INSTRUCOES
                        elif jogo.menu_opcoes[jogo.menu_selecionado] == "RECORDES":
                            jogo.estado_jogo = RECORDES
                        elif jogo.menu_opcoes[jogo.menu_selecionado] == "CONQUISTAS":
                            jogo.estado_jogo = CONQUISTAS
                        elif jogo.menu_opcoes[jogo.menu_selecionado] == "OPÇÕES":
                            jogo.estado_jogo = OPCOES
                        elif jogo.menu_opcoes[jogo.menu_selecionado] == "SAIR":
                            executando = False
                    elif evento.key == pygame.K_ESCAPE:
                        executando = False  # ESC sai do jogo no menu principal

                elif jogo.estado_jogo == INSTRUCOES:
                    if evento.key == pygame.K_ESCAPE:
                        jogo.estado_jogo = MENU_PRINCIPAL

                elif jogo.estado_jogo == OPCOES:
                    if evento.key == pygame.K_ESCAPE:
                        jogo.estado_jogo = MENU_PRINCIPAL

                elif jogo.estado_jogo == RECORDES:
                    if evento.key == pygame.K_ESCAPE:
                        jogo.estado_jogo = MENU_PRINCIPAL
                    elif evento.key == pygame.K_r:
                        jogo.resetar_recordes()

                elif jogo.estado_jogo == CONQUISTAS:
                    if evento.key == pygame.K_ESCAPE:
                        jogo.estado_jogo = MENU_PRINCIPAL
                    elif evento.key == pygame.K_r:
                        jogo.resetar_conquistas()

                elif jogo.estado_jogo == SELECIONAR_MODO:
                    if evento.key == pygame.K_UP:
                        jogo.modo_jogo_selecionado = (jogo.modo_jogo_selecionado - 1) % len(jogo.modo_jogo_opcoes)
                    elif evento.key == pygame.K_DOWN:
                        jogo.modo_jogo_selecionado = (jogo.modo_jogo_selecionado + 1) % len(jogo.modo_jogo_opcoes)
                    elif evento.key == pygame.K_RETURN:
                        modo_nome = jogo.modo_jogo_opcoes[jogo.modo_jogo_selecionado]
                        jogo = Tetris()  # Reinicia completamente: limpa grade, peças, bag, pontuação, nível
                        jogo.modo_jogo = modo_nome
                        jogo.modo_config = MODO_CONFIG[modo_nome]
                        jogo.velocidade_queda = jogo.modo_config["velocidade_inicial"]
                        jogo.linhas_objetivo = jogo.modo_config["linhas_objetivo"]
                        jogo.tempo_inicio = None
                        jogo.jogo_vencido = False
                        jogo.estado_jogo = EXPLICACAO_MODO
                    elif evento.key == pygame.K_ESCAPE:
                        jogo.estado_jogo = MENU_PRINCIPAL

                elif jogo.estado_jogo == EXPLICACAO_MODO:
                    if evento.key == pygame.K_RETURN:
                        jogo.estado_jogo = JOGO_ATIVO
                        jogo.tempo_inicio = time.time()
                    elif evento.key == pygame.K_ESCAPE:
                        if jogo.explicacao_origem == JOGO_PAUSADO:
                            jogo.estado_jogo = JOGO_PAUSADO
                        else:
                            jogo.estado_jogo = SELECIONAR_MODO

            # Tratamento de soltura de teclas para soft drop
            if evento.type == pygame.KEYUP:
                if jogo.estado_jogo == JOGO_ATIVO:
                    if evento.key == pygame.K_DOWN:
                        jogo.soft_drop_active = False

                elif jogo.estado_jogo == JOGO_FIM:
                    if evento.key == pygame.K_UP:
                        jogo.menu_fim_jogo_selecionado = (jogo.menu_fim_jogo_selecionado - 1) % len(jogo.opcoes_fim_jogo)
                    elif evento.key == pygame.K_DOWN:
                        jogo.menu_fim_jogo_selecionado = (jogo.menu_fim_jogo_selecionado + 1) % len(jogo.opcoes_fim_jogo)
                    elif evento.key == pygame.K_RETURN:
                        if jogo.opcoes_fim_jogo[jogo.menu_fim_jogo_selecionado] == "JOGAR NOVAMENTE":
                            modo_atual = jogo.modo_jogo  # Salva o modo em andamento
                            jogo = Tetris()  # Reinicia o jogo
                            jogo.modo_jogo = modo_atual  # Restaura o modo anterior
                            jogo.modo_config = MODO_CONFIG[modo_atual]
                            jogo.velocidade_queda = jogo.modo_config["velocidade_inicial"]
                            jogo.linhas_objetivo = jogo.modo_config["linhas_objetivo"]
                            jogo.tempo_inicio = time.time() if modo_atual == "ULTRA" else None
                            jogo.jogo_vencido = False
                            jogo.estado_jogo = JOGO_ATIVO
                        elif jogo.opcoes_fim_jogo[jogo.menu_fim_jogo_selecionado] == "VOLTAR AO MENU":
                            jogo.estado_jogo = MENU_PRINCIPAL
                    elif evento.key == pygame.K_ESCAPE:
                        jogo.estado_jogo = MENU_PRINCIPAL  # Volta ao menu principal

        # Atualização do jogo
        if jogo.estado_jogo == JOGO_ATIVO:
            jogo.atualizar()

        # Renderização
        janela.fill(PRETO)

        # Desenha o jogo apenas quando está ativamente jogando
        if jogo.estado_jogo == JOGO_ATIVO:
            jogo.desenhar_grade(janela)
            jogo.desenhar_peca(janela)
            jogo.desenhar_interface(janela)
        # Sempre atualiza e desenha os sistemas de partículas (para efeitos nos menus)
        jogo.particulas_linhas.draw(janela)
        jogo.particulas_impacto.draw(janela)

        # Desenha telas especiais baseado no estado do jogo
        if jogo.estado_jogo == JOGO_PAUSADO:
            desenhar_tela_pausa(janela, jogo)
        elif jogo.estado_jogo == JOGO_FIM:
            desenhar_tela_fim_jogo(janela, jogo)
        elif jogo.estado_jogo == MENU_PRINCIPAL:
            jogo.desenhar_menu(janela)
        elif jogo.estado_jogo == INSTRUCOES:
            jogo.desenhar_instrucoes(janela)
        elif jogo.estado_jogo == OPCOES:
            jogo.desenhar_opcoes(janela)
        elif jogo.estado_jogo == RECORDES:
            jogo.desenhar_recorde(janela)
        elif jogo.estado_jogo == CONQUISTAS:
            jogo.desenhar_conquistas(janela)
        elif jogo.estado_jogo == SELECIONAR_MODO:
            jogo.desenhar_selecionar_modo(janela)
        elif jogo.estado_jogo == EXPLICACAO_MODO:
            jogo.desenhar_explicacao_modo(janela)

        # Alerta visual de conquista desbloqueada (overlay durante o jogo)
        if jogo.estado_jogo == JOGO_ATIVO and jogo.conquista_alerta_tempo > 0 and jogo.conquista_alerta_nome:
            fonte_alerta = pygame.font.Font(None, 48)
            texto_alerta = fonte_alerta.render(
                f"Conquista desbloqueada: {jogo.conquista_alerta_nome}", True, UI_SUCESSO)
            texto_contorno = fonte_alerta.render(
                f"Conquista desbloqueada: {jogo.conquista_alerta_nome}", True, PRETO)
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx != 0 or dy != 0:
                        janela.blit(texto_contorno,
                                   (LARGURA_JANELA // 2 - texto_alerta.get_width() // 2 + dx,
                                    ALTURA_JANELA // 3 - texto_alerta.get_height() // 2 + dy))
            janela.blit(texto_alerta,
                       (LARGURA_JANELA // 2 - texto_alerta.get_width() // 2,
                        ALTURA_JANELA // 3 - texto_alerta.get_height() // 2))

        pygame.display.flip()
        relogio.tick(60)  # Limita a 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
