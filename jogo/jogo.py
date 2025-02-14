import pygame
from telas import *


class Jogo:
    def __init__(self):
        pygame.init()
        self.largura_janela = 1280
        self.altura_janela = 720
        self.window = pygame.display.set_mode((self.largura_janela, self.altura_janela))
        self.melhor_de_ = 2  # this variable refers to the game mode, best of 1, 3 or 5
        self.vitorias_branco = 0
        self.vitorias_preto = 0

    def roda(self):
        tela_atual = TelaMenu(self.largura_janela, self.altura_janela)

        rodando = True
        while rodando:
            tela_atual = tela_atual.atualiza(self)
            if tela_atual == 'exit':
                rodando = False
                pygame.quit()
            else:
                tela_atual.desenha(self.window)


if True:
    Jogo().roda()