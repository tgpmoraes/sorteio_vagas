import random
import json
import sys
from pprint import pprint
from prettytable import PrettyTable
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch,cm

if len(sys.argv) < 2:
    print("Entre com o nome do arquivo de saida.")
    exit(1)

bloq = json.load(open("/home/tiago/Documents/python/vagas/torre_vaga_bloqueada.json"))
nbloq = json.load(open("/home/tiago/Documents/python/vagas/torre_vaga_nao_bloqueada.json"))
ap_qtvaga = json.load(open("/home/tiago/Documents/python/vagas/ap_qtvaga.json"))

def sorteio_vagas(bloqueada,torre):
    if bloqueada:
        vaga = random.sample(bloq[torre],1)
        # se a vaga estiver como nao bloqueada, pois durante o 
        # processo de ap com 3 vagas, foi adicionado uma para cada e sobrou
        # neste caso, foi adicionado na lista de vagas bloqueadas para
        # participar do sorteio, porem a forma de sorteio foi criado para pegar
        # uma vaga e a seguinte, sendo assim, caso a vaga sorteada seja a
        # ultima da lista de nao bloqueada, se faz necessrio pegar a anterior
        # e isso que o if abaixo faz
        if vaga[0] in nbloq[torre]:
            indice = nbloq[torre].index(vaga[0])
            tam = len(nbloq[torre])
            #Verifica o item se e o ultimo da lista
            #Se for, resolveremos comparando o indice da vaga, com o tamanho 
            #da lista - 1
            if indice == (tam - 1):
                #vaga anterior e adicionada a variavel de retorno
                vaga2 = nbloq[torre][tam - 2]
                vaga.append(vaga2)
                #Agora para manter correto a lista para sorteio,
                #e necessario retirar da lista de nao bloqueada
                nbloq[torre].remove(vaga2)
                nbloq[torre].remove(vaga[0])
            else:
                #caso a vaga sorteada, nao seja a ultma da lista,
                #sera adicionado na variavel de retorno o seguinte
                #da lista de nao bloqueado
                vaga2 = nbloq[torre][indice+1]
                vaga.append(vaga2)
                nbloq[torre].remove(vaga2)
                nbloq[torre].remove(vaga[0])                
            #Como somente dentro do if sera possivel haver a segunda
            #vaga na funcao, apos o sorteio, sera ogrigado a remover
            #da lista de bloqueadas, pois no processo abaixo, todas
            #as que sobraram da lista de nao bloqueadas, foram dispo-
            #nibilizadas para que todos pudessem ter a chance de ter
            #uma vaga nao bloqueada
            bloq[torre].remove(vaga[1])
        #Independente da vaga ser bloqueada ou nao, a mesma sera excluida
        #da lista para os proximos sorteios
        if len(bloq[torre]) > 0: bloq[torre].remove(vaga[0])
    else:
        #Processo usado apenas para vagas nao bloqueadas
        vaga = random.sample(nbloq[torre],1)
        if len(nbloq[torre]) > 0: nbloq[torre].remove(vaga[0])
    return vaga
  
#inicializar dicionario de sorteio
dict_sorteio = {}
for ap in ap_qtvaga:
    dict_sorteio[ap] = []

#adiciona vaga bloqueada ao ap
def adiciona_vaga_bloq(ap,bloqueada):
    vaga_sorteada = sorteio_vagas(bloqueada,ap[0])
    #O retorno da funcao de sorteio e uma lista de ate duas
    #vagas, porem so havera duas vagas quando a pessoa for
    #sorteada com uma vaga nao bloqueada e por isso, a mesma
    #e obrigada a ter outra vaga nao bloqueada.
    
    #No caso de haver apenas um registro no retorno da funcao,
    #e como na lista de vagas bloqueadas, existe apenas uma
    #vaga, pelo fato de obrigado adicionar a vaga a sequencia
    if len(vaga_sorteada) == 1:
        dict_sorteio[ap].append(vaga_sorteada[0])
        dict_sorteio[ap].append(vaga_sorteada[0]+1)
 
    else:
        dict_sorteio[ap].append(vaga_sorteada[0])
        dict_sorteio[ap].append(vaga_sorteada[1])    
    
#adiciona vaga nao bloqueada ao ap
def adiciona_vaga_nbloq(ap,bloqueada):
    vaga_sorteada = sorteio_vagas(bloqueada,ap[0])
    #print(vaga_sorteada)
    dict_sorteio[ap].append(vaga_sorteada[0])

#Loop para atribuir uma vaga nao bloqueada para todos os ap's que
#tem 3 vagas    
for k, v in ap_qtvaga.items(): 
    if v == 3:
        adiciona_vaga_nbloq(k,False)
#Como o processo de adicionar a vaga para o apartamento seja
#correto na hora de realizar o sorteio, e necessario retirar
#vaga da lista de sorteio, e como existem torres com mais vagas
#nao bloqueadas do que ap com 3 vagas, elas sobraram e por isso
#o processo abaixo as adicionam na lista de vagas bloqueadas
#para participarem do processo normalmente
for x in nbloq:
    y = len(nbloq[x])
    ap = nbloq[x]
    if y > 0:
        while y > 0:
            bloq[x].append(ap[y-1])
            y -= 1
    
#loop em todos os ap's para sortear vagas
for ap in dict_sorteio:
    #A funcao abaixo, adiciona dois carros e para os ap's que possuem
    #4 vagas, e executado uma vez mais
    if ap_qtvaga[ap] == 4:
        adiciona_vaga_bloq(ap,True)
    adiciona_vaga_bloq(ap,True)

torres = {'1':'Veneza','2':'Verona','3':'Vicenza','4':'Rovigo','5':'Siena','6':'Milao','7':'Florenca','8':'Treviso'}

l = []
for key, value in dict_sorteio.items():
    temp = (key, value)
    l.append(temp)

l = sorted(l, key = lambda x: x[0])

pt = PrettyTable(["Bloco", "Unidade", "Vaga"])
pt.align["Bloco"] = "l" # Alinhamento a esquerda
pt.padding_width = 1 # One space between column edges and contents (default)

for key, lists in l:
    torre = torres[key[0]]
    for item in lists:
        unidade = str(key)[1:]
        vaga = str(item) + (' - 2 SS' if item <= 256 else ' - 1 SS')
        pt.add_row([torre,unidade,vaga])
lines = pt.get_string()

pw = canvas.Canvas(sys.argv[1])

y = 11.0 * inch
dy = 0.225 * inch

aux = 0
for line in lines.split('\n'):
    if aux == 40:
        aux = 0
        y = 11.0 * inch
        page_num = pw.getPageNumber()
        text = "Page #%s" % page_num
        pw.drawRightString(20*cm, 2*cm, text)
        pw.showPage()
        pw.drawString(0.25 * inch, 11.225 * inch, "| Bloco      |    Ap    |     Vaga    |")
    pw.drawString(0.25 * inch, y, line)
    aux += 1
    y = y - dy
pw.save() 

'''
with open(sys.argv[1],'wb') as file:
    for key, lists in l:
        torre = torres[key[0]]
        for item in lists:
            row = torre + "," + str(key) + "," + str(item)
            file.write(bytes(row, 'utf-8'))
            file.write(bytes('\n', 'utf-8'))
file.close()

soma = 0
for valida in dict_sorteio:
    for vaga in dict_sorteio[valida]:
        soma += vaga

print(soma)    
print(dict_sorteio)
print(bloq)
print(nbloq)
'''
