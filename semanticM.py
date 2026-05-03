
from token import *

TYPE_KEYWORDS = {'int', 'float', 'string', 'double', 'bool', 'char'}


class SymbolTable:
    def __init__(self):
        self.table = {}  

    def insert(self, name, declared_type, line):
        self.table[name] = {'type': declared_type, 'line': line}

    def lookup(self, name):
        return self.table.get(name, None)

    def exists(self, name):
        return name in self.table

    def all_entries(self):
        return self.table.items()

    def __repr__(self):
        rows = [f"  {'Name':<15} {'Type':<10} {'Declared Line'}"]
        rows.append("  " + "-" * 38)
        for name, info in self.table.items():
            rows.append(f"  {name:<15} {info['type']:<10} {info['line']}")
        return "\n".join(rows)



def analyze(tokens):
    symbol_table = SymbolTable()
    errors = []
    i = 0
    n = len(tokens)

    def at(offset=0):
        idx = i + offset
        return tokens[idx] if idx < n else None

    def scan_to_semicolon(start):
        j = start
        while j < n and tokens[j].token_type != TOK_SEMICOLON:
            j += 1
        return j

    def check_expr_identifiers(start, end):
        for j in range(start, end):
            tok = tokens[j]
            if tok.token_type == TOK_IDENTIFIER:
                if not symbol_table.exists(tok.lexeme):
                    errors.append(
                        f"Line {tok.line}: Undeclared variable '{tok.lexeme}' used in expression."
                    )

    while i < n:
        tok = at()

        if tok.token_type in (TOK_SCOMMENT, TOK_MCOMMENT):
            i += 1
            continue

        # ── DECLARATION:  TYPE IDENTIFIER = expr ;
        if tok.token_type == TOK_IDENTIFIER and tok.lexeme in TYPE_KEYWORDS:
            decl_type = tok.lexeme
            name_tok = at(1)

            if name_tok is None or name_tok.token_type != TOK_IDENTIFIER:
                errors.append(f"Line {tok.line}: Expected variable name after '{decl_type}'.")
                i += 1
                continue

            # double-declaration check via lookup
            existing = symbol_table.lookup(name_tok.lexeme)
            if existing:
                errors.append(
                    f"Line {name_tok.line}: Variable '{name_tok.lexeme}' already declared "
                    f"on line {existing['line']} as '{existing['type']}'."
                )
            else:
                symbol_table.insert(name_tok.lexeme, decl_type, name_tok.line)

            eq_tok = at(2)
            if eq_tok is None or eq_tok.token_type != TOK_ASSIGN:
                errors.append(f"Line {name_tok.line}: Expected '=' after '{name_tok.lexeme}'.")
                semi = scan_to_semicolon(i + 2)
                i = semi + 1
                continue

            semi = scan_to_semicolon(i + 3)
            check_expr_identifiers(i + 3, semi)

            if semi >= n:
                errors.append(f"Line {tok.line}: Missing ';' after declaration of '{name_tok.lexeme}'.")

            i = semi + 1
            continue

        # ── ASSIGNMENT:  IDENTIFIER = expr ;
        if tok.token_type == TOK_IDENTIFIER:
            eq_tok = at(1)
            if eq_tok is not None and eq_tok.token_type == TOK_ASSIGN:

                if not symbol_table.exists(tok.lexeme):
                    errors.append(
                        f"Line {tok.line}: Variable '{tok.lexeme}' used before declaration."
                    )

                semi = scan_to_semicolon(i + 2)
                check_expr_identifiers(i + 2, semi)

                if semi >= n:
                    errors.append(f"Line {tok.line}: Missing ';' in assignment to '{tok.lexeme}'.")

                i = semi + 1
                continue

        i += 1

    return symbol_table, errors


# ── QUICK TEST ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    from lexer import lexer

    source = """
int x = 0 ;
int y = 4 ;
x = 2 * y ;
z = 5 ;
int x = 99 ;
int w = z + 1 ;
"""

    tokens = lexer(source).tokenize()
    sym_table, errors = analyze(tokens)

    print("Symbol Table:")
    print(sym_table)

    print("\nErrors:")
    if errors:
        for e in errors:
            print(f"  ❌ {e}")
    else:
        print("  ✅ No semantic errors.")