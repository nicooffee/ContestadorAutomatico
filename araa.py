# coding=utf-8
"""
/*---------------------------------Trabajo de laboratorio 1: Contestador Automático----------------------------------**/
/***********************************************************************************************************************
#    Autores   : NICOLAS IGNACIO HONORATO DROGUETT.
#    Programa  : Algoritmo de Respuesta Automática Adaptativo.
#	 Proposito : Crear un diálogo en base a afirmaciones y preguntas escritas en un archivo de texto.
#    Version   : Python 3.5.2
#    Fecha     : Santiago de Chile, 11 de Mayo de 2018.
***********************************************************************************************************************/
"""

import os
import sys
from builtins import len, open, list, filter
from collections.__init__ import OrderedDict
# -----------------------------------------------------------------
# procesarAfirmación:
#
# Función que procesa una afirmación enviada por
# parámetro. Si la afirmación posee un + al inicio,
# se descompone convenientemente para luego
# agregarla al diccionario. En caso contrario, se
# busca la afirmacion para eliminarla del diccionario.
#
def procesarAfirmacion(line, dicAfirmacion, historial):
    af = line.split(' ', 3) if ("don't" in line or "doesn't" in line) else line.split(' ', 2)
    signo = af[0][0]
    af[0] = af[0].lstrip('+-')
    af[-1] = af[-1].rstrip('.')
    if "don't" in af or "doesn't" in af:
        af.append(af[1])
        af.pop(1)
    subject = af[0]
    predicate = af[1].rstrip('s') if (af[0] != "I" or af[0] != "you") else af[1]
    obj = af[-2] if (af[-1] == "don't" or af[-1] == "doesn't") else af[-1]
    if len(af) == 2 or (len(af) == 3 and (af[-1] == "don't" or af[-1] == "doesn't")):
        obj = None
    neg = af[-1] if (af[-1] == "don't" or af[-1] == "doesn't") else None
    if af[0] == "nobody":
        neg = "don't"
    if signo == '+':
        if dicAfirmacion.get(subject) is None:
            dicPredicate = OrderedDict({predicate: [(obj, neg)]})
            dicAfirmacion[subject] = dicPredicate
        elif dicAfirmacion[subject].get(predicate) is None:
            dicAfirmacion[subject][predicate] = [(obj, neg)]
        else:
            dicAfirmacion[subject][predicate].append((obj, neg))
        historial.append((subject, predicate, obj, neg))
    else: #signo == '-'
        lista = dicAfirmacion[subject][predicate]
        lista.remove((obj, neg))
        if dicAfirmacion[subject][predicate] == []:
            dicAfirmacion[subject].pop(predicate)
        if dicAfirmacion[subject] == {}:
            dicAfirmacion.pop(subject)
        historial.remove((subject, predicate, obj, neg))





# ---------------------------------------------------------------
# responderPregunta:
#
# Función que recibe una pregunta e identifica qué
# tipo de pregunta es. Luego, genera la respuesta
# basándonse en los datos almacenados en el diccionario y
# la almacena en el archivo de salida.
#
def responderPregunta(preg, dicAfirmacion, out, historial):
    out.write(preg+"\n")
    pregStr=preg.lower()
    preg = preg.rstrip('?')
    if "who" in pregStr:    # who_predicates[_object]?
        preg = preg.split(' ', 2)
        preg[1] = preg[1].rstrip('s')
        if len(preg) == 2:
            preg.append(None)
        respuesta = crearRespuestaWho(dicAfirmacion, preg[1], preg[2])
    elif "what" in pregStr:  # what_(do|does)_subject_do?
        preg = preg.split(' ')
        respuesta = crearRespuestaWhat(preg[2].lower(), historial)
    else:                   # (do|does)_subject_predicate[_object]?
        preg = preg.split(' ', 3)
        respuesta = crearRespuestaDoDoes(preg[1].lower(), preg[2], preg[-1], dicAfirmacion)
    out.write(respuesta+"\n")





