'''
modulo python: LAUtils

titulo:
    Analisador Semantico para a Linguagem Algoritmica(LA)
    TRABALHO 3 - COMPILADORES 1

autores:
    Luan V. Moraes da Silva - 744342
    Guilherme Servidoni - 727339
    Alisson Roberto Gomes - 725721
'''

from pprint import pprint, pformat
from collections import deque

# 
# Tabela de símbolos
#
#
class TabelaSimbolos:

    tabela = {}

    def __init__(self, tabela=None):
        if tabela == None:
            self.tabela = {}
        else:
            self.tabela = tabela

    # inserir
    # params: nome, token, categoria, tipo e kwargs
    # return: produz como retorno a entrada adicionada
    def inserir(self, nome, token, categoria, tipo, **kwargs):
        if nome == None:
            return None

        entrada = {'nome': nome,
                   'token': token,
                   'categoria': categoria,
                   'tipo': tipo, **kwargs
                   }

        self.tabela[nome] = entrada
        return entrada

    # join
    # params: tabelas de simbolo t1, t2
    # return: uniao entre duas tabelas de simbolos
    def join(self, t1, t2):
        return TabelaSimbolos(tabela={**(t1.tabela), **(t2.tabela)})

    def verificar(self, nome):
        return self.tabela.get(nome, None)

    def __str__(self):
        return pformat(self.tabela)

    def reiniciar(self):
        self.tabela = {}

    def __repr__(self):
        return pformat(self.tabela, indent=2, width=120, depth=4)


# 
# Escopos
#
#
class Escopos:
    escopos = deque()

    def criarEscopo(self, copia=None):
 
        if(isinstance(copia, TabelaSimbolos) and copia != None):
            self.escopos.appendleft(copia)
            return

        self.escopos.appendleft(TabelaSimbolos())

    def getAtualEscopo(self):
        if(len(self.escopos) == 0):
            return None

        return self.escopos[0]

    def runEscoposAninhados(self):
        return self.escopos

    # verificarNosEscopos
    # params: token_text, subtable
    # sreturn: None caso a busca nao retorne o resultado esperado
    def verificarNosEscopos(self, token_text, subtable = False):
        if subtable:
            for escopo in self.runEscoposAninhados():
                valor = escopo.verificar(exp[0])
                exp = token_text.split('.')
                
                if valor != None:
                    sub_tabela = valor['subtabela']
                    valor2 = sub_tabela.verificar(exp[1])

                    if('subtabela' not in valor or valor['categoria'] in ['proc', 'func']):
                        return None

                    if(valor2 != None):
                        return valor2

        else:
            for escopo in self.runEscoposAninhados():
                valor = escopo.verificar(token_text)

                if(valor != None):
                    return valor

        return None

    def abandonarEscopo(self):
        self.escopos.popleft()


    def clearEscopos(self):
        self.escopos = deque()
