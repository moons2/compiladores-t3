

<h1 align="center"> Analisador Semântico para a Linguagem Algorítmica (LA) </br> Trabalho 3</h1>

<p align="center">UNIVERSIDADE FEDERAL DE SÃO CARLOS</p>

<p align="center">Disciplina: Compiladores 1</p>

<p align="center">Professor: Daniel Lucrédio</p>


## SUMÁRIO

[Pré requisitos](#pré-requisitos)

[Execução](#execução)

[Compilação](#compilação)

[Código fonte](#código-fonte)

[Exemplo](#exemplo)

[Autores](#autores)

## PRÉ REQUISITOS

Este programa faz uso de Antlr com Python, desta forma é necessario ter instalado:

### 1. [python3](https://www.python.org/ftp/python/3.9.2/python-3.9.2-amd64.exe)

Você pode verificar se a instalação foi realizada com exito digitando no terminal:

```terminal
python3 --version
```

:warning: **ATENÇÃO** :warning: : se o comando `python3` não for reconhecido, substitua as ocorrências de `python3` neste tutorial por `python`, ou verifique se o comando `python3` está incluso nas variáveis de ambiente do seu sistema!

### 2. Antlr para python

Após ter instalado `python3`, instale o [Antlr para python](https://www.antlr.org/download.html) `na versão 4.8` através do terminal com o comando:

```terminal
pip install antlr4-python3-runtime==4.8
```

:warning: **Siga estritamente as versões específicadas nesta introdução, pois o Antlr apresenta alterações na produção do Parser que pode comprometer a execução do programa!**

Caso o comando `pip` não seja reconhecido, experimente o comando `pip3`


### 3. Qualquer versão Java JDK 11.0.2 ou superior.

Você pode verificar se tem o Java instalado em seu sistema obtendo a versão através do terminal com o seguinte comando:

```terminal
java -version
```

### 4. Este repositorio

faça o download deste repositorio clicando em **Code > Download Zip** e descompate em um diretorio local ou através do terminal com:

```terminal
git clone https://github.com/moons2/compiladores-t3
```

## EXECUÇÃO

Por fim, para executar nosso analisador semântico e gerador basta inserir o seguinte comando no terminal:

```terminal
python3 main.py path_arquivo_entrada.txt path_arquivo_saida.txt
```

onde `main.py` é o arquivo ou path até o arquivo principal, `path_arquivo_entrada.txt` é o caminho até o arquivo a ser analisado semanticamente e `path_arquivo_saida.txt` é o caminho onde o resultado da analise semantica será gerada.

## COMPILAÇÃO

Uma vez cumprido os passos presentes em [Pré requisitos](#pré-requisitos), precisamos compilar a gramática regular `LA.g4`, abra o terminal na pasta `/src` e digite:

```terminal
java -jar antlr4-4.8-complete.jar -Dlanguage=Python3 -visitor LA.g4
```

Nenhuma mensagem foi exibida no terminal, mas foram gerados alguns arquivos como `LALexer.py`, `LA.interp`, `LALexer.tokens`, `LAListener.py`, `LA.tokens`, `LAParser.py`, `LAVisitor.py`

:+1: Compilação realizada com exito!

## CÓDIGO FONTE

O código fonte principal devidamente comentado desta aplicação se encontra na pasta `src/main.py`!

## EXEMPLO

Um exemplo da execução do programa via linha de comando usando caminho absoluto:

```terminal
python3 C:/compiladores/compilatores-t3-main/src/main.py C:/compiladores/compilatores-t3-main/src/testes/input/1-algoritmo_2-2_apostila_LA.txt C:/compiladores/compilatores-t3-main/src/testes/output/1-algoritmo_2-2_apostila_LA.txt
```

Seguindo as instruções para uso do corretor providas pelo professor, um exemplo de execução deste programa via terminal se dá a seguir:

```terminal
java -jar C:/compiladores/compiladores-corretor-automatico-1.0-SNAPSHOT-jar-with-dependencies.jar "python3 C:/compiladores/compiladores-t3-main/src/main.py" gcc C:/compiladores/temp C:/compiladores/casos-de-teste "744342, 727339, 725721" semantico
```

ou 

```terminal
java -jar C:/compiladores/compiladores-corretor-automatico-1.0-SNAPSHOT-jar-with-dependencies.jar "python3 C:/compiladores/compiladores-t3-main/src/main.py" gcc C:/compiladores/temp C:/compiladores/casos-de-teste "744342, 727339, 725721" gerador
```

## AUTORES

Luan V. Moraes da Silva - 744342

Guilherme Servidoni - 727339

Alisson Roberto Gomes - 725721
