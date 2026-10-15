# Quadrix

Um clone moderno de Tetris construído com Python e Pygame.

## Sobre

Quadrix é um jogo de Tetris completo com múltiplos modos de jogo, sistema de conquistas, recordes por modo, partículas visuais, peça fantasma, lock delay, soft drop, hold (peça segurada), 7-bag randomizer e wall kicks.

Desenvolvido em português do Brasil.

## Modos de jogo

| Modo | Descrição |
|------|-----------|
| **Clássico** | Tetris tradicional. Jogue até não haver mais espaço. |
| **Maratona** | Jogo contínuo sem fim. A velocidade aumenta gradualmente. |
| **Sprint** | Limpe 40 linhas o mais rápido possível. |
| **Ultra** | Jogue por 2 minutos e maximize sua pontuação. |
| **Blitz** | Velocidade muito rápida desde o início. |
| **Practice** | Modo treino. Sem game over. |

## Como jogar

### Controles

| Tecla | Ação |
|-------|------|
| ← / → | Mover a peça |
| ↓ | Soft drop (queda mais rápida) |
| ↑ | Rotacionar a peça (com wall kicks) |
| Espaço | Queda rápida (hard drop) |
| C | Segurar / trocar peça (hold) |
| P / ESC | Pausar |
| R (Recordes/Conquistas) | Resetar recordes ou conquistas |

### Telas de menu

- **Menu principal**: JOGAR, INSTRUÇÕES, RECORDES, CONQUISTAS, OPÇÕES, SAIR
- **Seleção de modo**: Escolha entre os 6 modos de jogo
- **Explicação do modo**: Descrição do modo selecionado antes de iniciar

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/quadrix.git
cd quadrix

# Crie um ambiente virtual (opcional, recomendado)
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/macOS

# Instale as dependências
pip install -r requirements.txt

# Execute o jogo
python -m quadrix
```

Ou instale como pacote:

```bash
pip install .
quadrix
```

## Estrutura do projeto

```
quadrix/
├── __init__.py        # Pacote + versão
├── __main__.py        # Entrada: python -m quadrix
├── main.py            # Loop principal, estado do jogo, Tetris
├── config.py          # Constantes, cores, configurações de modo
├── states.py          # Constantes de estados do jogo
├── tetrominoes.py     # Formas das peças, wall kicks
├── particles.py       # Sistema de partículas
├── save.py            # Salvamento/carregamento de progresso
└── renderer.py        # Toda a renderização (desenhar_*)
assets/
└── images/
    └── icon.png       # Ícone da janela
tests/
└── test_*.py          # Testes unitários
quadrix_progresso.json # Progresso salvo (conquistas + recordes)
pyproject.toml
requirements.txt
README.md
LICENSE
```

## Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -e .

# Executar testes
python -m pytest tests/  # ou python -m unittest discover tests

# Verificar estilo
python -m py_compile quadrix/*.py
```

