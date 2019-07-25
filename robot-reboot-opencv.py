# -*- coding: utf-8 -*-
"""
requires:
    opencv-python    
    
Captura a tela do Robot Reboot e gera uma arena jogável
http://www.robotreboot.com/

Permite dois modos de obtenção de imagem. 
O que está configurado (por volta da linha 40) é ler da área de transferência.

Interações possíveis:
- comando "moveRobo(cor, direcao)", onde cor é numérico de 0 a 3, e direção é 'N', 'S', 'L', 'O'
- comando "desenhaArena(mapa, robo, alvo)" sem mudar as variáveis, gera a representação da tela

Variáveis relevantes:
- mapa, robos, alvo: configuram o ambiente
- loga: guarda os movimentos realizados via moveRobo

Próximos passos:
- Implementar um gerador de lances, sendo que há um exemplo no código "robot-reboot-teclado.py"
- obter as posições dos robôs e da estrela via leitura da página
- implementar heurística para reduzir as tentativas: por exemplo, identificar quando é possível ganhar em um lance.
- durante as iterações, trabalhar com uma forma compacta do Mapa deve trazer ganhos de velocidade.
"""

# também podem ser obtidas da página de configuração:
# http://www.robotreboot.com/challenge/config
verde = 5, 13
azul = 9, 6
vermelho = 12, 13
amarelo = 5, 3
estrela = 'amarelo', 4, 13


import numpy as np
import PIL.ImageGrab
import cv2


def importaImagemCopiada():
    pil_image = PIL.ImageGrab.grabclipboard()
    imgcv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return imgcv


def importaImagemArquivo():
    img = 'robot-screenshot.png'
    imgcv = cv2.imread(img)
    return imgcv


arena = importaImagemCopiada()


manual_threshold = 120
for x in arena:
    for y in x:
        
        if (y[0] < manual_threshold and 
            y[1] < manual_threshold and
            y[2] < manual_threshold):
            y[0], y[1], y[2] = 0, 0, 0
        else:
            y[0], y[1], y[2] = 255, 255, 255
            
            
