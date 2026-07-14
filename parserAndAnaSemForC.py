class Parser:
    def __init__(self, tokens):
        self.symbol_table = {}
        self.tokens = tokens
        self.pos = 0
        self.token = self.tokens[self.pos] if tokens else None
        self.errors = []
        
        self.code_segment = []
        self.data_segment = []
        self.used_regs = set()
        self.label_count = 0

    def emit(self, instruction):
        self.code_segment.append(instruction)

    def get_reg(self):
        for i in range(10):
            reg = f"$t{i}"
            if reg not in self.used_regs:
                self.used_regs.add(reg)
                return reg
        self.error("Falta de registradores temporários")
        return "$t0"

    def free_reg(self, reg):
        if reg in self.used_regs:
            self.used_regs.remove(reg)

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def next_token(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token = self.tokens[self.pos]
        else:
            self.token = None

    def error(self, msg="Erro de sintaxe"):
        if self.token:
            mensagem = f"{msg} na linha {self.token.line}, coluna {self.token.column} (token: {self.token.value})"
        else:
            mensagem = f"{msg} no final do arquivo"
        self.errors.append(mensagem)

    def sync(self):
        self.next_token()
        while self.token is not None:
            if self.match("SEPARATOR", ";") or self.match("SEPARATOR", "}"):
                self.next_token()
                return
            self.next_token()

    def match(self, type_, value=None):
        if self.token is None or self.token.type != type_:
            return False
        if value is not None and self.token.value != value:
            return False
        return True

    def expect(self, type_, value=None):
        if not self.match(type_, value):
            self.error(f"Esperado {type_} {value if value else ''}")
        self.next_token()

    def parse(self):
        self.bloco()

        if self.errors:
            print("Código INVÁLIDO:\n")
            for e in self.errors:
                print(e)
            return None

        print("=== CÓDIGO MIPS GERADO ===\n")
        print(".data")
        for decl in self.data_segment:
            print(f"    {decl}")
            
        print("\n.text")
        print(".globl main")
        print("main:")
        for inst in self.code_segment:
            if inst.endswith(":"):
                print(inst)
            else:
                print(f"    {inst}")
                
        print("    li $v0, 10")
        print("    syscall\n")

        print("=== TABELA DE SÍMBOLOS ===")
        for nome, tipo in self.symbol_table.items():
            print(f"Nome: {nome:<10} Tipo: {tipo}")
        print("==========================")
        return self.code_segment

    def bloco(self):
        self.expect("SEPARATOR", "{")
        while self.token is not None and not self.match("SEPARATOR", "}"):
            self.comando()
        if self.token is None:
            self.error("Bloco não fechado no final do arquivo")
            return
        self.expect("SEPARATOR", "}")

    def comando(self):
        if self.match("IF"):
            self.condicao()
        elif self.match("WHILE"):
            self.repeticao()
        elif self.match("FOR"):
            self.laco_for()
        elif self.token is not None and self.token.type in ("INT", "FLOAT", "STRING", "CHAR", "BOOL"):
            self.declaracao()
        elif self.match("IDENTIFIER"):
            next_token = self.peek()
            if next_token and next_token.type == "OPERATOR" and next_token.value == "=":
                self.atribuicao()
            else:
                reg, tipo = self.expressao()
                self.free_reg(reg)
                self.expect("SEPARATOR", ";")
        elif self.match("SEPARATOR", "("):
            reg, tipo = self.expressao()
            self.free_reg(reg)
            self.expect("SEPARATOR", ";")
        else:
            self.error("Comando inválido")
            self.sync()

    def declaracao(self):
        tipo = self.token.type
        self.next_token()
        nome = self.token.value
        self.expect("IDENTIFIER")

        if nome in self.symbol_table:
            self.error(f"Variável '{nome}' já declarada")
        else:
            self.symbol_table[nome] = tipo
            tipo_asm = ".byte 0" if tipo in ["CHAR", "BOOL"] else ".word 0"
            self.data_segment.append(f"{nome}: {tipo_asm}")

        if self.match("OPERATOR", "="):
            self.next_token()
            reg_expr, tipo_expr = self.expressao()
            
            if tipo != tipo_expr:
                self.error(f"Incompatibilidade de tipos: {tipo} recebe {tipo_expr}")
            
            inst = "sb" if tipo in ["CHAR", "BOOL"] else "sw"
            self.emit(f"{inst} {reg_expr}, {nome}")
            self.free_reg(reg_expr)

        self.expect("SEPARATOR", ";")

    def condicao(self):
        self.expect("IF")
        self.expect("SEPARATOR", "(")
        cond_reg, tipo = self.expressao()
        self.expect("SEPARATOR", ")")
        
        label_else = self.new_label() + "_else"
        label_fim = self.new_label() + "_fim_if"
        
        self.emit(f"beqz {cond_reg}, {label_else}")
        self.free_reg(cond_reg)
        
        self.bloco()
        
        if self.match("ELSE"):
            self.emit(f"j {label_fim}")
            self.emit(f"{label_else}:")
            self.next_token()
            self.bloco()
            self.emit(f"{label_fim}:")
        else:
            self.emit(f"{label_else}:")

    def repeticao(self):
        self.expect("WHILE")
        self.expect("SEPARATOR", "(")
        
        label_comeco = self.new_label() + "_while_start"
        label_fim = self.new_label() + "_while_end"
        
        self.emit(f"{label_comeco}:")
        
        cond_reg, tipo = self.expressao()
        self.expect("SEPARATOR", ")")
        
        self.emit(f"beqz {cond_reg}, {label_fim}")
        self.free_reg(cond_reg)
        
        self.bloco()
        
        self.emit(f"j {label_comeco}")
        self.emit(f"{label_fim}:")

    def laco_for(self):
        self.expect("FOR")
        self.expect("SEPARATOR", "(")
        
        if self.token.type in ["INT", "FLOAT", "CHAR", "BOOL"]:
            self.declaracao()
        else:
            self.atribuicao()
            
        label_comeco = self.new_label() + "_for_start"
        label_fim = self.new_label() + "_for_end"
        
        self.emit(f"{label_comeco}:")
        
        cond_reg, tipo_cond = self.expressao()
        self.expect("SEPARATOR", ";")
        
        self.emit(f"beqz {cond_reg}, {label_fim}")
        self.free_reg(cond_reg)
        
        while not self.match("SEPARATOR", ")"):
            self.next_token()
        self.expect("SEPARATOR", ")")
        
        self.bloco()
        
        self.emit(f"j {label_comeco}")
        self.emit(f"{label_fim}:")

    def atribuicao(self):
        left = self.token.value
        self.expect("IDENTIFIER")
        self.expect("OPERATOR", "=")

        reg_expr, tipo_expr = self.expressao()
        self.expect("SEPARATOR", ";")

        if left in self.symbol_table:
            tipo_variavel = self.symbol_table[left]
            if tipo_variavel != tipo_expr:
                self.error(f"Incompatibilidade de tipos: {tipo_variavel} recebe {tipo_expr}")
            
            inst = "sb" if tipo_variavel in ["CHAR", "BOOL"] else "sw"
            self.emit(f"{inst} {reg_expr}, {left}")
        else:
            self.error(f"Variável '{left}' não declarada")

        self.free_reg(reg_expr)

    def expressao(self):
        return self.rel()

    def rel(self):
        left_reg, left_type = self.soma()
        
        while self.match("OPERATOR") and self.token.value in ["==", "!=", "<", ">", "<=", ">="]:
            op = self.token.value
            self.next_token()
            right_reg, right_type = self.soma()
            
            if op == "==": self.emit(f"seq {left_reg}, {left_reg}, {right_reg}")
            elif op == "!=": self.emit(f"sne {left_reg}, {left_reg}, {right_reg}")
            elif op == "<": self.emit(f"slt {left_reg}, {left_reg}, {right_reg}")
            elif op == "<=": self.emit(f"sle {left_reg}, {left_reg}, {right_reg}")
            elif op == ">": self.emit(f"sgt {left_reg}, {left_reg}, {right_reg}")
            elif op == ">=": self.emit(f"sge {left_reg}, {left_reg}, {right_reg}")
                
            self.free_reg(right_reg)
            left_type = "BOOL"
            
        return left_reg, left_type

    def soma(self):
        left_reg, left_type = self.termo()
        
        while self.match("OPERATOR") and self.token.value in ["+", "-"]:
            op = self.token.value
            self.next_token()
            right_reg, right_type = self.termo()
                
            if op == "+": self.emit(f"add {left_reg}, {left_reg}, {right_reg}")
            else: self.emit(f"sub {left_reg}, {left_reg}, {right_reg}")
                
            self.free_reg(right_reg)
        return left_reg, left_type

    def termo(self):
        left_reg, left_type = self.fator()
        
        while self.match("OPERATOR") and self.token.value in ["*", "/"]:
            op = self.token.value
            self.next_token()
            right_reg, right_type = self.fator()
                
            if op == "*": 
                self.emit(f"mul {left_reg}, {left_reg}, {right_reg}")
            else: 
                self.emit(f"div {left_reg}, {right_reg}")
                self.emit(f"mflo {left_reg}")
                
            self.free_reg(right_reg)
        return left_reg, left_type
    
    def fator(self):
        if self.match("SEPARATOR", "("):
            self.next_token()
            reg, tipo = self.expressao()
            self.expect("SEPARATOR", ")")
            return reg, tipo
            
        elif self.match("NUMBER"):
            value = self.token.value
            self.next_token()
            tipo = "FLOAT" if "." in value else "INT"
            reg = self.get_reg()
            self.emit(f"li {reg}, {value}")
            return reg, tipo
            
        elif self.match("IDENTIFIER"):
            nome = self.token.value
            tipo = self.symbol_table.get(nome, "ERROR")
            self.next_token()
            reg = self.get_reg()
            
            inst = "lb" if tipo in ["CHAR", "BOOL"] else "lw"
            self.emit(f"{inst} {reg}, {nome}")
            return reg, tipo
            
        elif self.match("LITERAL"):
            valor = self.token.value
            self.next_token()
            tipo = "STRING" if valor.startswith('"') else "CHAR"
            reg = self.get_reg()
            return reg, tipo
            
        else:
            self.error("Esperado expressão válida")
            self.next_token()
            return self.get_reg(), "ERROR"

    def peek(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None