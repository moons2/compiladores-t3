'''
modulo python: LASemantico

titulo:
    Analisador Semantico para a Linguagem Algoritmica(LA)
    TRABALHO 3 - COMPILADORES 1

autores:
    Luan V. Moraes da Silva - 744342
    Guilherme Servidoni - 727339
    Alisson Roberto Gomes - 725721
'''


from LAParser import LAParser
from LAUtils import TabelaSimbolos, Escopos
import string
import random


class SemanticoUtils:

    errosSemanticos = []

    ATRIBUICAO = None

    TIPOS = ['literal', 'inteiro', 'real', 'logico']

    NUMERO = ['inteiro', 'real']

    OP_ARIT = ['+', '-', '*', '/', '%']

    OP_RELACIONAL = ['=', '<=', '>=', '<>', '>', '<']

    OP_LOGICO = ['e', 'ou']

    OP_ATRIBUICAO = '<-'

    def verificar(self, escopos, ctx):

        if(isinstance(ctx, LAParser.Declaracao_localContext)):
            self.verificarDecLocal(escopos, ctx)

        elif(isinstance(ctx, LAParser.Declaracao_globalContext)):
            self.verificarDecGlobal(escopos, ctx)
        elif(isinstance(ctx, LAParser.CmdContext)):
            self.verificarComando(escopos, ctx)

    def verificarDecGlobal(self, escopos, ctx):
        tipo_declaracao = ctx.start.text

        if(tipo_declaracao == 'procedimento'):
            self.declararProcedimento(escopos, ctx)
        elif(tipo_declaracao == 'funcao'):
            self.declararFuncao(escopos, ctx)

    def verificarDecLocal(self, escopos, ctx):
        tipo_declaracao = ctx.start.text

        if(tipo_declaracao == 'declare'):
            self.declararVariaveis(escopos, ctx.variavel())
        elif(tipo_declaracao == 'constante'):
            self.declararConstante(escopos, ctx)
        elif(tipo_declaracao == 'tipo'):
            self.criarTipo(escopos, ctx)


    def verificarIdentificador(self, escopos, ctx):
        aux = self.validarIdentificador(
            escopos, ctx)
        if(not aux or aux['categoria'] not in ['var']):
            return None

        return aux['tipo']


    def verificarChamada(self, escopos, ctx, modo='execucao'):

        chamada = escopos.verificarNosEscopos(ctx.IDENT().getText())
        param_table = chamada['parametros']
        expressoes = ctx.expressao()

        if(not chamada):
            return None

        if(chamada['categoria'] not in ['func', 'proc']):
            self.erroChamadaIncorreta(ctx.IDENT().getSymbol())
            return None


        if(len(param_table.tabela) != len(expressoes)):
            self.erroChamadaIncompativel(ctx.IDENT().getSymbol())
        else:
            for i in range(len(expressoes)):
                tipo_expss = self.obterTipo(escopos, expressoes[i])

                if(not tipo_expss):
                    return None

                if(tipo_expss != list(param_table.tabela.values())[i]['tipo']):
                    self.erroChamadaIncompativel(
                        ctx.IDENT().getSymbol())
                    return None


        if(modo == 'retorno' and chamada['categoria'] not in ['func']):
            self.erroChamadaSemRetorno(ctx.IDENT().getSymbol())
            return None

        if(chamada['categoria'] == 'proc'):
            return None
        else:
            return chamada['tipo']


    def verificarExpressao(self, escopos, ctx):

        ctx_termo = ctx.termo_logico()
        op = ctx.op_logico_1()
        operador = op[0].getText() if op and len(op) > 0 else None
        anterior = None

        for termo in ctx_termo:

            tipo = self.obterTipo(escopos, termo)

            if(not tipo):
                return None

            if(not anterior):
                anterior = tipo
                continue

            anterior = self.validarCompatibilidade(anterior, tipo, operador)

            if(not anterior):
                self.erroTipoIncompativel(termo.start)
                return None

        return anterior


    def verificarTermoLogico(self, escopos, ctx):

        ctx_factor = ctx.fator_logico()

        op = ctx.op_logico_2()
        operador = op[0].getText() if op and len(op) > 0 else None
        anterior = None

        for fator in ctx_factor:

            tipo = self.obterTipo(escopos, fator)

            if(tipo == None):
                return None

            if(anterior == None):
                anterior = tipo
                continue

            anterior = self.validarCompatibilidade(anterior, tipo, operador)

            if(anterior == None):
                self.erroTipoIncompativel(fator.start)
                return None

        return anterior

    def verificarFatorLogico(self, escopos, ctx):

        tipo = self.verificarParcelaLogica(escopos, ctx.parcela_logica())

        if(ctx.start.text == 'nao' and tipo != 'logico'):
            return None

        return tipo

    # verificarParcelaLogica
    # params: escopos, ctx
    # return: verifica se eh tipo basico logico, se for retorna, senao retorna expr relacional
    def verificarParcelaLogica(self, escopos, ctx):
        if(ctx.getText() in ['verdadeiro', 'falso']):
            return 'logico'
        else:
            return self.obterTipo(escopos, ctx.exp_relacional())


    def verificarExpressaoAritmetica(self, escopos, ctx):
        anterior = None
        ctx_termo = ctx.termo()
        local_op1 = ctx.op1()

        if(local_op1 and len(local_op1) > 0):
            operador = local_op1[0].getText()
        else:
            operador = None

        for termo in ctx_termo:
            tipo = self.obterTipo(escopos, termo)

            if(tipo == None):
                return None

            if(anterior == None):
                anterior = tipo
                continue

            anterior = self.validarCompatibilidade(anterior, tipo, operador)

            if(anterior == None):
                self.erroTipoIncompativel(termo.start)
                return None

        return anterior

    #
    # por favor nao mecher
    #
    def verificarTermo(self, escopos, ctx):

        anterior = None
        ctx_factor = ctx.fator()
        op2 = ctx.op2()

        operador = op2[0].getText() if op2 and len(
            op2) > 0 else None
        
        for fator in ctx_factor:
            tipo = self.obterTipo(escopos, fator)

            if(tipo == None):
                return None

            if(anterior == None):
                anterior = tipo
                continue

            anterior = self.validarCompatibilidade(anterior, tipo, operador)

            if(anterior == None):
                self.erroTipoIncompativel(fator.start)
                return None

        return anterior

    def verificarExpressaoRelacional(self, escopos, ctx):

        op_rel = ctx.op_relacional()
        operador = op_rel.getText() if op_rel else None
        anterior = None

        for exp in ctx.exp_aritmetica():

            tipo = self.obterTipo(escopos, exp)

            if(tipo == None):
                return None

            if(anterior == None):
                anterior = tipo
                continue

            anterior = self.validarCompatibilidade(anterior, tipo, operador)

            if(anterior == None):
                self.erroTipoIncompativel(exp.start)
                return None

        return anterior

    #
    #
    #
    def verificarFator(self, escopos, ctx):
        # var auxiliar para validar uso de operador
        anterior = None

        # Retorna uma lista de contextos da regra parcela
        ctx_parcela = ctx.parcela() 
        op3 = ctx.op3()

        if(op3 and len(op3) > 0):
            operador = op3[0].getText()
        else:
            operador = None


        for parcela in ctx_parcela:
            tipo = self.obterTipo(escopos, parcela)

            if(tipo == None):
                return None

            if(anterior == None):
                anterior = tipo
                continue

            anterior = self.validarCompatibilidade(anterior, tipo, operador)

            if(anterior == None):
                self.erroTipoIncompativel(parcela.start)
                return None

        return anterior

    #
    #
    #
    def verificarParcela(self, escopos, ctx):
        tipo = None
        local_op_unario = ctx.op_unario()

        if(local_op_unario):
            local_op = local_op_unario
        else:
            local_op = None
        

        if(ctx.parcela_unario()):
            ctx_parcela = ctx.parcela_unario()

            if(ctx_parcela.expressao()):
                tipo = self.obterTipo(escopos, ctx_parcela.expressao())
            elif(ctx_parcela.cmdChamada()):
                tipo = self.obterTipo(escopos, ctx_parcela.cmdChamada())
            elif(ctx_parcela.NUM_REAL()):
                tipo = 'real'
            elif(ctx_parcela.NUM_INT()):
                tipo = 'inteiro'
            elif(ctx_parcela.identificador()):

                tipo = self.obterTipo(escopos, ctx_parcela.identificador())

                if(tipo):

                    variavel = self.validarIdentificador(
                        escopos, ctx_parcela.identificador())

                    if('ponteiro' in variavel and not ctx_parcela.valor):
                        tipo = 'endereco'

        elif(ctx.parcela_nao_unario()):
            ctx_parcela = ctx.parcela_nao_unario()

            if(ctx_parcela.CADEIA()):
                tipo = 'literal'
            elif(ctx_parcela.identificador()):
                tipo = self.obterTipo(escopos, ctx_parcela.identificador())
                if(tipo and ctx_parcela.endereco):
                    tipo = 'endereco'

        if(tipo not in self.NUMERO and local_op):
            self.erroTipoIncompativel(ctx_parcela.start)
            return None

        return tipo

    def verificarSelecao(self, escopos, ctx):
        for item in ctx.item_selecao():
            self.verificarItemSelecao(escopos, ctx)

    def verificarItemSelecao(self, escopos, ctx):
        for cmd in ctx.cmd():
            self.verificarComando(escopos, cmd)


    def verificarComando(self, escopos, ctx):

        start = ctx.start.text

        if(start == 'se'):
            self.verificarSe(escopos, ctx.cmdSe())

        elif(start == 'caso'):
            self.verificarCaso(escopos, ctx.cmdCaso())

        elif(start == 'leia'):
            self.verificarLeitura(escopos, ctx.cmdLeia())

        elif(start == 'escreva'):
            self.verificarEscrita(escopos, ctx.cmdEscreva()) 

        elif(start == 'para'):
            self.verificarPara(escopos, ctx.cmdPara())

        elif(start == 'enquanto'):
            self.verificarEnquanto(escopos, ctx.cmdEnquanto())

        elif(start == 'faca'):
            self.verificarFaca(escopos, ctx.cmdFaca())

        elif(ctx.cmdAtribuicao()):
            self.verificarAtribuicao(escopos, ctx.cmdAtribuicao())

    def verificarLeitura(self, escopos, ctx):
        for ident in ctx.identificador():
            if( not self.validarIdentificador(escopos, ident)):
                return

    def verificarEscrita(self, escopos, ctx):
        for exp in ctx.expressao():
            tipo = self.verificarExpressao(escopos, exp)

    def verificarSe(self, escopos, ctx):
        tipo_exprss = self.obterTipo(escopos, ctx.expressao())
        if(tipo_exprss != 'logico'):
            return None

        for cmd in ctx.se:
            self.verificarComando(escopos, cmd)

        for cmd in ctx.senao:
            self.verificarComando(escopos, cmd)

    def verificarCaso(self, escopos, ctx):
        tipo_exprss_arit = self.obterTipo(escopos, ctx.exp_aritmetica())

        if(not tipo_exprss_arit):
            return None

        if(tipo_exprss_arit not in self.NUMERO):
            self.erroTipoIncompativel(ctx.start)
            return None

    def verificarPara(self, escopos, ctx):

        iterador = self.validarIdentificador(
            escopos, ctx.IDENT(), context=False)

        if(not iterador):
            return None

        if(iterador['tipo'] != 'inteiro'):
            self.erroTipoIncompativel(ctx.IDENT())
            return None

        # ctx.exp_aritmetica (contendo duas expss aritmeticas)
        for expss in ctx.exp_aritmetica():

            tipo_expss = self.obterTipo(escopos, expss)

            if(not tipo_expss):
                return None

            if(tipo_expss != 'inteiro'):
                self.erroTipoIncompativel(exp.start)
                return None

        for cmd in ctx.cmd():
            self.verificarComando(escopos, cmd)

    def verificarEnquanto(self, escopos, ctx):
        tipo_expss = self.obterTipo(escopos, ctx.expressao())

        if(not tipo_expss):
            return None

        if(tipo_expss != 'logico'):
            self.erroTipoIncompativel(ctx.expressao().start)
            return None

        for cmd in ctx.cmd():
            self.verificarComando(escopos, cmd)

    def verificarFaca(self, escopos, ctx):
        for cmd in ctx.cmd():
            self.verificarComando(escopos, cmd)

        tipo_expss = self.obterTipo(escopos, ctx.expressao())

        if(not tipo_expss):
            return None

        if(tipo_expss != 'logico'):
            self.erroTipoIncompativel(ctx.expressao().start)
            return None

    def verificarAtribuicao(self, escopos, ctx):

        self.ATRIBUICAO = True

        identificador = self.validarIdentificador(escopos, ctx.identificador())

        if(not identificador):
            return None

        tipo_expss = self.obterTipo(escopos, ctx.expressao())

        self.ATRIBUICAO = False

        operador = ctx.ATRIBUIDOR().getText()

        if('ponteiro' in identificador and not ctx.valor):
            tipo_ident = 'endereco'
        else:
            tipo_ident = identificador['tipo']

        validacao = self.validarCompatibilidade(tipo_ident, tipo_expss, operador=operador)

        if(not validacao):
            token_IDENT = self.obterTokenIDENT(ctx.identificador())

            if ctx.valor:
                token_IDENT.text = '^'+token_IDENT.text

            if ctx.identificador().dimensao():
                token_IDENT.text = token_IDENT.text + ctx.identificador().dimensao().getText()

            self.erroTipoIncompativel(token_IDENT)
            return None


    def declararVariaveis(self, escopos, ctx):

        curr_escopo = escopos.getAtualEscopo()
        tipo = ctx.tipo()
        
        for loca_ctx in ctx.identificador():
            self.declararIdentificador(escopos, loca_ctx, tipo)

    def declararConstante(self, escopos, ctx):

        curr_escopo = escopos.getAtualEscopo()
        ident = ctx.IDENT().getText()

        if(curr_escopo.verificar(ident)):

            self.erroJaDeclarado(ctx.IDENT().getSymbol())
            return

        tipo = ctx.tipo_basico().getText()
        valor = ctx.valor_constante()

        if( tipo == 'real' and not valor.NUM_REAL or tipo == 'literal' and not valor.CADEIA()
            or tipo == 'inteiro' and not valor.NUM_INT
            or tipo == 'logico' and valor.getText() not in ['verdadeiro', 'falso']):
            self.erroTipoIncompativel(ctx.IDENT().getSymbol())
            return

        curr_escopo.inserir(ident, 'IDENT', 'const', tipo, valor=valor.getText())


    def declararProcedimento(self, escopos, ctx):

        sub_tabela = TabelaSimbolos()
        params = TabelaSimbolos()

        if(ctx.parametros()):
            
            params = self.obterTabelaParametros(escopos, ctx.parametros())


        if(ctx.declaracao_local()):

            sub_tabela = self.obterSubtabela(escopos, ctx, params=params)

        escopos.criarEscopo(params.join(params, sub_tabela))

        if(ctx.cmd()):

            for cmd in ctx.cmd():
                if(cmd.cmdRetorne()):
                    self.erroRetorne(cmd.start)

                self.verificarComando(escopos, cmd)

        escopos.abandonarEscopo()

        escopos.getAtualEscopo().inserir(ctx.IDENT().getText(), 'IDENT', 'proc', None,\
            parametros=params, subtabela=sub_tabela)


    def declararFuncao(self, escopos, ctx):

        params = TabelaSimbolos()
        tipo_token = ctx.tipo_estendido().tipo_basico_ident()
        subtabela = TabelaSimbolos()

        if(not self.validarTipoVar(escopos, tipo=tipo_token.getText())):
            self.erroTipoInexistente(ctx.IDENT().getSymbol(), tipo_token.getText())
            return

        if(ctx.parametros()):
            params = self.obterTabelaParametros(escopos, ctx.parametros())

        
        if(ctx.declaracao_local()):
            subtabela = self.obterSubtabela(escopos, ctx, params=params)


        # Cria um novo escopo para simular a chamada da função e possibilitar a análise
        escopos.criarEscopo(params.join(params, subtabela))

        if(ctx.cmd()):
            for cmd in ctx.cmd():
                self.verificarComando(escopos, cmd)

        escopos.abandonarEscopo()

        escopos.getAtualEscopo().inserir(ctx.IDENT().getText(), 'IDENT', 'func',\
            tipo_token.getText(), parametros=params, subtabela=subtabela)



    # declararIdentificador
    # params: escoposm ctx_identificador, tipo_ctx, extra
    # return: caso haja erro ocorre um return, senao o identificador eh declarado
    def declararIdentificador(self, escopos, ctx_identificador, tipo_ctx, extra={}):

        identificador = ctx_identificador.IDENT()
        curr_escopo = escopos.getAtualEscopo()
        tamanho = []

        if(len(identificador) > 1 and '.' in ctx_identificador.getText()):
            return
        else:
            identificador = identificador[0]

        if(isinstance(tipo_ctx, LAParser.TipoContext) and tipo_ctx.registro()):
            custom_reg = self.criarRegistroNaoInstanciavel(
                escopos, tipo_ctx.registro())
            tipo_txt = custom_reg['nome']
        else:
            if('^' in tipo_ctx.start.text):
                extra['ponteiro'] = True

                tipo_txt = tipo_ctx.getText()[1::]
            else:
                tipo_txt = tipo_ctx.getText()

        dimensoes = ctx_identificador.dimensao().exp_aritmetica()

        if(not self.validarTipoVar(escopos, tipo=tipo_txt)):
            self.erroTipoInexistente(identificador.getSymbol(), tipo_ctx.getText())


        if(curr_escopo.verificar(identificador.getText()) == None):
            additional_args = {**extra}

            if(len(dimensoes) > 0):
                

                for dim in dimensoes:
                    tamanho.append(dim.getText())

                additional_args['tamanho'] = tamanho

            curr_escopo.inserir(identificador.getText(), 'IDENT', \
                'var', tipo_txt, **additional_args)
        else:
            self.erroJaDeclarado(identificador.getSymbol())

    # validarCompatibilidade
    #
    #
    #
    def validarCompatibilidade(self, tipo1, tipo2, operador=None):

        if(not operador):
            return None


        if(operador in self.OP_RELACIONAL):
            if (operador not in ['=', '<>'] and ((tipo1 == 'logico' or tipo2 == 'logico') or (tipo1 == 'literal' or tipo2 == 'literal'))):  # Se um deles é lógico ou literal e a comparação não é de igualdade ou diferença,
                return None

            elif(tipo1 == tipo2 or tipo1 in self.NUMERO and tipo2 in self.NUMERO):
                return 'logico'

        elif(operador in self.OP_LOGICO):
            if(tipo1 == 'logico' or tipo2 == 'logico'):
                return 'logico'
            else:
                return None

        elif(operador in self.OP_ARIT):

            # concatenacao nao comum
            if(tipo1 == tipo2 and tipo1 == 'literal'):
                return 'literal'
            # se pode fazer a operação
            elif(not (tipo1 in self.NUMERO and tipo2 in self.NUMERO)):
                return None
            else:
                if(tipo1 == tipo2):
                    return tipo1
                else:
                    return 'real'

        elif(operador == self.OP_ATRIBUICAO):
            if(tipo1 == tipo2):
                return tipo1
            elif(tipo1 == 'real' and tipo2 in self.NUMERO):
                return 'real'
            else:
                return None

    # validarTipoVar: checa a validade de tipo em atribuicoes
    # params: escopos, tipo (string)
    # return
    def validarTipoVar(self, escopos, tipo=None):

        if(not tipo):
            return False

        if(tipo in self.TIPOS):
            return True

        # verifica se é um registro ou um tipo estendido.
        check = escopos.verificarNosEscopos(tipo)

        # verifica se é um tipo estendido ou registro
        # caso contrario retorne falso
        if(check and (check['token'] == 'IDENT' and check['categoria'] in ['registro', 'tipo'])):
            return True
        else:
            return False

    # validarIdentificador: retorna o registro do identificador em caso de sucesso
    # params: escopos, 
    # identif_referenc: contexto do tipo LAParser.IdentificadorContext ou IDENT
    # context
    # return
    def validarIdentificador(self, escopos, identif_referenc, context=True):

        if (context):
            identificador = identif_referenc.IDENT()
        else:
            identificador = identif_referenc


        if(not identificador):
            return None

        if(isinstance(identificador, list) and len(identificador) > 1):
            aux = escopos.verificarNosEscopos(identificador[0].getText())

            # Registro existe ?
            if(not aux):
                self.erroNaoDeclarado(self.obterTokenIDENT(
                    identif_referenc, context=context))
                return None

            if(aux['categoria'] != 'var' or aux['tipo'] in self.TIPOS):

                self.erroTipoIncompativel(identificador[0].getSymbol())

                return None

            registro = escopos.verificarNosEscopos(aux['tipo'])

            # Verifica a existencia do atributo
            if(identificador[1].getText() not in registro['subtabela'].tabela):
                self.erroNaoDeclarado(self.obterTokenIDENT(
                    identif_referenc, context=context))
                return None
            else:
                aux = registro['subtabela'].verificar(
                    identificador[1].getText())

        else:

            if(isinstance(identificador, list)):
                identificador = identificador[0]
            else:
                identificador = identificador

            aux = escopos.verificarNosEscopos(identificador.getText())

            if(not aux):
                self.erroNaoDeclarado(identificador.getSymbol())

                return None

        return aux


    # obterTipo
    # params: escopos, ctx
    # 
    # python nao tem switch case, entao unica forma
    def obterTipo(self, escopos, ctx):

        # if(params):
            # escopos.criarEscopo(params)

        # escopos.criarEscopo()

        # for dec in ctx.declaracao_local():
        #     self.declararVariaveis(escopos, dec.variavel())

        if isinstance(ctx, LAParser.Exp_relacionalContext):
            return self.verificarExpressaoRelacional(escopos, ctx)

        elif isinstance(ctx, LAParser.ExpressaoContext):
            return self.verificarExpressao(escopos, ctx)

        elif isinstance(ctx, LAParser.Termo_logicoContext):
            return self.verificarTermoLogico(escopos, ctx)

        elif isinstance(ctx, LAParser.ParcelaContext):
            return self.verificarParcela(escopos, ctx)

        elif isinstance(ctx, LAParser.CmdChamadaContext):
            return self.verificarChamada(escopos, ctx, modo='retorno')

        elif isinstance(ctx, LAParser.Fator_logicoContext):
            return self.verificarFatorLogico(escopos, ctx)

        elif isinstance(ctx, LAParser.Exp_aritmeticaContext):
            return self.verificarExpressaoAritmetica(escopos, ctx)

        elif isinstance(ctx, LAParser.TermoContext):
            return self.verificarTermo(escopos, ctx)

        elif isinstance(ctx, LAParser.IdentificadorContext):
            return self.verificarIdentificador(escopos, ctx)

        elif isinstance(ctx, LAParser.FatorContext):
            return self.verificarFator(escopos, ctx)
        

        return None

    # obterSubtabela: 
    # params: escopos, ctx, params
    #
    #
    def obterSubtabela(self, escopos, ctx, params=None):

        if(params):
            escopos.criarEscopo(params)

        escopos.criarEscopo()

        for dec in ctx.declaracao_local():
            self.declararVariaveis(escopos, dec.variavel())

        subtabela = escopos.getAtualEscopo()

        escopos.abandonarEscopo()

        if(params):
            escopos.abandonarEscopo()

        return subtabela


    def obterTabelaParametros(self, escopos, ctx):

        escopos.criarEscopo()
        curr_escopo = escopos.getAtualEscopo()

        for param in ctx.parametro():

            tipo = param.tipo_estendido()

            for ident in param.identificador():

                self.declararIdentificador(escopos, ident, tipo, {
                                           'referencia': (param.start.text == 'var')})

        escopos.abandonarEscopo()

        return curr_escopo

    def obterTokenIDENT(self, identif_referenc, context=True):

        if(context):
            identificador = identif_referenc.IDENT()
        else:
            identificador = identif_referenc

        if(isinstance(identificador, list) and len(identificador) > 1):

            token = identificador[0].getSymbol()
            token.text = token.text+'.'+identificador[1].getSymbol().text

            return token
        else:
            if(isinstance(identificador, list)):
                identificador = identificador[0]
            else:
                identificador = identificador

            return identificador.getSymbol()

    # obterSubtabelaRegistro
    # params: escopos, ctx(tipo.registro())
    #
    def obterSubtabelaRegistro(self, escopos, ctx):

        # Um novo escopo é criado para comportar as variáveis do registro.
        escopos.criarEscopo()

        for variavel in ctx.variavel():
            self.declararVariaveis(escopos, variavel)

        sub_escopo = escopos.getAtualEscopo()

        escopos.abandonarEscopo()

        return sub_escopo

    # criarRegistroNaoInstanciavel
    # params: escopos, ctx
    #
    def criarRegistroNaoInstanciavel(self, escopos, ctx):

        # for variavel in ctx.variavel():
        #     self.declararVariaveis(escopos, variavel)


        nome_randomico = '__reg_custom_' + \
            str(''.join(random.choices(string.ascii_uppercase, k=8)))

        sub_escopo = self.obterSubtabelaRegistro(escopos, ctx)

        return escopos.getAtualEscopo().inserir(nome_randomico, 'IDENT', 'registro', None, subtabela = sub_escopo)

    # criarTipo
    # params: escopos, ctx
    # return:
    def criarTipo(self, escopos, ctx):

        ident = ctx.IDENT().getText()
        token = ctx.IDENT().getSymbol()
        curr_escopo = escopos.getAtualEscopo()
        tipo = ctx.tipo()

        # O escopo possui um identificador de nome igual
        if(curr_escopo.verificar(ident)):
            self.erroJaDeclarado(ctx.IDENT().getSymbol())
            return

        
        # subtabela decls locais desse registro
        if(tipo.registro()):
            sub_escopo = self.obterSubtabelaRegistro(escopos, tipo.registro())

            escopos.getAtualEscopo().inserir(
                ident, 'IDENT', 'registro', None, subtabela=sub_escopo)

        elif(tipo.tipo_estendido()):

            if((not tipo.tipo_estendido().tipo_basico_ident().tipo_basico()
                    and not self.validarTipoVar(escopos, tipo=tipo.getText()))):

                self.adicionarErro(token, 'Tipo nao declarado')

                return

            curr_escopo.inserir(ident, 'IDENT', 'tipo', tipo.getText())

    #
    # ERROS COMUNS QUE MERECEM ATENCAO
    #
    def adicionarErro(self, token, mensagem):
        err_msg = f"Linha {token.line}: {mensagem}"
        self.errosSemanticos.append(err_msg)

    def erroJaDeclarado(self, token):
        err_msg = f"identificador {token.text} ja declarado anteriormente"
        self.adicionarErro(token, err_msg)

    def erroChamadaIncorreta(self, token):
        err_msg = f"{token.text} nao e uma funcao ou procedimento"
        self.adicionarErro(token, err_msg)

    def erroRetorne(self, token):
        err_msg = f"comando retorne nao permitido nesse escopo"
        self.adicionarErro(token, err_msg)

    def erroNaoDeclarado(self, token):
        err_msg = f"identificador {token.text} nao declarado"
        self.adicionarErro(token, err_msg)

    def erroTipoIncompativel(self, token):
        err_msg = f"atribuicao nao compativel para {token.text}"
        if self.ATRIBUICAO:
            return

        self.adicionarErro(token, err_msg)

    def erroTipoInexistente(self, token, tipo):
        err_msg = f"tipo {tipo} nao declarado"
        self.adicionarErro(token, err_msg)

    def erroChamadaSemRetorno(self, token):
        err_msg = f"{token.text} nao possui retorno"
        self.adicionarErro(token, err_msg)

    def erroChamadaIncompativel(self, token):
        err_msg = f"incompatibilidade de parametros na chamada de {token.text}"
        self.adicionarErro(token, err_msg)
