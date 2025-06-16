# KodPy - Jogo de Plataforma 2D

Bem-vindo ao **KodPy**, um jogo de plataforma 2D desenvolvido com Pygame Zero! Neste jogo, você controla um personagem que navega por um mundo gerado dinamicamente, enfrentando inimigos como aranhas e abelhas, ganhando pontos e evitando perder vidas. Com gráficos simples, música de fundo e controles intuitivos, KodPy oferece uma experiência divertida e desafiadora.

## Funcionalidades

- **Mundo Infinito**: Plataformas e inimigos são gerados dinamicamente conforme o jogador avança.
- **Inimigos Variados**: Enfrente aranhas (movimento horizontal) e abelhas (movimento vertical).
- **Sistema de Vidas e Pontuação**: O jogador começa com 5 vidas e ganha pontos ao passar por inimigos.
- **Controles Simples**: Use as setas para mover, espaço para pular e o mouse para interagir com o menu.
- **Menu Interativo**: Inclui botões para iniciar o jogo, ativar/desativar som e sair.
- **Animações e Sons**: Sprites animados para o jogador e inimigos, além de efeitos sonoros para pulos e colisões.

## Requisitos

- **Python 3.6+**
- **Pygame Zero** (instalável via `pip install pgzero`)
- Arquivos de assets (sprites e sons), incluídos no repositório nas pastas:
  - Sprites: `player_idle/`, `player_walk/`, `enemy/spider/`, `enemy/bee/`, `menu/`
  - Sons: `jump`, `hit`, `bg_music`

## Instalação

1. Clone o repositório:

   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd kodpy
   ```

2. Instale o Pygame Zero:

   ```bash
   pip install pgzero
   ```

3. Execute o jogo:

   ```bash
   pgzrun game.py
   ```

## Como Jogar

- **Menu Principal**:
  - Clique em "Start" para começar.
  - Clique no ícone de som para ativar/desativar música e efeitos.
  - Clique em "Exit" para sair.
- **No Jogo**:
  - **Setas Esquerda/Direita**: Mover o personagem.
  - **Espaço**: Pular.
  - Evite colisões com inimigos para não perder vidas.
  - Passe por inimigos para ganhar pontos.
  - Se as vidas chegarem a zero, a tela de "Game Over" aparece. Clique para voltar ao menu.

## Estrutura do Código

O código está organizado em seções lógicas no arquivo `game.py` para facilitar a leitura e manutenção:

- **Configurações do Jogo**: Constantes, estados e variáveis globais.
- **Classes do Jogo**: Inclui `Player`, `Platform`, `Enemy`, `Spider` e `Bee`.
- **Instâncias Globais**: Objetos principais como o jogador e botões do menu.
- **Funções do Jogo**: Lógica principal, como geração de mundo e atualizações.
- **Funções de Interface**: Desenho do menu, jogo e tela de game over.
- **Funções Auxiliares**: Reset, colisões e controle de som.
