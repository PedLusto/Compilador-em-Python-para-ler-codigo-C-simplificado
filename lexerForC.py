import re
import parserAndAnaSemForC as parserCod

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value}, linha={self.line}, coluna={self.column})"


class Lexer:

    #expressões regulares!!
    token_specification = [
    ('INVALID_NUMBER', r'\d+[a-zA-Z_]+[a-zA-Z0-9_]*|\d+(\.\d+){2,}'),
    ('COMMENT', r'//.*'),
    ('INVALID_OPERATOR', r'(=\+|!\<)'),
    ('MULTILINE_COMMENT', r'/\*[\s\S]*?\*/'),
    ('NUMBER', r'\d+(\.\d+)?'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('OPERATOR', r'(\+\+|--|\+=|-=|\*=|/=|==|!=|<=|>=|&&|\|\||\+|-|\*|/|=|<|>)'),
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
        "for":"FOR",
        "bool":"BOOL",
        "string":"STRING",
        "float":"FLOAT",
        "while": "WHILE",
        "else":"ELSE"
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

                    elif token_type == "INVALID_NUMBER":
                        tokens.append(Token("ERROR", text, self.line, self.column))
                        self.column += len(text)

                    elif token_type == "OPERATOR":
                        valid_ops = {"++","--","+=","-=","*=","/=","==","!=","<=",">=","&&","||","+","-","*","/","=","<",">"}

                        if text not in valid_ops:
                            token_type = "ERROR"

                        tokens.append(Token(token_type, text, self.line, self.column))
                        self.column += len(text)

                    elif token_type in ("COMMENT", "MULTILINE_COMMENT"):
                        lines = text.count("\n")
                        if lines > 0:
                            self.line += lines
                            self.column = 1
                        else:
                            self.column += len(text)

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
                invalid_char = self.code[0]

                tokens.append(Token("ERROR", invalid_char, self.line, self.column))

                self.code = self.code[1:]
                self.column += 1
        return tokens