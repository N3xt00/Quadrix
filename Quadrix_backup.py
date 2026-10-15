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
# - Quadriculado de fundo para melhor visualização

import pygame
import sys
import random
import time
import math


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


# Configuração da janela do jogo
janela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
pygame.display.set_caption('Tetris')
relogio = pygame.time.Clock()

# Estados do jogo
JOGO_ATIVO = 0
JOGO_PAUSADO = 1
JOGO_FIM = 2

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
        self.estado_jogo = JOGO_ATIVO
        self.tempo_queda_ultima = time.time()
        self.velocidade_queda = 0.5  # segundos por bloco (começa em 0.5s)
        # Sistemas de partículas para efeitos visuais
        self.particulas_linhas = ParticleSystem()  # Para linhas limpando
        self.particulas_impacto = ParticleSystem()  # Para peças fixando
        self.nova_peca()

    def nova_peca(self):
        """Gera uma nova peça aleatória"""
        if self.peca_atual is None:
            self.peca_atual = random.choice(list(TETROMINOS.keys()))
            self.peca_proxima = random.choice(list(TETROMINOS.keys()))
        else:
            self.peca_atual = self.peca_proxima
            self.peca_proxima = random.choice(list(TETROMINOS.keys()))

        self.rotacao_peca = 0
        # Posiciona a peça no topo central da grade
        forma = TETROMINOS[self.peca_atual][self.rotacao_peca]
        self.posicao_peca = [0, (LARGURA_GRADE - len(forma[0])) // 2]

        # Verifica se o jogo acabou (se a nova peça colide imediatamente)
        if self.verificar_colisao():
            self.estado_jogo = JOGO_FIM

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
            # Pontuação clássica do Tetris: 40 * nível para 1 linha, 100 * nível para 2 linhas, etc.
            pontuacao_linhas = [0, 40, 100, 300, 1200]
            self.pontuacao += pontuacao_linhas[len(linhas_para_remover)] * self.nivel

            # Aumenta o nível a cada 10 linhas
            self.nivel = min(10, (self.linhas_limpas // 10) + 1)
            # Aumenta a velocidade conforme o nível aumenta (mínimo 0.05s)
            self.velocidade_queda = max(0.05, 0.5 - (self.nivel - 1) * 0.05)

    def mover_peca(self, dx, dy):
        """Tenta mover a peça na direção especificada"""
        if not self.verificar_colisao(posicao_adicional=[0, dx]):
            self.posicao_peca[1] += dx
            return True
        return False

    def rotacionar_peca(self):
        """Tenta rotacionar a peça"""
        if not self.verificar_colisao(rotacao_adicional=1):
            self.rotacao_peca = (self.rotacao_peca + 1) % len(TETROMINOS[self.peca_atual])
            return True
        return False

    def atualizar(self):
        """Atualiza o estado do jogo (queda automática da peça e animações)"""
        if self.estado_jogo != JOGO_ATIVO:
            return

        tempo_atual = time.time()

        # Atualiza sistemas de partículas
        self.particulas_linhas.update()
        self.particulas_impacto.update()

        # Queda automática da peça
        if tempo_atual - self.tempo_queda_ultima > self.velocidade_queda:
            if not self.verificar_colisao(posicao_adicional=[1, 0]):
                self.posicao_peca[0] += 1
            else:
                self.fixar_peca()
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

    def desenhar_interface(self, superficie):
        """Desenha a interface do jogo com painel de informações estilizado"""
        # Painel de informações com fundo
        painel_largura = 200
        painel_altura = 180
        pygame.draw.rect(superficie, CINZA_ESCURO,
                        (10, 10, painel_largura, painel_altura))
        pygame.draw.rect(superficie, CINZA_CLARO,
                        (10, 10, painel_largura, painel_altura), 2)

        fonte_titulo = pygame.font.Font(None, 28)
        fonte_valor = pygame.font.Font(None, 36)
        fonte_pequena = pygame.font.Font(None, 24)

        # Título
        texto_titulo = fonte_titulo.render('TETRIS', True, AMARELO)
        superficie.blit(texto_titulo, (20, 20))

        # Pontuação com ícone
        texto_pontuacao_label = fonte_pequena.render('PONTUAÇÃO', True, BRANCO)
        superficie.blit(texto_pontuacao_label, (20, 50))
        texto_pontuacao_valor = fonte_valor.render(f'{self.pontuacao:>6}', True, AMARELO)
        superficie.blit(texto_pontuacao_valor, (20, 75))

        # Nível com ícone
        texto_nivel_label = fonte_pequena.render('NÍVEL', True, BRANCO)
        superficie.blit(texto_nivel_label, (20, 110))
        texto_nivel_valor = fonte_valor.render(f'{self.nivel:>2}', True, VERDE)
        superficie.blit(texto_nivel_valor, (20, 135))

        # Linhas com ícone
        texto_linhas_label = fonte_pequena.render('LINHAS', True, BRANCO)
        superficie.blit(texto_linhas_label, (20, 170))
        texto_linhas_valor = fonte_valor.render(f'{self.linhas_limpas:>3}', True, CIANO)
        superficie.blit(texto_linhas_valor, (20, 195))

        # Próxima peça com quadro estilizado
        texto_proxima_label = fonte_titulo.render('PRÓXIMA', True, BRANCO)
        superficie.blit(texto_proxima_label, (LARGURA_JANELA - 150, 20))

        # Quadro para a próxima peça com borda dupla
        quadro_largura = 120
        quadro_altura = 120
        quadro_x = LARGURA_JANELA - 150
        quadro_y = 50
        pygame.draw.rect(superficie, CINZA_ESCURO,
                        (quadro_x - 2, quadro_y - 2, quadro_largura + 4, quadro_altura + 4))
        pygame.draw.rect(superficie, CINZA_CLARO,
                        (quadro_x, quadro_y, quadro_largura, quadro_altura))
        pygame.draw.rect(superficie, PRETO,
                        (quadro_x, quadro_y, quadro_largura, quadro_altura), 2)

        # Desenha a próxima peça centralizada no quadro
        forma_proxima = TETROMINOS[self.peca_proxima][0]
        largura_preview = len(forma_proxima[0]) * TAMANHO_BLOCO
        altura_preview = len(forma_proxima) * TAMANHO_BLOCO
        inicio_x = quadro_x + (quadro_largura - largura_preview) // 2
        inicio_y = quadro_y + (quadro_altura - altura_preview) // 2

        self.desenhar_peca(superficie, self.peca_proxima, [0, 0], 0,
                          inicio_x - MARGEM_X, inicio_y - MARGEM_Y)

def desenhar_tela_pausa(superficie):
    """Desenha a tela de pausa com efeito de escurecimento e texto estilizado"""
    # Overlay escurecido
    superficie_overlay = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
    superficie_overlay.fill((0, 0, 0, 180))  # Preto semi-transparente
    superficie.blit(superficie_overlay, (0, 0))

    # Título "PAUSADO" com efeito de brilho
    fonte_grande = pygame.font.Font(None, 96)
    texto_pausa = fonte_grande.render('PAUSADO', True, AMARELO)
    # Efeito de contorno para melhor legibilidade
    texto_contorno = fonte_grande.render('PAUSADO', True, PRETO)
    for dx in [-2, 0, 2]:
        for dy in [-2, 0, 2]:
            if dx != 0 or dy != 0:
                superficie.blit(texto_contorno,
                               (LARGURA_JANELA // 2 - texto_pausa.get_width() // 2 + dx,
                                ALTURA_JANELA // 2 - texto_pausa.get_height() // 2 - 40 + dy))
    superficie.blit(texto_pausa,
                   (LARGURA_JANELA // 2 - texto_pausa.get_width() // 2,
                    ALTURA_JANELA // 2 - texto_pausa.get_height() // 2 - 40))

    # Instruções
    fonte_media = pygame.font.Font(None, 36)
    texto_instrucoes = fonte_media.render('Pressione P para continuar ou R para reiniciar', True, BRANCO)
    superficie.blit(texto_instrucoes,
                   (LARGURA_JANELA // 2 - texto_instrucoes.get_width() // 2,
                    ALTURA_JANELA // 2 + 20))

    # Dica adicional
    fonte_pequena = pygame.font.Font(None, 24)
    texto_dica = fonte_pequena.render('Dica: Use as setas para mover e cima para girar', True, CINZA_CLARO)
    superficie.blit(texto_dica,
                   (LARGURA_JANELA // 2 - texto_dica.get_width() // 2,
                    ALTURA_JANELA // 2 + 70))

def desenhar_tela_fim_jogo(superficie, pontuacao):
    """Desenha a tela de fim de jogo com efeito de escurecimento e texto estilizado"""
    # Overlay escurecido
    superficie_overlay = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
    superficie_overlay.fill((0, 0, 0, 200))  # Preto semi-transparente
    superficie.blit(superficie_overlay, (0, 0))

    # Título "FIM DE JOGO" com efeito de pulsar leve
    fonte_grande = pygame.font.Font(None, 96)
    texto_fim = fonte_grande.render('FIM DE JOGO', True, VERMELHO)
    # Efeito de contorno para melhor legibilidade
    texto_contorno = fonte_grande.render('FIM DE JOGO', True, PRETO)
    for dx in [-3, 0, 3]:
        for dy in [-3, 0, 3]:
            if dx != 0 or dy != 0:
                superficie.blit(texto_contorno,
                               (LARGURA_JANELA // 2 - texto_fim.get_width() // 2 + dx,
                                ALTURA_JANELA // 2 - texto_fim.get_height() // 2 - 60 + dy))
    superficie.blit(texto_fim,
                   (LARGURA_JANELA // 2 - texto_fim.get_width() // 2,
                    ALTURA_JANELA // 2 - texto_fim.get_height() // 2 - 60))

    # Pontuação final
    fonte_media = pygame.font.Font(None, 48)
    texto_pontuacao_label = fonte_media.render('PONTUAÇÃO FINAL', True, BRANCO)
    superficie.blit(texto_pontuacao_label,
                   (LARGURA_JANELA // 2 - texto_pontuacao_label.get_width() // 2,
                    ALTURA_JANELA // 2 - 20))
    texto_pontuacao_valor = fonte_media.render(f'{pontuacao:>8}', True, AMARELO)
    superficie.blit(texto_pontuacao_valor,
                   (LARGURA_JANELA // 2 - texto_pontuacao_valor.get_width() // 2,
                    ALTURA_JANELA // 2 + 20))

    # Estatísticas adicionais
    fonte_pequena = pygame.font.Font(None, 28)
    texto_nivel = fonte_pequena.render(f'Nível atingido: {min(10, (pontuacao // 1000) + 1)}', True, VERDE)
    superficie.blit(texto_nivel,
                   (LARGURA_JANELA // 2 - texto_nivel.get_width() // 2,
                    ALTURA_JANELA // 2 + 70))

    # Instruções
    fonte_instrucoes = pygame.font.Font(None, 36)
    texto_reiniciar = fonte_instrucoes.render('Pressione R para reiniciar ou Q para sair', True, BRANCO)
    superficie.blit(texto_reiniciar,
                   (LARGURA_JANELA // 2 - texto_reiniciar.get_width() // 2,
                    ALTURA_JANELA // 2 + 130))

    # Dica de jogo
    fonte_dica = pygame.font.Font(None, 24)
    texto_dica = fonte_dica.render('Dica: Limpe múltiplas linhas de uma vez para mais pontos!', True, CINZA_CLARO)
    superficie.blit(texto_dica,
                   (LARGURA_JANELA // 2 - texto_dica.get_width() // 2,
                    ALTURA_JANELA // 2 + 170))

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
                        jogo.mover_peca(-1, 0)
                    elif evento.key == pygame.K_RIGHT:
                        jogo.mover_peca(1, 0)
                    elif evento.key == pygame.K_DOWN:
                        jogo.mover_peca(0, 1)  # Movimento suave para baixo
                    elif evento.key == pygame.K_UP:
                        jogo.rotacionar_peca()
                    elif evento.key == pygame.K_SPACE:
                        # Queda rápida
                        while not jogo.verificar_colisao(posicao_adicional=[1, 0]):
                            jogo.posicao_peca[0] += 1
                        jogo.fixar_peca()
                    elif evento.key == pygame.K_p:
                        jogo.estado_jogo = JOGO_PAUSADO

                elif jogo.estado_jogo == JOGO_PAUSADO:
                    if evento.key == pygame.K_p:
                        jogo.estado_jogo = JOGO_ATIVO
                    elif evento.key == pygame.K_r:
                        jogo = Tetris()  # Reinicia o jogo

                elif jogo.estado_jogo == JOGO_FIM:
                    if evento.key == pygame.K_r:
                        jogo = Tetris()  # Reinicia o jogo
                    elif evento.key == pygame.K_q:
                        executando = False

        # Atualização do jogo
        if jogo.estado_jogo == JOGO_ATIVO:
            jogo.atualizar()

        # Renderização
        janela.fill(PRETO)

        # Desenha o jogo
        jogo.desenhar_grade(janela)
        jogo.desenhar_peca(janela)
        jogo.desenhar_interface(janela)

        # Desenha telas especiais
        if jogo.estado_jogo == JOGO_PAUSADO:
            desenhar_tela_pausa(janela)
        elif jogo.estado_jogo == JOGO_FIM:
            desenhar_tela_fim_jogo(janela, jogo.pontuacao)

        pygame.display.flip()
        relogio.tick(60)  # Limita a 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()