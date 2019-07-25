# -*- coding: utf-8 -*-
"""
requires:
    pyautogui 

Injeta comandos de setas na tela do Robot Reboot
http://www.robotreboot.com/

Usa WinSound para gerar cinco beeps na caixa de som.
É o tempo para alternar tarefa e abrir o jogo.
O FAILSAFE para a execução do código caso o mouse seja movido para o canto superior esquerdo da tela.
Variáveis relevantes:
- corAlvo: determina a cor do alvo
- LANCES: determina a quantidade (exata) de movimentos que serão tentados
- redoPos: coordenadas da tela do botão de reinício.
"""

import winsound
import time
import itertools

import pyautogui
from random import shuffle


def beeperSec(x = 1):
    for i in range(x):
        frequency = 440  # Set Frequency To 2500 Hertz
        duration = 100  # Set Duration To 1000 ms == 1 second
        time.sleep(0.9)
        winsound.Beep(frequency, duration)


pyautogui.FAILSAFE = True

# pyautogui.position()
# Out[9]: Point(x=950, y=507)

def redo():
    redoPos = (950, 507)
    pyautogui.click(x=redoPos[0], y=redoPos[1], clicks=1, interval=0, button='left')
    pyautogui.press('tab')
    
# 0: verde
# 1: azul
# 2: vermelho
# 3: amarelo

# Para o caso de alvo verde
corAlvo = 0 

# total de tentativas
LANCES = 4


robots = [0, 1, 2, 3]
direcoes = ['up', 'down', 'left', 'right']

x0 = list(itertools.product(robots, direcoes))
x = list(itertools.product(x0, repeat=LANCES))
# x = list(itertools.product(direcoes, repeat=3))

shuffle(x)

# comeca pela cor do alvo
roboSel = corAlvo 

x1 = list()
for linha in x:
    # termine pelo objetivo
    if linha[-1][0] == corAlvo and linha[-2][0] == corAlvo:
        novalinha = list()
        for cmd in linha:            
            for i in range((cmd[0] - roboSel) % 4):
                novalinha.append('tab')
            roboSel = cmd[0]
            novalinha.append(cmd[1])
        x1.append(novalinha)

x = None

x2 = list()
for linha in x1:
    valido = True
    for k in range(1, len(linha)):
        if linha[k-1] == linha[k] and linha[k] != 'tab':
            valido = False            
            break
        if ((linha[k-1] == 'up' and linha[k] == 'down') or
           (linha[k-1] == 'down' and linha[k] == 'up') or
           (linha[k-1] == 'left' and linha[k] == 'right') or
           (linha[k-1] == 'right' and linha[k] == 'left')):        
            valido = False            
            break
    if valido:
        x2.append(linha)            

x1 = None

print(len(x2))

beeperSec(5)


redo()

for k in range(len(x2)):    
    if k % 1000 == 999:
        print('-- rodada', k+1, 'de', len(x2))
    pyautogui.press(x2[k])    
    redo()
    
beeperSec(1)

# para repeat = 3: LOG: tempo decorrido 39.70662236213684
# para repeat = 4: LOG: tempo decorrido 487.3578681945801
