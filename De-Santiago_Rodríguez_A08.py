from tkinter import *
from tkinter import filedialog
import os
import heapq
import matplotlib.pyplot as plt
import networkx as nx

#Aquí comienza el backend
class Nodo:
    def __init__(self, caracter, frecuencia):
        self.caracter = caracter
        self.frecuencia = frecuencia
        self.izquierda = None
        self.derecha = None
    def __lt__(self, otro):
        return self.frecuencia < otro.frecuencia


def contruir_arbol(contador_letras):
    heap = [Nodo(caracter, frecuencia) for caracter, frecuencia in contador_letras.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        izquierda = heapq.heappop(heap)
        derecha = heapq.heappop(heap)
        padre = Nodo(None, izquierda.frecuencia + derecha.frecuencia)
        padre.izquierda = izquierda
        padre.derecha = derecha
        heapq.heappush(heap, padre)
    return heap[0]

def asignar_codigos(arbol, prefijo='', codigos={}):
    if arbol.caracter is not None:
        codigos[arbol.caracter] = prefijo
    else:
        asignar_codigos(arbol.izquierda, prefijo + '0', codigos)
        asignar_codigos(arbol.derecha, prefijo + '1', codigos)
    return codigos

def comprimir_A(original_filename, codigos):
    comprimidos_filname = os.path.splitext(original_filename)[0] + 'comprimido.bin'
    with open(original_filename, 'r', encoding='utf-8') as original, open(comprimidos_filname, 'wb') as comprimidos:
        contenido = original.read()
        bits = ''.join(codigos[caracter] for caracter in contenido)
        padding = 8 - len(bits) % 8
        bits += padding * '0'
        for i in range(0, len(bits), 8):
            byte = bits[i:i + 8]
            comprimidos.write(bytes([int(byte, 2)]))
        comprimidos.write(bytes([padding]))
    return comprimidos_filname

def descomprimir_A(comprimidos_filename, arbol):
    descomprimidos_filename = os.path.splitext(comprimidos_filename)[0] + 'descomprimido.txt'
    with open(comprimidos_filename, 'rb') as comprimido, open(descomprimidos_filename, 'wb') as descomprimidos:
        bits = ''
        while True:
            byte = comprimido.read(1)
            if not byte:
                break
            bits += f'{byte[0]:08b}'
        padding_bits = bits[-8:]
        padding = int(padding_bits, 2)
        bits = bits[:-8]
        nodo_actual = arbol
        for bit in bits:
            if bit == '0':
                nodo_actual = nodo_actual.izquierda
            else:
                nodo_actual = nodo_actual.derecha
            if nodo_actual.caracter is not None:
                descomprimidos.write(nodo_actual.caracter.encode('utf-8'))
                nodo_actual = arbol
    return descomprimidos_filename

def comprimir():
    global contador_letras, filename
    arbol_huffman = contruir_arbol(contador_letras)
    codigos_huffman = asignar_codigos(arbol_huffman)
    comprimidos_filename = comprimir_A(filename, codigos_huffman)
    print(f"Archivo comprimido: {comprimidos_filename}")

def descomprimir():
    filetype = [('Archivos Binario', '*.bin')]
    comprimidos_filename = filedialog.askopenfilename(filetypes=filetype)
    if comprimidos_filename:
        arbol_huffman = contruir_arbol(contador_letras)
        descomprimidos_filename = descomprimir_A(comprimidos_filename, arbol_huffman)
        print(f"Archivo descomprimido: {descomprimidos_filename}")

#Aqui comienza el frontend
def leer():
    global filename
    filetypes = [('Archivos TXT', '*.txt')]
    filename = filedialog.askopenfilename(filetypes=filetypes)
    if filename:
        try:
            #ESTO ESPECIFICA QUE EL R, ES SOLO PARA LEER LOS DATOS DEL ARCHVIO SIN MODIFICARLO, Y EL UTF-8 ES PARA QUE PUEDA LEER UNA GRAN VARIEDAD DE CARACTERES
            #LO ESPECIFIQUE PORQUE NO ME DEJABA LEER EL ARCHIVO DEL PROFE
            with open(filename, 'r', encoding='utf-8') as file:
                contenido = file.read()
                conteo(contenido)
                #ESTO SE PONE POR SI HAY ALGUN ERROR EN LA CODIFICACIÓN DE LA CANTIDAD DE LETRAS REPETIDS
        except UnicodeDecodeError as e:
            print(f"Error al decodificar el archivo: {e}")

#CREO QUE UNA VARIABLE GLOBAL DONDE GUARDO EN UN DICCIOANRIO LOS DATOS DE REPETICONES DEL ARCHVIO TXT
#ESTO LO HICE PARA QUE SEA MÁS FACIL UTILIZAR ESTA VARIABLE EN FUNCIONES PARA MANIPULAR
contador_letras = {}


def conteo(letras):
    global contador_letras#AQUI MARCO LA VARIABLE COMO GLOBAL, ESTO SIGNIFICA QUE SI MODIFICAS LOS VALORES
    #EN ESTA FUNCIÓN, Y LA TIENES O LA LLAMAS EN OTRA FUNCIÓN, ESTA SERÁ EXACTAMENTE LA MISMA
    #AHOAR BIEN, EN LA LINEA DE ABAJO HACE ALGO CURIOSO, DETECTA LA LETRA Y EN EL ARCHIVO, SI ESTA EN EL DICIIONARIO, LE SUMA UNO
    #Si no se encuentra, este se guarda como nuevo valor
    for letra in letras:
        if letra in contador_letras:
            contador_letras[letra] += 1
        else:
            contador_letras[letra] = 1
    #Esto sirve para ordenar el diccionario de mayor a menor
    contador_letras = {k: v for k, v in sorted(contador_letras.items(), key=lambda item: item[1], reverse=True)}

    print(contador_letras)
    #Aquí solo va insertra en el cuadro de texto, los valores que almacenó el diccioanrio
    CuadroTexto.insert(END,"El resumen de las letras son:\n")
    for clave,valor in contador_letras.items():
        CuadroTexto.insert(END,  f"{clave}: {valor}\n")

Raiz = Tk()
Raiz.title('Actividad 07')
Raiz.config(width=700, height=600)

MFrame = Frame(Raiz)
MFrame.config(width=500, height=200, bg="#757575")
MFrame.pack()

BotonLeer=Button(MFrame, text="Examinar",command=leer,bg="#0B656C",fg="#FFFFFF")
BotonLeer.place(x=10,y=75, width=115,height=25)

CuadroTexto=Text(MFrame)
CuadroTexto.place(x=130,y=45,width=350,height=145)

BotonComprimir = Button(MFrame, text="Comprimir", command=comprimir, bg="#0B476C", fg="#FFFFFF")
BotonComprimir.place(x=10, y=105, width=115, height=25)

BotonDescomprimir = Button(MFrame, text="Descomprimir", command=descomprimir, bg="#0B476C", fg="#FFFFFF")
BotonDescomprimir.place(x=10, y=135, width=115, height=25)

Raiz.mainloop()