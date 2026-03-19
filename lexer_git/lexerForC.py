import re

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value}, linha={self.line}, coluna={self.column})"


class Lexer:

    token_specification = [
    ('COMMENT', r'//.*'),
    ('MULTILINE_COMMENT', r'/\*[\s\S]*?\*/'),
    ('NUMBER', r'\d+(\.\d+)?'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('OPERATOR', r'(\+\+|--|\+=|-=|\*=|/=|==|!=|<=|>=|\+|-|\*|/|=|<|>)'),
    ('SEPARATOR', r'[\(\)\[\]\{\},:\.;]'),
    ('LITERAL', r'(\".*?\"|\'.*?\')'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
]

    keywords = {
        "int":"INT",
        "char":"CHAR",
        "print": "PRINT",
        "if": "IF",
        "while": "WHILE",
        "else":"ELSE",
    }

    def __init__(self, code):
        self.code = code
        self.line = 1
        self.column = 1

    def tokenize(self):
        tokens = []

        while self.code:

            match = None

            for token_type, pattern in self.token_specification:

                regex = re.compile(pattern)
                match = regex.match(self.code)

                if match:
                    text = match.group(0)

                    if token_type == "NEWLINE":
                        self.line += 1
                        self.column = 1

                    elif token_type == "SKIP":
                        self.column += len(text)

                    elif token_type == "COMMENT" or token_type == "MULTILINE_COMMENT":
                        self.code = self.code[len(text):]
                        continue

                    else:
                        if token_type == "IDENTIFIER" and text in self.keywords:
                            token_type = self.keywords[text]

                        tokens.append(Token(token_type, text, self.line, self.column))
                        self.column += len(text)

                    self.code = self.code[len(text):]
                    break

            if not match:
                raise SyntaxError(
                    f"Erro léxico: caractere inválido '{self.code[0]}' na linha {self.line}, coluna {self.column}"
                )

        return tokens
    
#code = """
#x = 10
#y = x + 5
#print y
#"""

code="""
int x=5;
for(y=1;y<100;y++){
    y--;
    y=23;
}
//comentarioooo
/* comen
tari
ooooo
*/
"""

lexer = Lexer(code)

tokens = lexer.tokenize()

for token in tokens:
    print(token)