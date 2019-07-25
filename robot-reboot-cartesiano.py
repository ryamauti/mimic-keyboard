# -*- coding: utf-8 -*-
"""
usa o "moveRobo" e o "redefinir" do código robot-reboot-opencv.py
Gera uma lista força bruta - produto cartesiano - e aplica os movimentos.
Muito lento e não está paralelizando.
"""

import itertools
from random import shuffle

# total de tentativas
LANCES = 5

robots = [0, 1, 2, 3]
direcoes = ['N', 'S', 'O', 'L']

x0 = list(itertools.product(robots, direcoes))
x = list(itertools.product(x0, repeat=LANCES))
x0 = None
shuffle(x)

for k in range(len(x)):    
    if k % 1000 == 999:
        print('-- rodada', k+1, 'de', len(x))
        
    for m in x[k]:
        moveRobo(m[0], m[1])  
    if game == False:
        break
    redefinir()    
    
# para LANCES = 5: LOG: tempo decorrido 43s