# ---------------------------------------------------------------
# crearRespuestaDoDoes:
#
# Función que genera la repuesta para una pregunta de
# tipo do/does utilizando los datos del diccionario.
#
# Primero verifica si existe el predicate/object en los
# sujetos nobody y everybody. En el caso de que no exista
# en estos sujetos, se busca la acción en el diccionario
# del mismo sujeto.
#
def crearRespuestaDoDoes(subject, predicate, obj, dicAfirmacion):
    subjectAux = subject
    negado = "doesn't"
    if subject == "i":
        subjectAux = "you"
        negado = "don't"
    elif subject == "you":
        subjectAux = "i"
        negado = "don't"
    if obj == predicate:
        obj = None
    if subject!="everybody" and subject!="nobody" and subject!="i" and subject!="you":
        subjectAux=subjectAux.capitalize()
    if "everybody" in dicAfirmacion:
        if predicate in dicAfirmacion["everybody"] and existeObjectEnLista(dicAfirmacion["everybody"][predicate], obj) != -1:
            string = "yes, " + subjectAux + " "
            string = string + predicate + 's ' if (subject != "I" and subject != "you") else string + predicate + ' '
            string = string.rstrip() + " " + obj if (obj is not None) else string.rstrip()
            return string + ".\n"
    if "nobody" in dicAfirmacion:
        if predicate in dicAfirmacion["nobody"] and existeObjectEnLista(dicAfirmacion["nobody"][predicate], obj) != -1:
            string = "no, " + subjectAux + " "
            string = string + "doesn't " + predicate + ' ' if (
                        subject != "i" and subject != "you") else string + "don't " + predicate + ' '
            string = string.rstrip() + " " + obj if (obj is not None) else string.rstrip()
            return string + ".\n"
    if subject in dicAfirmacion:
        if predicate in dicAfirmacion[subject]:
            if((obj,None) in dicAfirmacion[subject][predicate] or (obj,negado) in dicAfirmacion[subject][predicate]):
                tupla = dicAfirmacion[subject][predicate][existeObjectEnLista(dicAfirmacion[subject][predicate], obj)]
                string = "yes, " + subjectAux + " " + predicate if tupla[1] is None else "no, " + subjectAux + " " + negado + " " + predicate
                string = string + "s " if tupla[1] is None and (subject != "i" and subject != "you") else string + " "
                string = string + tupla[0] if tupla[0] is not None else string.rstrip()
                return string + ".\n"
            else:
                return "maybe.\n"
        else:
            return "maybe.\n"
    else:
        return "maybe.\n"





# ---------------------------------------------------------------
# crearRespuestaWhat:
#
# Función que genera la respuesta para una pregunta
# de tipo what utilizando los datos almacenados en el diccionario.
#
# En esta funcion se requiere un uso de una estructura adicional llamada
# historial, debido a que se deben imprimir los verbos de forma
# cronológica.
#
def crearRespuestaWhat(subject, historial):
    histAux = list(filter(lambda x: x[0] == subject or x[0] == "everybody" or x[0] == "nobody", historial))
    conectivo = "don't" if (subject == "i" or subject == "you") else "doesn't"
    impresos = []
    if histAux==[]:
        return "I don't know.\n"
    s = 's' if conectivo == "doesn't" else ""
    if subject.lower() == "i":
        subject = "you"
    elif subject.lower() == "you":
        subject = "I"
    string = subject + " "
    for i in histAux:
        if (i[1], i[2], i[3]) not in impresos:
            impresos.append((i[1],i[2],i[3]))
            string = string + conectivo + " " if i[3] is not None else string
            if i == histAux[-1] and len(histAux)>1:
                string = string + "and"
            string = string + i[1] + s + " " if i[3] is None else string + i[1] + " "
            string = string + i[2] + ", " if i[2] is not None else string.rstrip() + ", "
    string = string.rstrip(' ,')
    string = string.replace(", and", " and ")
    return string + ".\n"





# ---------------------------------------------------------------
# crearRespuestaWho:
#
# Función que genera la respuesta para una pregunta
# de tipo who.
#
# Genera una lista de sujetos que posean el
# predicate/object enviado por parámetro. Luego,
# crea la respuesta con la lista de sujetos.
def crearRespuestaWho(dicAfirmacion, predicate, obj):
    lista=[k for k in dicAfirmacion if  dicAfirmacion[k].get(predicate) is not None and (obj, None) in dicAfirmacion[k][predicate]]
    string = ""
    if lista == []:
        return "I don't know.\n"
    elif "everybody" in lista:
        string = string + "everybody " + predicate + "s"
    elif "nobody" in lista:
        string = string + "nobody " + predicate + "s"
    else:
        for s in lista:
            if s != lista[-1]:
                string = string + (s.capitalize() + ", ") if s!="i" and s!="you" else string + (s + ", ")
            else:
                string = string+("and "+s.capitalize()+" "+predicate+"s") if s!="i" and s!="you" else string+("and "+s+" "+predicate+"s")
    if obj is not None:
        string = string + " " + obj
    string = string.lstrip("and ")
    string = string.replace(", and", " and")
    return string + ".\n"





# ---------------------------------------------------------------
# procesarDialogos:
#
# Función que llama a la función procesarDialogo
# cada vez que se lee una cadena numérica en el archivo
# enviado por parámetro.
#
def procesarDialogos(inp, out):
    line = inp.readline().rstrip()
    while line.isnumeric():
        out.write("Dialogue #" + line + ":\n")
        procesarDialogo(inp, out)
        line = inp.readline().rstrip()





