# Compilador C-like para MIPS

**Autor:** Pedro Lustosa Coutinho

## Sobre o Projeto
Este é um compilador de uma passagem (*single-pass*) desenvolvido em Python que traduz uma linguagem imperativa de alto nível (com sintaxe semelhante à linguagem C) diretamente para código de máquina na arquitetura **MIPS Assembly**.

O compilador utiliza a abordagem de **Tradução Dirigida pela Sintaxe (Syntax-Directed Translation)**. Isso significa que não há a construção de uma árvore intermediária (AST). A análise sintática, a análise semântica e a geração de código objeto ocorrem de forma simultânea e unificada: as instruções MIPS são emitidas no exato momento em que as regras gramaticais são reconhecidas.

## Arquitetura Interna e Componentes

O projeto opera sob uma arquitetura enxuta, dividida nas seguintes engrenagens:

### 1. Análise Léxica (`lexerForC.py`)
O analisador léxico é o primeiro ponto de contato com o código-fonte bruto, transformando a cadeia de caracteres em uma sequência de unidades significativas (*Tokens*).
* **Expressões Regulares:** Varre o texto utilizando uma especificação de padrões (via biblioteca `re`), identificando palavras-chave, números, identificadores e ignorando espaços e comentários (`//` e `/* */`).
* **Tratamento Precoce de Erros:** Padrões malformados (como números atrelados a letras) são capturados deliberadamente no topo da lista de busca, garantindo que o compilador aponte falhas antes que alcancem as fases seguintes.
* **Mapeamento de Coordenadas:** Rastreia ativamente linhas e colunas para emissão de mensagens de erro precisas.

### 2. Análise Sintática (`parserAndAnaSemForC.py`)
Um *Recursive Descent Parser* (Analisador Descendente Recursivo) que agrupa os tokens em estruturas gramaticais válidas.
* **Mapeamento de Regras:** Cada variável não-terminal da gramática é um método na classe. A execução desce recursivamente de blocos gerais para comandos e expressões.
* **Precedência em Cascata:** Para respeitar a ordem matemática sem uma AST, as expressões são analisadas em uma hierarquia de chamadas consecutivas. A busca inicia nas operações relacionais, desce para soma/subtração, depois multiplicação/divisão, até alcançar fatores atômicos (forçando a base da pilha a resolver a multiplicação primeiro).

### 3. Análise Semântica (Integrada ao Parser)
Garante que o significado do programa faça sentido, aplicando regras contextuais.
* **Tabela de Símbolos:** Um dicionário dinâmico que armazena variáveis e seus tipos. É consultado para impedir dupla declaração e garantir o uso correto de variáveis previamente alocadas.
* **Verificação de Tipos:** O tipo resultante de subexpressões é propagado e validado. Incompatibilidades (ex: somar um `float` com um `char`) geram erros imediatos e abortam a compilação.

### 4. Geração de Código MIPS (Integrada ao Parser)
Traduz as construções validadas diretamente em instruções Assembly.
* **Gerenciamento Dinâmico de Registradores:** O compilador mantém um *pool* de registradores temporários (`$t0` a `$t9`). Eles são alocados para armazenar resultados de subexpressões e liberados assim que o valor é consumido por operações de nível superior.
* **Rótulos Dinâmicos:** Cria *labels* sequenciais únicos (ex: `L1_while_start`) para controlar os desvios de fluxo (`if`, `while`, `for`).
* **Bufferização do Laço FOR:** Como a atualização da variável do `for` é lida no cabeçalho mas deve rodar apenas no fim da iteração, o gerador de código desvia a emissão dessa instrução para um buffer temporário. Após compilar o corpo do laço, esse buffer é descarregado (injetado) no Assembly final, logo antes do salto de retorno.

## Funcionalidades Suportadas
* **Tipos de Dados:** `int`, `float`, `char`, `bool`.
* **Estruturas de Controle:** Condicionais (`if`, `if/else`) e Repetição (`while`, `for`).
* **Operadores Relacionais:** `==`, `!=`, `<`, `>`, `<=`, `>=`.

## Como Executar

**Pré-requisitos:** Python 3.x instalado.

Na raiz do projeto, crie um arquivo chamado `entrada.txt` e insira o seu código-fonte.
   *Exemplo:*
   ```c
   int a = 5;
   int b = 10;
   int soma = a + b;

   comando para a execução:
        python main.py

Abaixo estão as regras estruturais reconhecidas pelo Parser:

<programa>    ::= <bloco>
<bloco>       ::= "{" <comando>* "}"

<comando>     ::= <declaracao> 
                | <atribuicao> 
                | <condicao> 
                | <repeticao> 
                | <laco_for>

<declaracao>  ::= <tipo> IDENTIFIER [ "=" <expressao> ] ";"
<atribuicao>  ::= IDENTIFIER "=" <expressao> ";"

<condicao>    ::= "if" "(" <expressao> ")" <bloco> [ "else" <bloco> ]
<repeticao>   ::= "while" "(" <expressao> ")" <bloco>
<laco_for>    ::= "for" "(" ( <declaracao> | <atribuicao> ) <expressao> ";" <atribuicao_sem_ponto_virgula> ")" <bloco>

<expressao>   ::= <relacional>
<relacional>  ::= <soma> ( ("==" | "!=" | "<" | ">" | "<=" | ">=") <soma> )*
<soma>        ::= <termo> ( ("+" | "-") <termo> )*
<termo>       ::= <fator> ( ("*" | "/") <fator> )*

<fator>       ::= "(" <expressao> ")" 
                | NUMBER 
                | IDENTIFIER 
                | LITERAL

<tipo>        ::= "INT" | "FLOAT" | "CHAR" | "STRING" | "BOOL"