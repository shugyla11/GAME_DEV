import pygame


class Mapa(pygame.Surface):
    def __init__(self, estado_jogo):
        pygame.Surface.__init__(self, (estado_jogo.largura_mapa, estado_jogo.altura_mapa))
        
        self.width = estado_jogo.largura_mapa
        self.height = estado_jogo.altura_mapa


class Block(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # Initializes the block rectangle
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        # Initializes block state
        self.estado = False  # False for not broken, True for broken
        self.tick_inicial = 0
        self.tempo_animacao = 750  # Animation time in milliseconds

    def update(self, estado_jogo):
        if self.estado and self.tick_inicial == 0:
            self.tick_inicial = estado_jogo.tick_atual
        elif self.tick_inicial != 0:
            if estado_jogo.tick_atual > self.tick_inicial + self.tempo_animacao * self.i_imagem / 7:
                self.i_imagem += 1
            if self.i_imagem < 7:
                self.image = self.sprite_sheet[self.i_imagem]
            else:
                estado_jogo.blocos.remove(self)


class UnbreakBlock(Block):
    def __init__(self, estado_jogo, x, y):
# Block parameters
        self.width = estado_jogo.sprite_size[0]
        self.height = estado_jogo.sprite_size[1]
        self.x = x
        self.y = y
        self.eh_quebravel = False 
        # Initializes image
        self.image = pygame.transform.scale(pygame.image.load('assets/Blocos/blocoinquebravel.png'), (self.width, self.height))

        Block.__init__(self)


class BreakBlock(Block):
    def __init__(self, estado_jogo, x, y):
        # Block parameters
        self.width = estado_jogo.sprite_size[0]
        self.height = estado_jogo.sprite_size[1]
        self.x = x
        self.y = y
        self.eh_quebravel = True
        # Initializes block images
        self.sprite_sheet =[
            pygame.transform.scale(pygame.image.load('assets/Blocos/blocoquebraveis/blocoquebravel_0.png'), (self.width, self.height)),
            pygame.transform.scale(pygame.image.load('assets/Blocos/blocoquebraveis/blocoquebravel_1.png'), (self.width, self.height)),
            pygame.transform.scale(pygame.image.load('assets/Blocos/blocoquebraveis/blocoquebravel_2.png'), (self.width, self.height)),
            pygame.transform.scale(pygame.image.load('assets/Blocos/blocoquebraveis/blocoquebravel_3.png'), (self.width, self.height)),
            pygame.transform.scale(pygame.image.load('assets/Blocos/blocoquebraveis/blocoquebravel_4.png'), (self.width, self.height)),
            pygame.transform.scale(pygame.image.load('assets/Blocos/blocoquebraveis/blocoquebravel_5.png'), (self.width, self.height)),
            pygame.transform.scale(pygame.image.load('assets/Blocos/blocoquebraveis/blocoquebravel_6.png'), (self.width, self.height)),
        ]
        self.i_imagem = 0
        self.image = self.sprite_sheet[0]

        Block.__init__(self)

    
class Player(pygame.sprite.Sprite):
    def __init__(self, estado_jogo, x, y):
        pygame.sprite.Sprite.__init__(self)
        # Player parameters
        self.estoque_bomba = 1
        self.alcance_bomba = 1
        self.constante_velocidade = 250
        self.chuta = False
        # Image parameters
        self.sprite_width = estado_jogo.sprite_size[0]
        self.sprite_height = estado_jogo.sprite_size[1]
        self.i_imagem = 0
        self.estado = ['sul', False]  # Direction of the player and information of stopped or not
        #Sounds
        self.coloca_bomba_som = pygame.mixer.Sound('assets/Sons/colocabomba.wav')
        self.morre_som = pygame.mixer.Sound('assets/Sons/morrebomberman.wav')
        self.chuta_som = pygame.mixer.Sound('assets/Sons/chutabomba.wav')
        self.pega_powerup_som = pygame.mixer.Sound('assets/Sons/pegaitem.wav')
        #Displacement parameters
        self.tick_anterior = 0
        self.vel = [0, 0]
        #Animation parameters
        self.flag_bomba = False
        self.flag_morte = True
        self.flag_andar = True
        self.contador = 0
        self.tick_animacao = 0 # Initial tick of the animation
        self.freq_animacao = 6  # Animation frequency in hertz
        self.tempo_morte = 1000 # Time of death in milliseconds
        # Initializes standing surface make player
        self.image = self.sprite_sheet[self.estado[0]][self.i_imagem]
        self.rect = pygame.Rect(0, 0, estado_jogo.sprite_size[0], estado_jogo.sprite_size[1])
        self.rect.x = x
        self.rect.y = y


    # Updates player status
    def update(self, estado_jogo):
        # Upgrades the player's speed
        if self.estado[1]:
            if self.estado[0] == 'norte':
                self.vel = [0, -(self.constante_velocidade)]
            elif self.estado[0] == 'oeste':
                self.vel = [-(self.constante_velocidade), 0]
            elif self.estado[0] == 'sul':
                self.vel = [0, self.constante_velocidade]
            elif self.estado[0] == 'leste':
                self.vel = [self.constante_velocidade, 0] 
        else:
            self.vel = [0, 0]
        # Atualiza a posicao do jogador
        ultima_pos = [self.rect.x, self.rect.y]
        frame_time = estado_jogo.tick_atual - self.tick_anterior
        self.tick_anterior = estado_jogo.tick_atual
        self.rect.x += self.vel[0] * frame_time / 1000
        self.rect.y += self.vel[1] * frame_time / 1000
        # Colisao com blocos
        if len(pygame.sprite.spritecollide(self, estado_jogo.blocos, False)) > 1:
            self.rect.x,self.rect.y = ultima_pos
        # Deslocamento suavizado em vertices de bloco
        elif len(pygame.sprite.spritecollide(self, estado_jogo.blocos, False)) == 1:
            bloco_colidido = pygame.sprite.spritecollide(self, estado_jogo.blocos, False)[0]
            if self.estado[0] == 'norte':  # Colisao para cima
                self.rect.y = ultima_pos[1]
                if self.rect.midtop[0] > bloco_colidido.rect.right:
                    self.rect.x += 1
                elif self.rect.midtop[0] < bloco_colidido.rect.left:
                    self.rect.x -= 1
                else:
                    self.rect.x = ultima_pos[0]
            elif self.estado[0] == 'leste':  # ... direita
                self.rect.x = ultima_pos[0]
                if self.rect.midright[1] > bloco_colidido.rect.bottom:
                    self.rect.y += 1
                elif self.rect.midright[1] < bloco_colidido.rect.top:
                    self.rect.y -= 1
                else:
                    self.rect.y = ultima_pos[1]
            elif self.estado[0] == 'sul':  # ... baixo
                self.rect.y = ultima_pos[1]
                if self.rect.midbottom[0] > bloco_colidido.rect.right:
                    self.rect.x += 1
                elif self.rect.midbottom[0] < bloco_colidido.rect.left:
                    self.rect.x -= 1
                else:
                    self.rect.y = ultima_pos[1]
            elif self.estado[0] == 'oeste':  # ...esquerda
                self.rect.x = ultima_pos[0]
                if self.rect.midleft[1] > bloco_colidido.rect.bottom:
                    self.rect.y += 1
                elif self.rect.midleft[1] < bloco_colidido.rect.top:
                    self.rect.y -= 1
                else:
                    self.rect.x = ultima_pos[0]
        # Colisao com outros players
        if len(pygame.sprite.spritecollide(self, estado_jogo.jogadores, False)) > 1:
            self.rect.x, self.rect.y = ultima_pos
        # Colisao com explosao
        if len(pygame.sprite.spritecollide(self, estado_jogo.explosoes, False)) > 0:
            self.estado = ['morte', False]
        # Colisao com powerup
        if len(pygame.sprite.spritecollide(self, estado_jogo.powerups, False)) > 0:
            powerup_colidido = pygame.sprite.spritecollide(self, estado_jogo.powerups, False)[0]
            self.pega_powerup_som.play()
            if powerup_colidido.tipo == 'estoque':
                self.estoque_bomba += 1
                estado_jogo.powerups.remove(powerup_colidido)
            elif powerup_colidido.tipo == 'explosao':
                self.alcance_bomba += 1
                estado_jogo.powerups.remove(powerup_colidido)
            elif powerup_colidido.tipo == 'velocidade':
                self.constante_velocidade += 50
                estado_jogo.powerups.remove(powerup_colidido)
            elif powerup_colidido.tipo == 'chute' and not self.chuta:
                self.chuta = True
                estado_jogo.powerups.remove(powerup_colidido)
        # Colisao com bomba
        if len(pygame.sprite.spritecollide(self, estado_jogo.bombas, False)) > 0 and self.flag_bomba:
            if self.chuta:
                self.chuta_som.play()
                bomba_colidida = pygame.sprite.spritecollide(self, estado_jogo.bombas, False)[0]
                bomba_colidida.movimenta(self.estado[0])
        elif len(pygame.sprite.spritecollide(self, estado_jogo.bombas, False)) == 0 and not self.flag_bomba:
            self.flag_bomba = True

        # Atualiza a imagem do jogador
        if self.estado[0] == 'morte' and self.flag_morte:
            self.morre_som.play()
            self.tick_animacao = estado_jogo.tick_atual
            self.i_imagem = 0
            self.flag_morte = False
        elif not self.flag_morte:
            if estado_jogo.tick_atual > self.tick_animacao + self.tempo_morte * (self.i_imagem + 1) / len(self.sprite_sheet['morte']):
                self.i_imagem += 1
            if not self.i_imagem < len(self.sprite_sheet['morte']):
                estado_jogo.jogadores.remove(self)
            else:
                self.image = self.sprite_sheet['morte'][self.i_imagem]

        else:
            if ultima_pos == [self.rect.x, self.rect.y]:
                self.i_imagem = 0
                self.flag_andar = True
            elif self.flag_andar:
                self.tick_animacao = estado_jogo.tick_atual
                self.contador = 0
                self.flag_andar = False
            if estado_jogo.tick_atual > self.tick_animacao + (1000 / self.freq_animacao) * self.contador and not self.flag_andar:
                self.contador += 1
                self.i_imagem = (self.i_imagem + 1) % len(self.sprite_sheet[self.estado[0]])

            self.image = self.sprite_sheet[self.estado[0]][self.i_imagem]

    def cria_bomba(self, estado_jogo):
        if self.estoque_bomba > 0:
            self.estoque_bomba -= 1
            pos_x_arredondado = round(self.rect.x / self.sprite_width) * self.sprite_width
            pos_y_arredondado = round(self.rect.y / self.sprite_height) * self.sprite_height
            estado_jogo.bombas.add(Bomb(self.cor, pos_x_arredondado, pos_y_arredondado, estado_jogo, self.alcance_bomba))
            self.coloca_bomba_som.play()


class PlayerWhite(Player):  
    def __init__(self, estado_jogo, x, y):
        self.width, self.height = estado_jogo.sprite_size[0], estado_jogo.sprite_size[1] * 1.6
        self.cor = 'white'
        self.sprite_sheet = {
            'norte': [
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoNorte/branconorte_0.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoNorte/branconorte_1.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoNorte/branconorte_2.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoNorte/branconorte_3.png'), (self.width, self.height)),
            ],
            'oeste': [
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoOeste/brancooeste_0.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoOeste/brancooeste_1.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoOeste/brancooeste_2.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoOeste/brancooeste_3.png'), (self.width, self.height)),
            ],
            'sul': [
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoSul/brancosul_0.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoSul/brancosul_1.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoSul/brancosul_2.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoSul/brancosul_3.png'), (self.width, self.height)),
            ],
            'leste': [
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoLeste/brancoleste_0.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoLeste/brancoleste_1.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoLeste/brancoleste_2.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoLeste/brancoleste_3.png'), (self.width, self.height)),
            ],
            'morte': [
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoMorte/brancomorte_0.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoMorte/brancomorte_1.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoMorte/brancomorte_2.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoMorte/brancomorte_3.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoMorte/brancomorte_4.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerBranco/BrancoMorte/brancomorte_5.png'), (self.width, self.height)),
            ]
        }
        
        Player.__init__(self, estado_jogo, x, y)


class PlayerBlack(Player):
    def __init__(self, estado_jogo, x, y):
        self.width, self.height = estado_jogo.sprite_size[0], estado_jogo.sprite_size[1] * 1.6
        self.cor = 'black'
        self.sprite_sheet = {
            'norte': [
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoNorte/pretonorte_0.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoNorte/pretonorte_1.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoNorte/pretonorte_2.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoNorte/pretonorte_3.png'), (self.width, self.height)),
            ],
            'oeste': [
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoOeste/brancooeste_0.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoOeste/brancooeste_1.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoOeste/brancooeste_2.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoOeste/brancooeste_3.png'), (self.width, self.height)),
            ],
            'sul': [
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoSul/pretosul_0.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoSul/pretosul_1.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoSul/pretosul_2.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoSul/pretosul_3.png'), (self.width, self.height)),
            ],
            'leste': [
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoLeste/pretoleste_0.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoLeste/pretoleste_1.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoLeste/pretoleste_2.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoLeste/pretoleste_3.png'), (self.width, self.height)),
            ],
            'morte': [
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoMorte/pretomorte_0.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoMorte/pretomorte_1.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoMorte/pretomorte_2.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoMorte/pretomorte_3.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoMorte/pretomorte_4.png'), (self.width, self.height)),
                pygame.transform.scale(pygame.image.load('assets/PlayerPreto/PretoMorte/pretomorte_5.png'), (self.width, self.height)),
            ]
        }

        Player.__init__(self, estado_jogo, x, y)


class Bomb(pygame.sprite.Sprite):
    def __init__(self, player, x, y, estado_jogo, alcance):
        pygame.sprite.Sprite.__init__(self)
        self.width = estado_jogo.sprite_size[0]
        self.height = estado_jogo.sprite_size[1]
        # Inicializa imagens da bomba
        self.sprite_sheet = [
            pygame.transform.scale(pygame.image.load('assets/Bomba/bomb_0.png'), (self.width, self.height)),
            pygame.transform.scale(pygame.image.load('assets/Bomba/bomb_1.png'), (self.width, self.height)),
            pygame.transform.scale(pygame.image.load('assets/Bomba/bomb_2.png'), (self.width, self.height)),
        ]
        self.ind_imagem = 0
        self.fase_imagem = 1
        self.image = self.sprite_sheet[self.ind_imagem]
        # Sons
        self.explode_som = pygame.mixer.Sound('assets/Sons/explodebomba.wav')
        # Inicializa retangulo da bomba
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Inicializa parametros da bomba
        self.tick_inicial = pygame.time.get_ticks()
        self.vel = [0,0]
        self.tick_anterior = 0
        self.alcance = alcance
        self.player = player
    
    def movimenta(self, direcao):
        if direcao == 'norte':
            self.vel = [0, -300]
        elif direcao == 'leste':
            self.vel = [300, 0]
        elif direcao == 'sul':
            self.vel = [0, 300]
        elif direcao == 'oeste':
            self.vel = [-300, 0]

    def update(self, estado_jogo):
        # Atualiza posicao da bomba
        ultima_pos = [self.rect.x, self.rect.y]
        frame_time = estado_jogo.tick_atual - self.tick_anterior
        self.tick_anterior = estado_jogo.tick_atual
        self.rect.x += self.vel[0] * frame_time / 1000
        self.rect.y += self.vel[1] * frame_time / 1000
        # Colisao com blocos
        if len(pygame.sprite.spritecollide(self, estado_jogo.blocos, False)) > 0:
            self.rect.x, self.rect.y = ultima_pos
            self.vel = [0, 0]
        # Colisao com jogadores
        if len(pygame.sprite.spritecollide(self, estado_jogo.jogadores, False)) > 0 and pygame.sprite.spritecollide(self, estado_jogo.jogadores, False)[0].cor != self.player:
            self.rect.x, self.rect.y = ultima_pos
            self.vel = [0, 0]
        if estado_jogo.tick_atual > self.tick_inicial + 500 * self.fase_imagem:
            self.fase_imagem += 1
            self.ind_imagem = self.fase_imagem % 3
            self.image = self.sprite_sheet[self.ind_imagem]
        
        if estado_jogo.tick_atual > self.tick_inicial + 3000:
            self.explode_bomba(estado_jogo)

    def explode_bomba(self, estado_jogo):
        self.explode_som.play()
        estado_jogo.bombas.remove(self)
        if self.player == 'white': 
            estado_jogo.jogador_um.estoque_bomba += 1
        elif self.player == 'black':
            estado_jogo.jogador_dois.estoque_bomba += 1
        # Constroe a explosao
        tick_inicial = estado_jogo.tick_atual
        pos_x_arredondado = round(self.rect.x / self.width) * self.width
        pos_y_arredondado = round(self.rect.y / self.height) * self.height
        for a in range(5):
            i = 0
            colide_bloco = False
            while i < self.alcance and not colide_bloco:
                i += 1
                if i == self.alcance:
                    fase = 2
                else:
                    fase = 1
                if a == 0:
                    explosao = Explosao(estado_jogo, pos_x_arredondado, pos_y_arredondado, 0, 'leste', tick_inicial)  # Desenha o centro da explosao
                if a == 1:
                    explosao = Explosao(estado_jogo, pos_x_arredondado + self.width * i, pos_y_arredondado, fase, 'leste', tick_inicial)  # ... o leste
                elif a == 2:
                    explosao = Explosao(estado_jogo, pos_x_arredondado , pos_y_arredondado - self.height * i, fase, 'norte', tick_inicial)  # ... o norte
                elif a == 3:
                    explosao = Explosao(estado_jogo, pos_x_arredondado - self.width * i, pos_y_arredondado, fase, 'oeste', tick_inicial)  # ... o oeste
                elif a == 4:
                    explosao = Explosao(estado_jogo, pos_x_arredondado , pos_y_arredondado + self.height * i, fase, 'sul', tick_inicial)  # ... o sul

                if len(pygame.sprite.spritecollide(explosao, estado_jogo.blocos, False)) > 0:
                    colide_bloco = True
                    bloco_colidido = pygame.sprite.spritecollide(explosao, estado_jogo.blocos, False)[0]
                    if bloco_colidido.eh_quebravel:
                        bloco_colidido.estado = True

                else:
                    estado_jogo.explosoes.add(explosao)
                    

class Explosao(pygame.sprite.Sprite):
    def __init__(self, estado_jogo, x, y, parte, orientacao, tick_inicial):
        pygame.sprite.Sprite.__init__(self)

        self.width = estado_jogo.sprite_size[0]
        self.height = estado_jogo.sprite_size[1]
        # Inicializa imagens da explosao
        self.sprite_sheet = [
            [pygame.image.load('assets/Explosao/ExplosaoA/explosionA_0.png'),
             pygame.image.load('assets/Explosao/ExplosaoA/explosionA_1.png'),
             pygame.image.load('assets/Explosao/ExplosaoA/explosionA_2.png'),],
            [pygame.image.load('assets/Explosao/ExplosaoB/explosionB_0.png'),
             pygame.image.load('assets/Explosao/ExplosaoB/explosionB_1.png'),
             pygame.image.load('assets/Explosao/ExplosaoB/explosionB_2.png'),],
            [pygame.image.load('assets/Explosao/ExplosaoC/explosionC_0.png'),
             pygame.image.load('assets/Explosao/ExplosaoC/explosionC_1.png'),
             pygame.image.load('assets/Explosao/ExplosaoC/explosionC_2.png'),],
            [pygame.image.load('assets/Explosao/ExplosaoD/explosionD_0.png'),
             pygame.image.load('assets/Explosao/ExplosaoD/explosionD_1.png'),
             pygame.image.load('assets/Explosao/ExplosaoD/explosionD_2.png'),],
            [pygame.image.load('assets/Explosao/ExplosaoE/explosionE_0.png'),
             pygame.image.load('assets/Explosao/ExplosaoE/explosionE_1.png'),
             pygame.image.load('assets/Explosao/ExplosaoE/explosionE_2.png'),],
        ]
        if orientacao == 'leste':
            self.inclinacao = 0
        if orientacao == 'norte':
            self.inclinacao = 90
        elif orientacao == 'oeste':
            self.inclinacao = 180
        elif orientacao == 'sul':
            self.inclinacao = 270
        self.ind_fase = 0
        self.ind_parte = parte
        image = pygame.transform.rotate(self.sprite_sheet[self.ind_fase][self.ind_parte], self.inclinacao)
        self.image = pygame.transform.scale(image, (self.width, self.height))
        #Initializes explosion parameters
        self.tempo_explosao = 500  # Explosion time in milliseconds
        self.tick_inicial = tick_inicial
        self.ind_fase = 0
        self.contador = 1
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, estado_jogo):
        if self.contador < 5:
            if estado_jogo.tick_atual > self.tick_inicial + self.tempo_explosao * self.contador / 10:
                self.ind_fase += 1
                self.contador += 1
                image = pygame.transform.rotate(self.sprite_sheet[self.ind_fase][self.ind_parte], self.inclinacao)
                self.image = pygame.transform.scale(image, (self.width, self.height))
        elif self.contador < 10:
            if estado_jogo.tick_atual > self.tick_inicial + self.tempo_explosao * self.contador / 10:
                self.ind_fase -= 1
                self.contador += 1
                image = pygame.transform.rotate(self.sprite_sheet[self.ind_fase][self.ind_parte], self.inclinacao)
                self.image = pygame.transform.scale(image, (self.width, self.height))
        else:
            estado_jogo.explosoes.remove(self)  # Remove the explosion


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, estado_jogo, x, y, tipo):
        pygame.sprite.Sprite.__init__(self)
        self.width = estado_jogo.sprite_size[0]
        self.height = estado_jogo.sprite_size[1]
        self.tipo = tipo
        # Initializes image of powerups
        if tipo == 'estoque':
            self.image = pygame.transform.scale(pygame.image.load('assets/PowerUps/estoque_powerup.png'), (self.width, self.height))
        elif tipo == 'explosao':
            self.image = pygame.transform.scale(pygame.image.load('assets/PowerUps/explosao_powerup.png'), (self.width, self.height))
        elif tipo == 'velocidade':
            self.image = pygame.transform.scale(pygame.image.load('assets/PowerUps/velocidade_powerup.png'), (self.width, self.height))
        elif tipo == 'chute':
            self.image = pygame.transform.scale(pygame.image.load('assets/PowerUps/chute_powerup.png'), (self.width, self.height))
        #Initializes PowerUp rectangle
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y