# ---------------------------------------------------------------
#procesarDialogo:
#
# Función que recibe un archivo y procesa un diálogo desde
# la linea siguiente a la última leída hasta encontrar una
# linea que posea el caracter '!'.
#
# Es la que llama a las funciones procesarAfirmacion y
# responderPregunta. Además, escribe el resultado del
# diálogo en el archivo de salida.
def procesarDialogo(inp, out):
    historial = []
    dicAfirmacion = OrderedDict({})
    dicContradiccion = OrderedDict({"si":{},"no":{},"cont":0})
    line = inp.readline().rstrip()
    while '!' not in line:
        if not (line[0].isalnum()):
            existeContradiccion(dicContradiccion, line)
            procesarAfirmacion(line.lower(), dicAfirmacion, historial)
        elif line[-1] == '?':
            if dicContradiccion["cont"]!=0:
                out.write(line + "\n")
                out.write("I am abroad.\n\n")
            else:
                responderPregunta(line, dicAfirmacion, out, historial)
        line = inp.readline().rstrip()
        if '!' in line:
            out.write(line + "\n\n")





# ---------------------------------------------------------------
# existeContradiccion:
#
# Función que comprueba si existe una contradicción de
# afirmaciones dentro del diccionario.
#
# Comprueba si la afirmacion aumenta el número de contradicciones
# en caso de ser agregada o lo decrementa en caso de ser eliminada.
#
# Que el valor de la llave cont sea 0 significa que no existen
# contradicciones dentro del diccionario.
def existeContradiccion(dicContradiccion,af):
    #dicContradicciones={"si":{sujeto:[(pred1,obj1),(pred2,obj2)]},"no":{},"cont"=0}
    af=af.rstrip('.')
    # aflist= [suj,pred,obj]
    aflist= af.split(' ', 3) if ("don't" in af or "doesn't" in af) else af.split(' ', 2)
    signo = af[0][0]
    llaveDic="si"
    if "don't" in af or "doesn't" in af:
        llaveDic="no"
        aflist.pop(1)
        if len(aflist)==2:
            aflist.append(None)
    elif len(aflist)==2:
        aflist.append(None)
    aflist[0]=aflist[0].lstrip('+-')
    aflist[1]=aflist[1].rstrip('s')
    if aflist[0]=="nobody":
        aflist[0]="everybody"
        llaveDic="no"
    procesarContradiccion(dicContradiccion, llaveDic, signo, aflist)
    llaveDicNeg = "si" if llaveDic=="no" else "no"
    signoNum=1 if signo=='+' else -1
    if aflist[0]!="everybody":
        for suj in (aflist[0],"everybody"):
            if dicContradiccion[llaveDicNeg].get(suj) is not None:
                if (aflist[1], aflist[2]) in dicContradiccion[llaveDicNeg][suj]:
                    dicContradiccion["cont"] += signoNum
    else:
        for suj in dicContradiccion[llaveDicNeg]:
            if (aflist[1], aflist[2]) in dicContradiccion[llaveDicNeg][suj]:
                dicContradiccion["cont"] += signoNum





# procesarContradiccion:
#
# Función que agrega o elimina una afirmación dentro del diccionario
# de contradicciones. Dependerá del signo si es eliminada o agregada.
#
# En este diccionario, las afirmaciones con sujeto nobody son
# transformadas a afirmaciones con sujeto everybody, pero negadas.
def procesarContradiccion(dicContradiccion,llaveDic,signo,aflist):
    if signo=='+':
        if aflist[0] in dicContradiccion[llaveDic]:
            dicContradiccion[llaveDic][aflist[0]].append((aflist[1], aflist[2]))
        else:
            dicContradiccion[llaveDic][aflist[0]] = [(aflist[1], aflist[2])]
    else:
        dicContradiccion[llaveDic][aflist[0]].remove((aflist[1],aflist[2]))
        if dicContradiccion[llaveDic][aflist[0]]==[]:
            dicContradiccion[llaveDic].pop(aflist[0])





# ---------------------------------------------------------------
# existeObjectEnLista:
#
# Funcion que comprueba si una lista de objetos de una clave
# subject/predicate contiene alguna tupla con el objeto enviado.
#
def existeObjectEnLista(lista, obj):
    for items in lista:
        if items[0] == obj:
            return lista.index(items)
    return -1





# ---------------------------------------------------------------
# ---------------------------------------------------------------
# Instrucciones principales del programa.
#
# Se abren los archivos correspondientes dependiendo de si
# se envían los nombres de los archivos al momento de ejecutar
# el programa.
#
# Luego, se llama a la función procesarDialogos para
# generar el archivo de salida.
os.system('clear')
inputPath,outputPath = ("in.txt","out.txt") if len(sys.argv)==1 else (sys.argv[-2]+".txt",sys.argv[-1]+".txt")
inp,out = open(inputPath, "r"),open(outputPath, "w")
procesarDialogos(inp, out)
inp.close()
out.close()
# ---------------------------------------------------------------
# ---------------------------------------------------------------