# convert the resized image to grayscale, blur it slightly,
# and threshold it
gray = cv2.cvtColor(arena, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# print(len(contours))

def pontos(n):
    vert = set()
    for elem in contours[n]:
        x = elem[0][0]
        y = elem[0][1]
        vert.add((x, y))    
    return vert


def dimensoes(pg):
    x = list()
    y = list()
    for k in pg:
        x.append(k[0])
        y.append(k[1])
    return (max(x) - min(x), max(y) - min(y)) ,(min(x), min(y)), (max(x), max(y))


raw = list()
for i in range(len(contours)):
    temp = dict()
    temp['indice'] = i
    p = pontos(i)
    temp['pontos'] = p
    temp['dimensao'], temp['canto-sup-esq'], temp['canto-inf-dir'] = dimensoes(p)
    raw.append(temp)

# a arena sera uma lista de lista de dicionários                               N
# cada ponto [x][y] possui quatro variáveis: Norte, Sul, Leste, Oeste.       O + L
# cada variável tem atribuição zero para sem barreira e um para com barreira   S


TAM = 16

mapa = list()
for row in range(TAM):
    mapa.append(list())
   
for row in mapa:
    for col in range(TAM):
        temp = {'N': 0, 'S': 0, 'L': 0, 'O': 0}        
        row.append(temp)
        
def alocaMapa(x, y, tipo, mapa, fator = 1):
    if tipo == 'N':
        mapa[x][y]['N'] += fator
        if y > 0:
            mapa[x][y-1]['S'] += fator
    if tipo == 'S':
        mapa[x][y]['S'] += fator
        if y < 15:
            mapa[x][y+1]['N'] += fator
    if tipo == 'O':
        mapa[x][y]['O'] += fator
        if x > 0:
            mapa[x-1][y]['L'] += fator
    if tipo == 'L':
        mapa[x][y]['L'] += fator
        if x < 15:
            mapa[x+1][y]['O'] += fator
    return mapa
    

# bordas:
for k in range(TAM):
    mapa = alocaMapa(0, k, 'O', mapa)
    mapa = alocaMapa(15, k, 'L', mapa)
    mapa = alocaMapa(k, 0, 'N', mapa)
    mapa = alocaMapa(k, 15, 'S', mapa)

# miolo:
for k in range(7, 9):
    mapa = alocaMapa(7, k, 'O', mapa)
    mapa = alocaMapa(8, k, 'L', mapa)
    mapa = alocaMapa(k, 7, 'N', mapa)
    mapa = alocaMapa(k, 8, 'S', mapa)


# ciclo para achar o indice da borda:
for k in range(len(contours)):
    d = raw[k]['dimensao']
    cse = raw[k]['canto-sup-esq']
    if d[0] == d[1] and cse != (0, 0):
        dimMapa = d[0]
        cid = raw[k]['canto-inf-dir']
        kini = k
        break
        
        
    
for k in range(kini, len(contours)):
    # se a borda está abaixo ou à direita do fim do tabuleiro, ignore
    tmpcse = raw[k]['canto-sup-esq']    
    if tmpcse[0] > cid[0] or tmpcse[1] > cid[1]:
        continue
    tempset = set()
    for elem in raw[k]['pontos']:    
        tempx = (elem[0]-cse[0])*16/dimMapa
        tempy = (elem[1]-cse[1])*16/dimMapa
        tempset.add((int(round(tempx)), int(round(tempy))))
    #print(k, tempset)
    
    if len(tempset) > 1:
        for (x, y) in tempset:
            if (x-1, y) in tempset:
                mapa = alocaMapa(x-1, y-1, 'S', mapa)
            if (x, y-1) in tempset:
                mapa = alocaMapa(x-1, y-1, 'L', mapa)
                
                
# Dinamica do jogo        
game = True
robos = [(), (), (), ()]
alvo = ()
loga = list()

def pareRobo(cor, x, y):
    robos[cor] = (x, y)
    if (cor, x, y) == alvo:
        game = False
        print('Sucesso')        
        print(str(loga))
    roboEstado(cor, 'para')    


move = dict()
move['N'] = lambda x, y: (x, y - 1)
move['S'] = lambda x, y: (x, y + 1)
move['O'] = lambda x, y: (x - 1, y)
move['L'] = lambda x, y: (x + 1, y)


def moveRobo(cor, direcao):
    global loga
    loga.append(str(cor) + direcao)
    x, y = robos[cor]
    roboEstado(cor, 'move')
    for k in range(TAM):        
        if mapa[x][y][direcao] > 0:
            break
        x, y = move[direcao](x, y)
    pareRobo(cor, x, y)    
    

def roboEstado(cor, mudanca = 'para'):
    global mapa
    if mudanca == 'move':
        w = -1
    else:
        w = 1
    x, y = robos[cor]
    mapa = alocaMapa(x, y, 'O', mapa, w * (cor+1)*10)
    mapa = alocaMapa(x, y, 'L', mapa, w * (cor+1)*10)
    mapa = alocaMapa(x, y, 'N', mapa, w * (cor+1)*10)
    mapa = alocaMapa(x, y, 'S', mapa, w * (cor+1)*10)


depara = ['verde', 'azul', 'vermelho', 'amarelo']

alvo = (depara.index(estrela[0]), estrela[1], estrela[2])
pareRobo(0, verde[0], verde[1])
pareRobo(1, azul[0], azul[1])
pareRobo(2, vermelho[0], vermelho[1])
pareRobo(3, amarelo[0], amarelo[1])

                
# Desenho                
def desenhaArena(mapa, robo, alvo):
    from PIL import Image, ImageDraw
    
    SZ = 40
    borda = 20
    im = Image.new('RGB', (2 * borda + SZ * 16, 2 * borda + SZ * 16))
    draw = ImageDraw.Draw(im)
    
    # Grid
    for x in range(TAM):
        for y in range(TAM):
            draw.line((borda + x * SZ, borda + y * SZ, borda + (x + 1)*SZ, borda + y * SZ), fill=(0,0,128,64))
            draw.line((borda + x * SZ, borda + y * SZ, borda + x*SZ, borda + (y+1) * SZ), fill=(0,0,128,64))
    
    # Barreiras. Funciona tanto N + O quanto S + L pois são complementares.
    for x in range(TAM):
        for y in range(TAM):
            
            if mapa[x][y]['N'] % 10 == 1:
                draw.line((borda + x * SZ, borda + y * SZ, borda + (x + 1)*SZ, borda + y * SZ), fill=(255,0,255,255))
            if mapa[x][y]['O'] % 10 == 1:
                draw.line((borda + x * SZ, borda + y * SZ, borda + x*SZ, borda + (y+1) * SZ), fill=(255,0,255,255))       
            
            if mapa[x][y]['S'] % 10 == 1:
                draw.line((borda + x * SZ, borda + (y+1) * SZ, borda + (x + 1)*SZ, borda + (y+1) * SZ), fill=(255,0,255,255))
            if mapa[x][y]['L'] % 10 == 1:
                draw.line((borda + (x+1) * SZ, borda + y * SZ, borda + (x+1)*SZ, borda + (y+1) * SZ), fill=(255,0,255,255))     
                
    # robos:
    # 0: verde
    # 1: azul
    # 2: vermelho
    # 3: amarelo
    roboCor = [(0,255,0,255), (0,0,255,255), (255,0,0,255), (255,255,0,255)]
    raio = SZ // 3
    for r in robos:
        if len(r) > 0:
            x, y = r
            draw.ellipse((borda + x * SZ - raio + SZ // 2, borda + y * SZ - raio + SZ // 2,
                          borda + x * SZ + raio + SZ // 2, borda + y * SZ + raio + SZ // 2,), fill=roboCor[robos.index(r)])
    # alvo:
    c, x, y = alvo
    corAlvo = roboCor[c]
    draw.ellipse((borda + x * SZ - raio-1 + SZ // 2, borda + y * SZ - raio-1 + SZ // 2,
                  borda + x * SZ + raio+1 + SZ // 2, borda + y * SZ + raio+1 + SZ // 2,), outline=corAlvo)
            
    im.show()
    
#cv2.imshow("Image", arena)
#cv2.waitKey(0)

print('fim')
