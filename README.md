# Quadrix

## Objetivo

Um clone moderno de Tetris em Python com Pygame, oferecendo múltiplos modos de jogo, sistema de conquistas, recordes por modo e efeitos visuais de partículas.

## Funcionalidades

- 6 modos de jogo: Clássico, Maratona, Sprint, Ultra, Blitz e Practice
- Sistema de conquistas com desbloqueio e alerta visual
- Recordes salvos por modo de jogo em `quadrix_progresso.json`
- Peça fantasma mostrando onde a peça atual irá cair
- Lock delay, soft drop, hard drop e hold (peça segurada)
- Visualização das próximas 5 peças e da peça segurada
- Efeitos de partículas ao limpar linhas e fixar peças
- Wall kicks para rotação próxima às paredes
- Interface moderna com menus, pausar e tela de fim de jogo

## Tecnologias utilizadas

- Python 3.x
- Pygame 2.6.1

## Como executar

1. Clone o repositório
2. Instale as dependências
3. Execute o arquivo principal

```bash
pip install -r requirements.txt
python -m quadrix
```

## Integrantes

- Quadrix

## Observações

- O arquivo de progresso `quadrix_progresso.json` é criado automaticamente na raiz do projeto.
- O ícone da janela é opcional: se `assets/images/icon.png` não estiver presente, o jogo continua funcionando normalmente.
