'''
modulo python: LAInterpreter

titulo:
    Analisador Semantico para a Linguagem Algoritmica(LA)
    TRABALHO 3 - COMPILADORES 1

autores:
    Luan V. Moraes da Silva - 744342
    Guilherme Servidoni - 727339
    Alisson Roberto Gomes - 725721
'''

from LASemantico import SemanticoUtils
from LAVisitor import LAVisitor
from LAUtils import Escopos


#
# LAInterpreter
# params: LAVisitor
# return: class nao produz retorno
class LAInterpreter(LAVisitor):
    escopos = Escopos()
    utils = SemanticoUtils()

    def visitPrograma(self, ctx):
        self.escopos.clearEscopos()
        self.escopos.criarEscopo()
        self.visitDeclaracoes(ctx.declaracoes())
        self.visitCorpo(ctx.corpo())

    # visitDeclaracoes
    # params: ctx
    # return: funcao original visitara cada declaracao
    def visitDeclaracoes(self, ctx):
        for declaracao in ctx.decl_local_global():
            self.visitDecl_local_global(declaracao)

    def visitDeclaracao_global(self, ctx):
        self.utils.verificar(self.escopos, ctx)

    def visitDeclaracao_local(self, ctx):
        self.utils.verificar(self.escopos, ctx)

    # visitCorpo
    # params: ctx
    # return: uma lista com o ou mais declaracoes e comandos
    def visitCorpo(self, ctx):
        for decs in ctx.declaracao_local():
            self.utils.verificar(self.escopos, decs)

        for cmd in ctx.cmd():
            if(cmd.cmdRetorne() != None):
                self.utils.erroRetorne(cmd.start)

            self.utils.verificar(self.escopos, cmd)
