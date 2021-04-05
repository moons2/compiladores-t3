'''
modulo python: LACGenerator

titulo:
    Analisador Semantico para a Linguagem Algoritmica(LA)
    TRABALHO 3 - COMPILADORES 1

autores:
    Luan V. Moraes da Silva - 744342
    Guilherme Servidoni - 727339
    Alisson Roberto Gomes - 725721
'''

from LAVisitor import LAVisitor

# definicao de constantes que serao uteis ao longo de todo codigo
STRING_LENGTH = '[144]'
TIPOS_BASICOS = ['literal', 'inteiro', 'real', 'logico']

class LATranslatorUtils():

    # traduzirTipo
    # params:
    # return:
    def traduzirTipo(self, tipo, placeholder=False):

        pointer = ""
        if(tipo[0] == "^"):
            tipo = tipo[1::]
            pointer = "*"

        #
        # Como nao existe swith em python :( entao temos que partir
        # para a abordagem menos permormatica
        if(tipo in TIPOS_BASICOS):
            if(tipo == "literal"):
                return ("char" if not placeholder else "%s") + pointer
            elif(tipo == "real"):
                return ("float" if not placeholder else "%f") + pointer
            elif(tipo == "inteiro"):
                return ("int" if not placeholder else "%d") + pointer
            elif(tipo == "logico"):
                return ("bool" if not placeholder else "%d") + pointer

        return tipo

    # traduzirIDENT
    # params: ctx (contexto de tokens), tipo (argumento), argumento, declaracao()
    # return: 
    def traduzirIDENT(self, ctx, tipo=None, argumento=False, declaracao=False):
        if(not isinstance(ctx, list)):
            ctx = [ctx]

        nome = ctx[0].getText() + '.' + \
            ctx[1].getText() if len(ctx) > 1 else ctx[0].getText()

        if(declaracao and tipo == "char"):
            nome += STRING_LENGTH
        elif(argumento and tipo == "char"):
            nome += "[]"

        return nome


