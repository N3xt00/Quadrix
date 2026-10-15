"""Ponto de entrada e loop principal do Quadrix.

Coordena o objeto :class:`Tetris` (estado e regras do jogo) com a
renderização (:mod:`quadrix.renderer`) e a persistência
(:mod:`quadrix.save`). Mantém o comportamento idêntico ao arquivo
monolítico original, apenas com as responsabilidades separadas em
módulos focados.
"""

import math
import random
import sys
import time

import pygame

from .config import (
    LARGURA_JANELA,
    ALTURA_JANELA,
    MARGEM_X,
    MARGEM_Y,
    TAMANHO_BLOCO,
    LARGURA_GRADE,
    ALTURA_GRADE,
    PRETO,
    BRANCO,
    CINZA,
    CINZA_CLARO,
    CINZA_ESCURO,
    UI_DESTAQUE,
    UI_SUCESSO,
    CORES_TETROMINOS,
    MODO_CONFIG,
    ICON_PATH,
)
from .particles import ParticleSystem
from .states import (
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
from .tetrominoes import TETROMINOS, WALL_KICKS
from .renderer import (
    desenhar_menu,
    desenhar_instrucoes,
    desenhar_opcoes,
    desenhar_recorde,
    desenhar_conquistas,
    desenhar_selecionar_modo,
    desenhar_explicacao_modo,
    desenhar_grade,
    desenhar_peca,
    desenhar_interface,
    desenhar_tela_pausa,
    desenhar_tela_fim_jogo,
)
from .save import salvar_progresso, carregar_progresso


class Tetris:
    """Objeto central do jogo: concentra o estado e as regras."""

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
        self.particulas_linhas = None  # tipo: ParticleSystem
        self.particulas_impacto = None  # tipo: ParticleSystem
        # Sistema de holding (peça para segurar)
        self.hold_peca = None  # Peça atualmente segurada
        self.hold_usado = False  # Se o holding já foi usado nesta troca
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
        self.modo_config = dict(MODO_CONFIG[self.modo_jogo])
        self.tempo_inicio = None  # Para modos com tempo (ULTRA)
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
        self.particulas_linhas = ParticleSystem()  # Para linhas limpando
        self.particulas_impacto = ParticleSystem()  # Para peças fixando

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
        """Define todas as conquistas disponíveis no jogo."""
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
        carregar_progresso(self)

    def verificar_conquista(self, conquista_id):
        """Marca uma conquista como desbloqueada e salva o progresso."""
        if conquista_id in self.conquistas and not self.conquistas[conquista_id]["desbloqueada"]:
            self.conquistas[conquista_id]["desbloqueada"] = True
            self.conquista_alerta_nome = self.conquistas[conquista_id]["nome"]
            self.conquista_alerta_tempo = 4.0  # Alerta visível por 4 segundos
            salvar_progresso(self)

    def checar_conquistas(self):
        """Verifica todas as conquistas com base no estado atual do jogo."""
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
        """Reseta todas as conquistas para desbloqueada=False."""
        for conquista in self.conquistas.values():
            conquista["desbloqueada"] = False
        salvar_progresso(self)

    def resetar_recordes(self):
        """Reseta todos os recordes para 0."""
        for modo in self.recordes:
            self.recordes[modo] = 0
        salvar_progresso(self)

    def verificar_recorde(self):
        """Atualiza o recorde do modo atual se a pontuação atual for maior."""
        modo = self.modo_jogo
        if modo not in self.recordes:
            self.recordes[modo] = 0
        if self.pontuacao > self.recordes[modo]:
            self.recordes[modo] = self.pontuacao
            salvar_progresso(self)

    def refill_bag(self):
        """Reabastece e embaralha a bag com as 7 peças do Tetris."""
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
        """Obtém uma peça da bag, reabastecendo se necessário."""
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
        """Guarda a peça atual para uso futuro ou troca com a peça segurada."""
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
        """Adiciona um comando ao buffer de entrada para processamento posterior."""
        if len(self.input_buffer) < self.input_buffer_max_size:
            self.input_buffer.append(comando)
        # Se o buffer estiver cheio, ignora o comando mais antigo (FIFO)
        elif len(self.input_buffer) >= self.input_buffer_max_size:
            # Remove o comando mais antigo e adiciona o novo
            self.input_buffer.pop(0)
            self.input_buffer.append(comando)

    def _processar_input_buffer(self, comando):
        """Processa um comando do buffer de entrada."""
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
        """Calcula a posição onde a peça atual irá cair se solta imediatamente."""
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
        """Verifica se há colisão com as paredes ou outras peças."""
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
        """Fixa a peça atual na grade e gera uma nova."""
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
        """Remove linhas completas e gera efeitos de partículas."""
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
        """Tenta mover a peça na direção especificada."""
        if not self.verificar_colisao(posicao_adicional=[0, dx]):
            self.posicao_peca[1] += dx
            self.calcular_posicao_fantasma()
            # Reseta o lock delay quando a peça é movida horizontalmente durante o delay
            if self.is_lock_delay_active:
                self.lock_delay_timer = time.time()
            return True
        return False

    def rotacionar_peca(self):
        """Tenta rotacionar a peça com wall kicks."""
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
        """Atualiza o estado do jogo (queda automática da peça e animações)."""
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


def main():
    """Função principal do jogo."""
    pygame.init()

    janela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    pygame.display.set_caption('Quadrix')

    # Ícone da janela (caminho relativo ao pacote; nunca falha o jogo se faltar)
    try:
        icone = pygame.image.load(str(ICON_PATH))
        pygame.display.set_icon(icone)
    except (pygame.error, FileNotFoundError, OSError):
        pass  # Ícone opcional: não impede o jogo de rodar

    relogio = pygame.time.Clock()
    fonte = pygame.font.Font(None, 36)

    jogo = Tetris()

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
                            jogo.modo_config = dict(MODO_CONFIG[modo_atual])
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
                        jogo.modo_config = dict(MODO_CONFIG[modo_nome])
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
                            jogo.modo_config = dict(MODO_CONFIG[modo_atual])
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
            desenhar_grade(janela, jogo)
            desenhar_peca(janela, jogo)
            desenhar_interface(janela, jogo)
        # Sempre atualiza e desenha os sistemas de partículas (para efeitos nos menus)
        jogo.particulas_linhas.draw(janela)
        jogo.particulas_impacto.draw(janela)

        # Desenha telas especiais baseado no estado do jogo
        if jogo.estado_jogo == JOGO_PAUSADO:
            desenhar_tela_pausa(janela, jogo)
        elif jogo.estado_jogo == JOGO_FIM:
            desenhar_tela_fim_jogo(janela, jogo)
        elif jogo.estado_jogo == MENU_PRINCIPAL:
            desenhar_menu(janela, jogo)
        elif jogo.estado_jogo == INSTRUCOES:
            desenhar_instrucoes(janela, jogo)
        elif jogo.estado_jogo == OPCOES:
            desenhar_opcoes(janela, jogo)
        elif jogo.estado_jogo == RECORDES:
            desenhar_recorde(janela, jogo)
        elif jogo.estado_jogo == CONQUISTAS:
            desenhar_conquistas(janela, jogo)
        elif jogo.estado_jogo == SELECIONAR_MODO:
            desenhar_selecionar_modo(janela, jogo)
        elif jogo.estado_jogo == EXPLICACAO_MODO:
            desenhar_explicacao_modo(janela, jogo)

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
