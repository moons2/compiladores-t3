'''
titulo:
    Analisador Semantico para a Linguagem Algoritmica (LA)
    TRABALHO 3 - COMPILADORES 1

autores:
    Luan V. Moraes da Silva - 744342
    Guilherme Servidoni - 727339
    Alisson Roberto Gomes - 725721

para compilar:
    > java -jar antlr4-4.8-complete.jar -Dlanguage=Python3 -visitor LA.g4

para executar:
    > [python | python3] main.py input-program.txt output-program.txt
'''

# importacoes
from antlr4 import *
from LALexer import LALexer
from LAParser import LAParser
from LAInterpreter import LAInterpreter
from LACGenerator import LACGenerator
import sys
import os

# 
# Parser para erros semanticos
#
class ParserErroListener(object):
    def syntaxError(recognizer, offendingSymbol, line, column, msg, e):
        if "EOF" in offendingSymbol.text:
            offendingSymbol.text = "EOF"

        err_msg = f'Linha {line}: erro sintatico proximo a {offendingSymbol.text}'

        raise Exception(err_msg)


#
# Tratamento de erros lexicos
#
class LexicoErroListener(object):
    def syntaxError(recognizer, offendingSymbol, line, column, msg, e):

        text = recognizer._input.getText(
            recognizer._tokenStartCharIndex, recognizer._input.index)

        text = text.replace('\n', '')

        if text[0] == '"' and len(text) > 1:
            raise Exception(f'Linha {line}: cadeia literal nao fechada')
        elif text[0] == '{' and len(text) > 1:
            raise Exception(f'Linha {line}: comentario nao fechado')
        else:
            raise Exception(f'Linha {line}: {text} - simbolo nao identificado')

# funcao principal
# params: argv, uma lista com as entradas obtidas da linha de comando
# return: nao possui return
def main(argv):

    # verificacao basica de numero de argumentos
    if (len(argv) < 2):
        print("O Comando deve necessariamente conter dois argumentos!\n")
        return

    # guarda argumento 1
    input_file = argv[1]

    # guarda argumento 2
    output_file = argv[2]

    # verifica se o arquivo destino output existe
    if os.path.exists(output_file):
        # se existir entao ele eh apagado
        os.remove(output_file)

    # o arquivo onde a saida sera gerada eh entao criado
    target_file = open(output_file, "a")

    # metodo da lib antlr4 que le um arquivo
    input_stream = FileStream(input_file, encoding="utf-8")

    # variavel que sera atribuida ao arquivo destino e variaveis uteis na execucao
    output = ""
    tree = False
    interpreter = False

    # objeto Lexer criado
    lexer = LALexer(input_stream)

    # por garantia
    lexer.removeErrorListeners()
    lexer._listeners = [LexicoErroListener]

    # fluxo de tokens
    tokens = CommonTokenStream(lexer)
    parser = LAParser(tokens)

    # removendo os listeners de erros defaults
    parser.removeErrorListeners()
    parser._listeners = [ParserErroListener]

    try:
        tree = parser.programa()
    except Exception as err:
        output += f'{str(err)}\nFim da compilacao\n'

    if tree:
        try:
            interpreter = LAInterpreter()
            interpreter.visitPrograma(tree)
        except Exception as err:
            output += str(err)
            output += f'Fim da compilacao\n'

    if interpreter:
        if len(interpreter.utils.errosSemanticos):
            output += '\n'.join(interpreter.utils.errosSemanticos)
            output += f'\nFim da compilacao\n'
        else:
            translator = LACGenerator(interpreter.escopos, interpreter.utils)
            translator.visitPrograma(tree)
            output += '\n'.join(translator.saida)

    # a variavel output eh entao escrita no arquivo destino e fechado
    target_file.write(output)
    target_file.close()


# assinatura python para verificar se este arquivo e o principal
if __name__ == '__main__':
    main(sys.argv)
