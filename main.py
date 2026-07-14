from lexerForC import Lexer
from parserAndAnaSemForC import Parser

print("=== LENDO O ARQUIVO ===\n")
with open("entrada.txt", "r", encoding="utf-8") as file:
    code = file.read()

print(code)
print("\n" + "="*30 + "\n")

lexer = Lexer(code)
tokens = lexer.tokenize()

print("=== INICIANDO COMPILADOR ===\n")
parser = Parser(tokens)

code_segment = parser.parse()

if not parser.errors and code_segment is not None:
    print("\nMontando arquivo Assembly final...")
    
    linhas_asm = [".data"]
    for decl in parser.data_segment:
        linhas_asm.append(f"    {decl}")
        
    linhas_asm.extend(["", ".text", ".globl main", "main:"])
    
    for inst in code_segment:
        if inst.endswith(":"):
            linhas_asm.append(inst)
        else:
            linhas_asm.append(f"    {inst}")
            
    linhas_asm.extend(["    li $v0, 10", "    syscall", ""])
    
    codigo_asm_final = "\n".join(linhas_asm)
    
    with open("saida.asm", "w", encoding="utf-8") as out_file:
        out_file.write(codigo_asm_final)
    
    print("[!] Código salvo com sucesso no arquivo 'saida.asm'!")
else:
    print("\n[X] Geração de arquivo Assembly abortada devido a erros de sintaxe ou semântica.")