class LACGenerator(LAVisitor):
    saida = []
    utils = LATranslatorUtils()

    def __init__(self, escopos, utils):

        self.escopos = escopos
        self.interpreterUtils = utils

    def visitPrograma(self, ctx):
        self.saida.append("#include <stdio.h>")
        self.saida.append("#include <stdlib.h>")
        self.saida.append("#include <stdbool.h>")
        self.saida.append("#include <string.h>")

        self.visitDeclaracoes(ctx.declaracoes())

        self.saida.append("int main(){")
        self.visitCorpo(ctx.corpo())
        self.saida.append("\treturn 0;")
        self.saida.append("}")

    def visitDeclaracao_local(self, ctx):
        start = ctx.start.text

        if(start == 'declare'):
            self.visitVariavel(ctx.variavel())
        elif(start == 'constante'):
            aux = ctx.IDENT().getText()
            tipo = self.utils.traduzirTipo(ctx.tipo_basico().getText())
            valor = ctx.valor_constante().getText()

            self.saida.append(f"const {tipo} {aux} = {valor};")

        elif(start == 'tipo'):

            if(ctx.tipo().registro() != None):
                tipo = self.visitRegistro(ctx.tipo().registro())
            else:
                tipo = self.utils.traduzirTipo(ctx.tipo().getText())

            aux = self.utils.traduzirIDENT(
                ctx.IDENT(), tipo=tipo, declaracao=True)

            self.saida.append(f"typedef {tipo} {aux};")

    def visitDeclaracao_global(self, ctx):
        start = ctx.start.text

        if(ctx.parametros() != None):
            parametros = self.visitParametros(ctx.parametros())

        nome = ctx.IDENT().getText()

        if(start == 'procedimento'):
            self.saida.append(f"void {nome}({parametros})"+"{")
        else:
            retorno = self.utils.traduzirTipo(ctx.tipo_estendido().getText())
            self.saida.append(f"{retorno} {nome} ({parametros})"+"{")

        sub_rotina = self.escopos.verificarNosEscopos(nome)

        for declaracao in ctx.declaracao_local():
            self.visitDeclaracao_local(declaracao)

        self.escopos.criarEscopo(sub_rotina["subtabela"].join(
            sub_rotina["parametros"], sub_rotina["subtabela"]))

        for cmd in ctx.cmd():
            self.visitCmd(cmd)

        self.escopos.abandonarEscopo()

        self.saida.append("}")

    def visitVariavel(self, ctx):
        declaracao = []

        if(ctx.tipo().registro() != None):
            tipoTraduzido = self.visitRegistro(ctx.tipo().registro())
        else:
            tipoTraduzido = self.utils.traduzirTipo(ctx.tipo().getText())

        for ident in ctx.identificador():
            declaracao.append(self.visitIdentificador(
                ident, tipoTraduzido, declaracao=True))

        declaracao = f"{tipoTraduzido} {', '.join(declaracao)};"

        self.saida.append(declaracao)

    def visitRegistro(self, ctx):
        declaracoes = []

        for aux in ctx.variavel():
            self.visitVariavel(aux)
            declaracoes.append(self.saida.pop())

        declaracoes_local = ' '.join(declaracoes)

        return f"struct {{ {declaracoes_local} }}"


    def visitParametro(self, ctx):

        tipo = self.utils.traduzirTipo(ctx.tipo_estendido().getText())
        args = []

        for ident in ctx.identificador():
            args.append(
                f"{tipo} {self.visitIdentificador(ident, tipo=tipo, argumento=True)}")
        return ', '.join(args)

    def visitParametros(self, ctx):
        parametros = []

        for param in ctx.parametro():
            parametros.append(self.visitParametro(param))

        return ', '.join(parametros)


    def visitIdentificador(self, ctx, tipo=None, argumento=False, declaracao=False):
        nome = self.utils.traduzirIDENT(ctx.IDENT(
        ), tipo=tipo, argumento=argumento, declaracao=declaracao)

        if(ctx.dimensao() != None):
            return f"{nome}{ctx.dimensao().getText()}"

        return nome

    def visitExpressao(self, ctx):
        termos = []

        for termo in ctx.termo_logico():
            termos.append(self.visitTermo_logico(termo))
        return ' || '.join(termos)

    def visitTermo_logico(self, ctx):
        fatores = []

        for fator in ctx.fator_logico():
            fatores.append(self.visitFator_logico(fator))

        return ' && '.join(fatores)

    def visitFator_logico(self, ctx):
        if(ctx.start.text == 'nao'):
            return "!" + self.visitParcela_logica(ctx.parcela_logica())
        return self.visitParcela_logica(ctx.parcela_logica())

    def visitParcela_logica(self, ctx):
        if(ctx.exp_relacional() is None):
            return ctx.getText()
        return self.visitExp_relacional(ctx.exp_relacional())

    def visitParcela(self, ctx):
        return (ctx.op_unario().getText() if ctx.op_unario() != None else "") + self.visitChildren(ctx)

    def visitExp_relacional(self, ctx):
        op = ctx.op_relacional()
        final = []
        expressoes = ctx.exp_aritmetica()

        if(op != None):
            operador = op.getText() if op.getText() != '=' else "=="

            for exp in expressoes:
                final.append(self.visitExp_aritmetica(exp))
            return operador.join(final)

        return self.visitChildren(ctx)

    def visitExp_aritmetica(self, ctx):
        final = ""
        op = ctx.op1()
        termos = ctx.termo()

        if(len(op) == 0):
            return self.visitTermo(termos[0])

        final += termos[0].getText()
        for i in range(len(op)):
            final += f"{ op[i].getText() }{self.visitTermo(termos[i+1])}"

        return final

    def visitTermo(self, ctx):
        final = ""
        op = ctx.op2()
        fatores = ctx.fator()

        if(len(op) == 0):
            return self.visitFator(fatores[0])

        final += fatores[0].getText()
        for i in range(len(op)):
            final += f"{op[i].getText()}{self.visitFator(fatores[i+1])}"

        return final

    def visitFator(self, ctx):
        final = []
        op = ctx.op3()

        if(len(op) == 0):
            return self.visitParcela(ctx.parcela()[0])

        for parcela in ctx.parcela():
            final.append(self.visitParcela(parcela))

        return '%'.join(final)


    def visitParcela_unario(self, ctx):
        if(ctx.NUM_INT() != None or ctx.NUM_REAL() != None):
            return ctx.getText()
        elif(ctx.cmdChamada() != None):
            return self.visitCmdChamada(ctx.cmdChamada(), in_expressao=True)
        elif(ctx.identificador() != None):
            return ("*" if ctx.valor != None else "") + self.visitIdentificador(ctx.identificador())

        return "(" + self.visitExpressao(ctx.expressao()) + ")"

    def visitParcela_nao_unario(self, ctx):
        if(ctx.CADEIA()):
            return ctx.getText()

        return ("&" if ctx.endereco != None else "") + self.visitIdentificador(ctx.identificador())

    def visitItem_selecao(self, ctx):
        self.visitConstantes(ctx.constantes())

        for cmd in ctx.cmd():
            self.visitCmd(cmd)

        self.saida.append("break;")

    def visitConstantes(self, ctx):
        for intervalo in ctx.numero_intervalo():
            extremidades = self.visitNumero_intervalo(
                intervalo)

            if(len(extremidades) > 1):
                for num in range(int(extremidades[0]), int(extremidades[1])):
                    self.saida.append(f"case {num}:")

                self.saida.append(f"case {extremidades[1]}:")
            else:
                self.saida.append(f"case {extremidades[0]}:")

    def visitNumero_intervalo(self, ctx):
        return ctx.getText().split('..')

    def visitCmdEscreva(self, ctx):
        tipos = []
        expressoes = []

        for exp in ctx.expressao():
            tipos.append(self.utils.traduzirTipo(
                self.interpreterUtils.obterTipo(self.escopos, exp), placeholder=True))
            expressoes.append(self.visitExpressao(exp))

        final = "\"" + ''.join(tipos) + "\", " + ', '.join(expressoes)

        self.saida.append(f"printf({final});")

    def visitCmdLeia(self, ctx):
        tipos = []
        identificadores = []

        for ident in ctx.identificador():
            tipos.append(self.utils.traduzirTipo(
                self.interpreterUtils.obterTipo(self.escopos, ident), placeholder=True))
            identificadores.append(
                # o indice -1 eh a forma pythonica de selecionar o ultimo elemento
                ("&" if tipos[-1] != "%s" else "") + self.visitIdentificador(ident))

        final = "\"" + ' '.join(tipos) + "\"" + ', ' + \
            ','.join(identificadores)

        self.saida.append(f"scanf({final});")

    def visitCmdSe(self, ctx):
        self.saida.append(f"if ({self.visitExpressao(ctx.expressao())})"+"{")

        if(len(ctx.se)):
            for cmd in ctx.se:
                self.visitCmd(cmd)

        self.saida.append("}")

        if(len(ctx.senao)):
            self.saida.append("else {")

            for cmd in ctx.senao:
                self.visitCmd(cmd)

            self.saida.append("}")

    def visitCmdCaso(self, ctx):
        self.saida.append(f"switch ({ctx.exp_aritmetica().getText()})"+"{")

        self.visitSelecao(ctx.selecao())

        if(ctx.cmd() != None):
            self.saida.append("default:")

            for cmd in ctx.cmd():
                self.visitCmd(cmd)

            self.saida.append("break;")

        self.saida.append("}")

    def visitCmdPara(self, ctx):
        expressoes = ctx.exp_aritmetica()
        aux = ctx.IDENT().getText()

        self.saida.append(
            f"for (int {aux} = {expressoes[0].getText()}; {aux} <= {expressoes[1].getText()}; {aux}++)" + "{")

        for cmd in ctx.cmd():
            self.visitCmd(cmd)

        self.saida.append("}")

    def visitCmdAtribuicao(self, ctx):
        ident = self.visitIdentificador(ctx.identificador())
        expressao = self.visitExpressao(ctx.expressao())

        if(ctx.start.text == '^'):
            ident = '*' + ident

        if(self.interpreterUtils.obterTipo(self.escopos, ctx.identificador()) == 'literal'):
            self.saida.append(f"strcpy({ident}, {expressao});")
            return

        self.saida.append(f"{ident} = {expressao};")

    def visitCmdChamada(self, ctx, in_expressao=False):
        ident = self.utils.traduzirIDENT(ctx.IDENT())
        final = []

        for exp in ctx.expressao():
            final.append(self.visitExpressao(exp))

        final = f"{ident}({', '.join(final)})"

        if in_expressao:
            return final
        else:
            self.saida.append(f"{final};")

    def visitCmdRetorne(self, ctx):
        exp = self.visitExpressao(ctx.expressao())

        self.saida.append(f"return {exp};")

    def visitCmdEnquanto(self, ctx):
        self.saida.append(f"while ({self.visitExpressao(ctx.expressao())})"+"{")

        for cmd in ctx.cmd():
            self.visitCmd(cmd)

        self.saida.append("}")

    def visitCmdFaca(self, ctx):
        self.saida.append("do {")

        for cmd in ctx.cmd():
            self.visitCmd(cmd)

        self.saida.append(
            "}" + f" while ({self.visitExpressao(ctx.expressao())});")
