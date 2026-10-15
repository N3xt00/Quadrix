"""Renderização e desenho da interface do Quadrix.

Todas as funções recebem a superficie do pygame e o objeto do jogo
(quando necessário), centralizando a lógica visual e removendo a
duplicação de padrões de UI: título com contorno, painel de fundo,
bordas decorativas, pastilha de seleção e blocos com efeito 3D.
"""

import pygame
import time

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
    CORES_TETROMINOS,
    UI_FUNDO,
    UI_PAINEL,
    UI_BORDA,
    UI_TEXTO,
    UI_TEXTO_SUAVE,
    UI_DESTAQUE,
    UI_ACAO,
    UI_SUCESSO,
    UI_AVISO,
)
from .tetrominoes import TETROMINOS
from .states import JOGO_ATIVO


def texto_centralizado(superficie, texto, fonte, cor, cx, cy):
    """Renderiza texto centralizado em (cx, cy) e devolve a superficie."""
    render = fonte.render(texto, True, cor)
    superficie.blit(render, (cx - render.get_width() // 2, cy - render.get_height() // 2))
    return render


def desenhar_painel(superficie, alpha=210):
    """Painel de fundo escuro e semitransparente que cobre a janela inteira."""
    painel = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
    painel.fill((0, 0, 0, alpha))
    superficie.blit(painel, (0, 0))


def desenhar_bordas(superficie, espessura=6):
    """Bordas decorativas superior e inferior da janela."""
    pygame.draw.rect(superficie, UI_BORDA, (0, 0, LARGURA_JANELA, espessura))
    pygame.draw.rect(superficie, UI_BORDA, (0, ALTURA_JANELA - espessura, LARGURA_JANELA, espessura))


def desenhar_titulo_contorno(superficie, texto, fonte, cx, cy, cor=UI_DESTAQUE,
                             contorno_cor=PRETO, offset=3):
    """Título com contorno preto desenhado em torno do texto principal."""
    texto_surf = fonte.render(texto, True, cor)
    contorno_surf = fonte.render(texto, True, contorno_cor)
    x_base = cx - texto_surf.get_width() // 2
    y_base = cy - texto_surf.get_height() // 2
    for dx in [-offset, 0, offset]:
        for dy in [-offset, 0, offset]:
            if dx != 0 or dy != 0:
                superficie.blit(contorno_surf, (x_base + dx, y_base + dy))
    superficie.blit(texto_surf, (x_base, y_base))
    return texto_surf


def desenhar_pastilha_selecao(superficie, x, y, largura, altura):
    """Pastilha (pill) que destaca a opção atualmente selecionada."""
    pygame.draw.rect(superficie, UI_PAINEL, (x - 4, y - 14, largura + 8, altura + 8), border_radius=12)
    pygame.draw.rect(superficie, UI_BORDA, (x - 4, y - 14, largura + 8, altura + 8), 2, border_radius=12)


def desenhar_bloco(superficie, x, y, tamanho, cor):
    """Bloco com efeito 3D: brilho no topo/esquerda, sombra na base/direita."""
    pygame.draw.rect(superficie, cor, (x, y, tamanho, tamanho))
    claro = tuple(min(255, c + 30) for c in cor)
    escuro = tuple(max(0, c - 30) for c in cor)
    fim = tamanho - 1
    pygame.draw.line(superficie, claro, (x, y), (x + fim, y), 2)
    pygame.draw.line(superficie, claro, (x, y), (x, y + fim), 2)
    pygame.draw.line(superficie, escuro, (x, y + fim), (x + fim, y + fim), 2)
    pygame.draw.line(superficie, escuro, (x + fim, y), (x + fim, y + fim), 2)
    pygame.draw.rect(superficie, BRANCO, (x, y, tamanho, tamanho), 1)


def desenhar_menu(superficie, jogo):
    """Desenha o menu principal com visual moderno."""
    desenhar_painel(superficie)
    desenhar_bordas(superficie)

    fonte_titulo = pygame.font.Font(None, 110)
    desenhar_titulo_contorno(
        superficie, 'QUADRIX', fonte_titulo,
        LARGURA_JANELA // 2, ALTURA_JANELA // 4,
    )

    fonte_sub = pygame.font.Font(None, 30)
    texto_centralizado(
        superficie, 'O clássico dos blocos, com visual renovado',
        fonte_sub, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA // 4 + 80,
    )

    fonte_opcao = pygame.font.Font(None, 44)
    espacamento = 50
    y_inicial = ALTURA_JANELA // 4 + 155
    largura_pastilha = 340
    altura_pastilha = 48

    for i, opcao in enumerate(jogo.menu_opcoes):
        y = y_inicial + i * espacamento
        x_pastilha = LARGURA_JANELA // 2 - largura_pastilha // 2
        if i == jogo.menu_selecionado:
            desenhar_pastilha_selecao(superficie, x_pastilha, y, largura_pastilha, altura_pastilha)
            cor = UI_DESTAQUE
            indicador = "> "
        else:
            cor = UI_TEXTO
            indicador = "  "
        texto_opcao = fonte_opcao.render(indicador + opcao, True, cor)
        superficie.blit(texto_opcao,
                        (LARGURA_JANELA // 2 - texto_opcao.get_width() // 2, y))

    fonte_instrucoes = pygame.font.Font(None, 24)
    texto_centralizado(
        superficie, "SETAS: navegar   ENTER: selecionar   ESC: sair",
        fonte_instrucoes, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA - 40,
    )


def desenhar_instrucoes(superficie, jogo):
    """Desenha a tela de instruções sem sobreposição de textos."""
    desenhar_painel(superficie)
    desenhar_bordas(superficie)

    fonte_titulo = pygame.font.Font(None, 72)
    texto_centralizado(
        superficie, 'COMO JOGAR', fonte_titulo, UI_DESTAQUE,
        LARGURA_JANELA // 2, 30,
    )

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
                            (LARGURA_JANELA // 2 - largura // 2, y))
            y += 32
        else:
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
                                        (LARGURA_JANELA // 2 - largura // 2, y))
                        y += 24
                    parte = palavra
            if parte:
                ts = fonte.render(parte, True, cor)
                largura = ts.get_width()
                superficie.blit(ts,
                                (LARGURA_JANELA // 2 - largura // 2, y))
                y += 24

    fonte_rodape = pygame.font.Font(None, 24)
    texto_centralizado(
        superficie, "Pressione ESC para voltar ao menu",
        fonte_rodape, UI_SUCESSO, LARGURA_JANELA // 2, ALTURA_JANELA - 35,
    )


def desenhar_opcoes(superficie, jogo):
    """Desenha a tela de opções com estilo do menu principal."""
    desenhar_painel(superficie)
    desenhar_bordas(superficie)

    fonte_titulo = pygame.font.Font(None, 64)
    desenhar_titulo_contorno(
        superficie, 'OPÇÕES', fonte_titulo,
        LARGURA_JANELA // 2, ALTURA_JANELA // 4,
    )

    fonte_sub = pygame.font.Font(None, 30)
    texto_centralizado(
        superficie, 'Configurações em desenvolvimento',
        fonte_sub, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA // 4 + 80,
    )

    fonte_opcao = pygame.font.Font(None, 32)
    opcoes = [
        "VOLUME DE SOM: [ TODO: Implementar slider ]",
        "VOLUME DE MÚSICA: [ TODO: Implementar slider ]",
        "CONTROLES: [ TODO: Implementar remapeamento ]",
        "TEMA VISUAL: [ TODO: Implementar seleção de tema ]",
        "DIFICULDADE: [ TODO: Implementar seleção de dificuldade ]",
        "",
        "ESTAS OPÇÕES ESTÃO EM DESENVOLVIMENTO",
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
                        (LARGURA_JANELA // 2 - texto_linha.get_width() // 2, y))

    fonte_rodape = pygame.font.Font(None, 24)
    texto_centralizado(
        superficie, "Pressione ESC para voltar ao menu",
        fonte_rodape, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA - 40,
    )


def desenhar_recorde(superficie, jogo):
    """Desenha a tela de recordes com estilo do menu principal."""
    desenhar_painel(superficie)
    desenhar_bordas(superficie)

    fonte_titulo = pygame.font.Font(None, 64)
    desenhar_titulo_contorno(
        superficie, 'RECORDES', fonte_titulo,
        LARGURA_JANELA // 2, ALTURA_JANELA // 4,
    )

    fonte_sub = pygame.font.Font(None, 30)
    texto_centralizado(
        superficie, 'Maior pontuação por modo',
        fonte_sub, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA // 4 + 80,
    )

    fonte_recorde = pygame.font.Font(None, 28)
    y_inicial = ALTURA_JANELA // 4 + 130
    espacamento = 40

    for i, modo in enumerate(jogo.modo_jogo_opcoes):
        recorde = jogo.recordes.get(modo, 0)
        texto_linha = fonte_recorde.render(f'{modo}: {recorde:>6}', True, UI_TEXTO)
        superficie.blit(texto_linha,
                        (LARGURA_JANELA // 2 - texto_linha.get_width() // 2,
                         y_inicial + i * espacamento))

    # Botão de resetar recordes
    largura_botao = 320
    altura_botao = 40
    x_botao = LARGURA_JANELA // 2 - largura_botao // 2
    y_botao = ALTURA_JANELA - 90
    jogo.rect_botao_reset_recordes = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
    pygame.draw.rect(superficie, UI_ACAO, jogo.rect_botao_reset_recordes, border_radius=8)
    pygame.draw.rect(superficie, UI_BORDA, jogo.rect_botao_reset_recordes, 2, border_radius=8)
    fonte_botao = pygame.font.Font(None, 28)
    texto_botao = fonte_botao.render("RESETAR RECORDES", True, BRANCO)
    superficie.blit(texto_botao,
                    (jogo.rect_botao_reset_recordes.centerx - texto_botao.get_width() // 2,
                     jogo.rect_botao_reset_recordes.centery - texto_botao.get_height() // 2))

    fonte_rodape = pygame.font.Font(None, 24)
    texto_centralizado(
        superficie, "ESC: Voltar   R: Resetar recordes",
        fonte_rodape, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA - 40,
    )


def desenhar_conquistas(superficie, jogo):
    """Desenha a tela de conquistas com estilo do menu principal."""
    desenhar_painel(superficie)
    desenhar_bordas(superficie)

    fonte_titulo = pygame.font.Font(None, 64)
    desenhar_titulo_contorno(
        superficie, 'CONQUISTAS', fonte_titulo,
        LARGURA_JANELA // 2, ALTURA_JANELA // 4,
    )

    fonte_sub = pygame.font.Font(None, 30)
    total = len(jogo.conquistas)
    desbloqueadas = sum(1 for c in jogo.conquistas.values() if c["desbloqueada"])
    texto_centralizado(
        superficie, f'Conquistas: {desbloqueadas}/{total}',
        fonte_sub, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA // 4 + 80,
    )

    fonte_conquista = pygame.font.Font(None, 24)
    y_inicial = ALTURA_JANELA // 4 + 120
    espacamento = 30

    for i, (_, conquista) in enumerate(jogo.conquistas.items()):
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
    jogo.rect_botao_reset_conquistas = pygame.Rect(x_botao, y_botao, largura_botao, altura_botao)
    pygame.draw.rect(superficie, UI_ACAO, jogo.rect_botao_reset_conquistas, border_radius=8)
    pygame.draw.rect(superficie, UI_BORDA, jogo.rect_botao_reset_conquistas, 2, border_radius=8)
    fonte_botao = pygame.font.Font(None, 28)
    texto_botao = fonte_botao.render("RESETAR CONQUISTAS", True, BRANCO)
    superficie.blit(texto_botao,
                    (jogo.rect_botao_reset_conquistas.centerx - texto_botao.get_width() // 2,
                     jogo.rect_botao_reset_conquistas.centery - texto_botao.get_height() // 2))

    fonte_rodape = pygame.font.Font(None, 24)
    texto_centralizado(
        superficie, "ESC: Voltar   R: Resetar conquistas",
        fonte_rodape, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA - 40,
    )


def desenhar_selecionar_modo(superficie, jogo):
    """Desenha a tela de seleção de modo de jogo."""
    desenhar_painel(superficie)
    desenhar_bordas(superficie)

    fonte_titulo = pygame.font.Font(None, 64)
    desenhar_titulo_contorno(
        superficie, 'SELECIONAR MODO', fonte_titulo,
        LARGURA_JANELA // 2, ALTURA_JANELA // 4,
    )

    fonte_sub = pygame.font.Font(None, 30)
    texto_centralizado(
        superficie, 'Escolha o modo de jogo',
        fonte_sub, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA // 4 + 80,
    )

    fonte_opcao = pygame.font.Font(None, 44)
    y_inicial = ALTURA_JANELA // 4 + 155
    espacamento = 40
    largura_pastilha = 300
    altura_pastilha = 48

    for i, modo in enumerate(jogo.modo_jogo_opcoes):
        y = y_inicial + i * espacamento
        x_pastilha = LARGURA_JANELA // 2 - largura_pastilha // 2
        if i == jogo.modo_jogo_selecionado:
            desenhar_pastilha_selecao(superficie, x_pastilha, y, largura_pastilha, altura_pastilha)
            cor = UI_DESTAQUE
            indicador = "> "
        else:
            cor = UI_TEXTO
            indicador = "  "
        texto_modo = fonte_opcao.render(f"{indicador}{modo}", True, cor)
        superficie.blit(texto_modo,
                        (LARGURA_JANELA // 2 - texto_modo.get_width() // 2, y))

    fonte_rodape = pygame.font.Font(None, 24)
    texto_centralizado(
        superficie, "ESC: Voltar ao menu   ENTER: Confirmar",
        fonte_rodape, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA - 40,
    )


def desenhar_explicacao_modo(superficie, jogo):
    """Desenha a tela de explicação do modo de jogo selecionado."""
    desenhar_painel(superficie)
    desenhar_bordas(superficie)

    fonte_titulo = pygame.font.Font(None, 64)
    modo_nome = jogo.modo_jogo
    desenhar_titulo_contorno(
        superficie, f'MODO: {modo_nome}', fonte_titulo,
        LARGURA_JANELA // 2, ALTURA_JANELA // 4,
    )

    fonte_desc = pygame.font.Font(None, 32)
    descricao = jogo.modo_config["descricao"]
    texto_centralizado(
        superficie, descricao, fonte_desc, UI_TEXTO,
        LARGURA_JANELA // 2, ALTURA_JANELA // 4 + 100,
    )

    fonte_detalhe = pygame.font.Font(None, 24)
    detalhes = []
    if jogo.modo_config["tempo_limite"]:
        detalhes.append(f"Tempo limite: {jogo.modo_config['tempo_limite']} segundos")
    if jogo.modo_config["linhas_objetivo"]:
        detalhes.append(f"Objetivo: limpar {jogo.modo_config['linhas_objetivo']} linhas")
    if jogo.modo_config["caos"]:
        detalhes.append("Modo CAOS: peças aparecem de forma imprevisível!")

    y_detalhe = ALTURA_JANELA // 4 + 150
    for detalhe in detalhes:
        texto_detalhe = fonte_detalhe.render(detalhe, True, UI_TEXTO_SUAVE)
        superficie.blit(texto_detalhe,
                        (LARGURA_JANELA // 2 - texto_detalhe.get_width() // 2, y_detalhe))
        y_detalhe += 30

    fonte_rodape = pygame.font.Font(None, 24)
    texto_centralizado(
        superficie, "ESC: Voltar   ENTER: Iniciar jogo",
        fonte_rodape, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA - 40,
    )


def desenhar_grade(superficie, jogo):
    """Desenha a grade do jogo com bordas, quadriculado e blocos fixos."""
    # Fundo da grade com borda dupla
    pygame.draw.rect(superficie, CINZA_ESCURO,
                     (MARGEM_X - 4, MARGEM_Y - 4,
                      LARGURA_GRADE * TAMANHO_BLOCO + 8,
                      ALTURA_GRADE * TAMANHO_BLOCO + 8))
    pygame.draw.rect(superficie, CINZA_CLARO,
                     (MARGEM_X - 2, MARGEM_Y - 2,
                      LARGURA_GRADE * TAMANHO_BLOCO + 4,
                      ALTURA_GRADE * TAMANHO_BLOCO + 4))

    # Quadriculado
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

    # Blocos fixos na grade
    for linha in range(ALTURA_GRADE):
        for coluna in range(LARGURA_GRADE):
            if jogo.grade[linha][coluna]:
                cor = CORES_TETROMINOS[jogo.grade[linha][coluna]]
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

    # Peça fantasma
    if (jogo.posicao_fantasma is not None and jogo.estado_jogo == JOGO_ATIVO):
        forma_fantasma = TETROMINOS[jogo.peca_atual][jogo.rotacao_peca]
        cor_fantasma = CORES_TETROMINOS[jogo.peca_atual]
        cor_fantasma_transparente = (*cor_fantasma, 90)

        superficie_fantasma = pygame.Surface(
            (LARGURA_GRADE * TAMANHO_BLOCO, ALTURA_GRADE * TAMANHO_BLOCO), pygame.SRCALPHA)

        for linha_peca, linha in enumerate(forma_fantasma):
            for coluna_peca, celula in enumerate(linha):
                if celula:
                    x = (jogo.posicao_fantasma[1] + coluna_peca) * TAMANHO_BLOCO
                    y = (jogo.posicao_fantasma[0] + linha_peca) * TAMANHO_BLOCO
                    pygame.draw.rect(superficie_fantasma, cor_fantasma_transparente,
                                     (x, y, TAMANHO_BLOCO, TAMANHO_BLOCO))
                    pygame.draw.rect(superficie_fantasma, BRANCO,
                                     (x, y, TAMANHO_BLOCO, TAMANHO_BLOCO), 2)

        superficie.blit(superficie_fantasma, (MARGEM_X, MARGEM_Y))

    # Sistemas de partículas
    jogo.particulas_linhas.draw(superficie)
    jogo.particulas_impacto.draw(superficie)


def desenhar_peca(superficie, jogo, peca=None, posicao=None, rotacao=None,
                  offset_x=0, offset_y=0):
    """Desenha uma peça na superficie especificada com efeito 3D."""
    if peca is None:
        peca = jogo.peca_atual
    if posicao is None:
        posicao = jogo.posicao_peca
    if rotacao is None:
        rotacao = jogo.rotacao_peca

    forma = TETROMINOS[peca][rotacao]
    cor = CORES_TETROMINOS[peca]

    for linha_peca, linha in enumerate(forma):
        for coluna_peca, celula in enumerate(linha):
            if celula:
                x = MARGEM_X + (posicao[1] + coluna_peca) * TAMANHO_BLOCO + offset_x
                y = MARGEM_Y + (posicao[0] + linha_peca) * TAMANHO_BLOCO + offset_y
                desenhar_bloco(superficie, x, y, TAMANHO_BLOCO, cor)


def desenhar_peca_mini(superficie, peca, rotacao, offset_x=0, offset_y=0,
                       tamanho_bloco=8):
    """Desenha uma peça pequena (pré-visualização) em posição de pixels."""
    forma = TETROMINOS[peca][rotacao]
    cor = CORES_TETROMINOS[peca]
    for linha_peca, linha in enumerate(forma):
        for coluna_peca, celula in enumerate(linha):
            if celula:
                x = offset_x + coluna_peca * tamanho_bloco
                y = offset_y + linha_peca * tamanho_bloco
                pygame.draw.rect(superficie, cor, (x, y, tamanho_bloco, tamanho_bloco))
                pygame.draw.rect(superficie, BRANCO, (x, y, tamanho_bloco, tamanho_bloco), 1)


def desenhar_interface(superficie, jogo):
    """Desenha a interface do jogo com painéis organizados."""
    # Painel de pontuação (esquerda)
    painel_largura = 200
    painel_altura = 175
    pygame.draw.rect(superficie, UI_PAINEL, (10, 10, painel_largura, painel_altura), border_radius=10)
    pygame.draw.rect(superficie, UI_BORDA, (10, 10, painel_largura, painel_altura), 2, border_radius=10)

    fonte_titulo = pygame.font.Font(None, 28)
    fonte_valor = pygame.font.Font(None, 36)
    fonte_pequena = pygame.font.Font(None, 22)

    texto_titulo = fonte_titulo.render('QUADRIX', True, UI_DESTAQUE)
    superficie.blit(texto_titulo, (20, 20))

    # Pontuação
    texto_pontuacao_label = fonte_pequena.render('PONTUAÇÃO', True, UI_TEXTO_SUAVE)
    superficie.blit(texto_pontuacao_label, (20, 58))
    texto_pontuacao_valor = fonte_valor.render(f'{jogo.pontuacao:>6}', True, UI_DESTAQUE)
    superficie.blit(texto_pontuacao_valor, (20, 84))

    # Nível
    texto_nivel_label = fonte_pequena.render('NÍVEL', True, UI_TEXTO_SUAVE)
    superficie.blit(texto_nivel_label, (20, 124))
    texto_nivel_valor = fonte_valor.render(f'{jogo.nivel:>2}', True, UI_SUCESSO)
    superficie.blit(texto_nivel_valor, (20, 150))

    # Linhas
    texto_linhas_label = fonte_pequena.render('LINHAS', True, UI_TEXTO_SUAVE)
    superficie.blit(texto_linhas_label, (20, 218))
    texto_linhas_valor = fonte_valor.render(f'{jogo.linhas_limpas:>3}', True, UI_ACAO)
    superficie.blit(texto_linhas_valor, (20, 244))

    # Tempo (modo ULTRA)
    if jogo.modo_jogo == "ULTRA" and jogo.tempo_inicio is not None:
        tempo_restante = max(0, jogo.modo_config["tempo_limite"] - (time.time() - jogo.tempo_inicio))
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

    for i, proxima_peca in enumerate(jogo.fila_proximas[:5]):
        quadro_y = quadro_y_inicial + i * espacamento
        pygame.draw.rect(superficie, UI_FUNDO, (quadro_x - 2, quadro_y - 2, quadro_largura + 4, quadro_altura + 4), border_radius=6)
        pygame.draw.rect(superficie, UI_PAINEL, (quadro_x, quadro_y, quadro_largura, quadro_altura), border_radius=6)
        pygame.draw.rect(superficie, UI_BORDA, (quadro_x, quadro_y, quadro_largura, quadro_altura), 2, border_radius=6)

        forma_proxima = TETROMINOS[proxima_peca][0]
        bloco_prev = 7
        largura_preview = len(forma_proxima[0]) * bloco_prev
        altura_preview = len(forma_proxima) * bloco_prev
        inicio_x = quadro_x + (quadro_largura - largura_preview) // 2
        inicio_y = quadro_y + (quadro_altura - altura_preview) // 2
        desenhar_peca_mini(superficie, proxima_peca, 0, inicio_x, inicio_y, bloco_prev)

    # --- Peça segurada (zona inferior direita) ---
    texto_held_label = fonte_titulo.render('SEGURAR', True, UI_DESTAQUE)
    superficie.blit(texto_held_label, (LARGURA_JANELA - 160, 370))

    held_quadro_largura = 100
    held_quadro_altura = 100
    held_quadro_x = LARGURA_JANELA - 140
    held_quadro_y = 395
    pygame.draw.rect(superficie, UI_FUNDO, (held_quadro_x - 2, held_quadro_y - 2, held_quadro_largura + 4, held_quadro_altura + 4), border_radius=8)
    pygame.draw.rect(superficie, UI_PAINEL, (held_quadro_x, held_quadro_y, held_quadro_largura, held_quadro_altura), border_radius=8)
    pygame.draw.rect(superficie, UI_BORDA, (held_quadro_x, held_quadro_y, held_quadro_largura, held_quadro_altura), 2, border_radius=8)

    if jogo.hold_peca is not None:
        forma_held = TETROMINOS[jogo.hold_peca][0]
        bloco_held = 14
        held_largura_preview = len(forma_held[0]) * bloco_held
        held_altura_preview = len(forma_held) * bloco_held
        held_inicio_x = held_quadro_x + (held_quadro_largura - held_largura_preview) // 2
        held_inicio_y = held_quadro_y + (held_quadro_altura - held_altura_preview) // 2
        desenhar_peca_mini(superficie, jogo.hold_peca, 0, held_inicio_x, held_inicio_y, bloco_held)
    else:
        fonte_vazio = pygame.font.Font(None, 20)
        texto_vazio = fonte_vazio.render("VAZIO", True, UI_TEXTO_SUAVE)
        superficie.blit(texto_vazio,
                        (held_quadro_x + held_quadro_largura // 2 - texto_vazio.get_width() // 2,
                         held_quadro_y + held_quadro_altura // 2 - texto_vazio.get_height() // 2))


def desenhar_tela_pausa(superficie, jogo):
    """Desenha o menu de pausa com estilo do menu principal."""
    desenhar_painel(superficie)
    desenhar_bordas(superficie)

    fonte_titulo = pygame.font.Font(None, 96)
    desenhar_titulo_contorno(
        superficie, 'PAUSADO', fonte_titulo,
        LARGURA_JANELA // 2, ALTURA_JANELA // 4,
    )

    fonte_sub = pygame.font.Font(None, 30)
    texto_centralizado(
        superficie, 'O jogo está pausado',
        fonte_sub, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA // 4 + 80,
    )

    fonte_opcao = pygame.font.Font(None, 44)
    y_inicial = ALTURA_JANELA // 4 + 155
    espacamento = 50
    largura_pastilha = 340
    altura_pastilha = 48

    for i, opcao in enumerate(jogo.opcoes_pausa):
        y = y_inicial + i * espacamento
        x_pastilha = LARGURA_JANELA // 2 - largura_pastilha // 2
        if i == jogo.menu_pausa_selecionado:
            desenhar_pastilha_selecao(superficie, x_pastilha, y, largura_pastilha, altura_pastilha)
            cor = UI_DESTAQUE
            indicador = "> "
        else:
            cor = UI_TEXTO
            indicador = "  "
        texto_opcao = fonte_opcao.render(indicador + opcao, True, cor)
        superficie.blit(texto_opcao,
                        (LARGURA_JANELA // 2 - texto_opcao.get_width() // 2, y))

    fonte_dica = pygame.font.Font(None, 24)
    texto_centralizado(
        superficie, "SETAS: navegar   ENTER: selecionar   ESC: voltar ao jogo",
        fonte_dica, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA - 40,
    )


def desenhar_tela_fim_jogo(superficie, jogo):
    """Desenha a tela de fim de jogo com estatísticas e menu de opções."""
    desenhar_painel(superficie)
    desenhar_bordas(superficie)

    fonte_titulo = pygame.font.Font(None, 96)
    desenhar_titulo_contorno(
        superficie, 'FIM DE JOGO', fonte_titulo,
        LARGURA_JANELA // 2, ALTURA_JANELA // 4,
    )

    fonte_sub = pygame.font.Font(None, 30)
    texto_centralizado(
        superficie, 'Sua jornada acabou',
        fonte_sub, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA // 4 + 80,
    )

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
        pygame.draw.rect(superficie, UI_PAINEL, (x_card, y_stats, card_largura, card_altura), border_radius=10)
        pygame.draw.rect(superficie, UI_BORDA, (x_card, y_stats, card_largura, card_altura), 2, border_radius=10)
        texto_label = fonte_stats.render(label, True, UI_TEXTO_SUAVE)
        superficie.blit(texto_label,
                        (x_card + card_largura // 2 - texto_label.get_width() // 2,
                         y_stats + 12))
        texto_valor = fonte_stats.render(valor, True, cor)
        superficie.blit(texto_valor,
                        (x_card + card_largura // 2 - texto_valor.get_width() // 2,
                         y_stats + 30))

    # Opções do menu com pastilha de seleção
    fonte_opcao = pygame.font.Font(None, 44)
    y_inicial = ALTURA_JANELA // 2 + 80
    espacamento = 55
    largura_pastilha = 320
    altura_pastilha = 48

    for i, opcao in enumerate(jogo.opcoes_fim_jogo):
        y = y_inicial + i * espacamento
        x_pastilha = LARGURA_JANELA // 2 - largura_pastilha // 2
        if i == jogo.menu_fim_jogo_selecionado:
            desenhar_pastilha_selecao(superficie, x_pastilha, y, largura_pastilha, altura_pastilha)
            cor = UI_DESTAQUE
            indicador = "> "
        else:
            cor = UI_TEXTO
            indicador = "  "
        texto_opcao = fonte_opcao.render(indicador + opcao, True, cor)
        superficie.blit(texto_opcao,
                        (LARGURA_JANELA // 2 - texto_opcao.get_width() // 2, y))

    fonte_rodape = pygame.font.Font(None, 24)
    texto_centralizado(
        superficie, "SETAS: navegar   ENTER: selecionar   ESC: voltar ao menu",
        fonte_rodape, UI_TEXTO_SUAVE, LARGURA_JANELA // 2, ALTURA_JANELA - 40,
    )
