"""
MiniLang: a small educational programming language.
Run: python minilang.py program.mini
"""
import re
import sys

TOKEN_SPEC = [
    ("NUMBER",   r"\d+(?:\.\d+)?"),
    ("STRING",   r'"(?:\\.|[^"\\])*"'),
    ("ID",       r"[A-Za-z_][A-Za-z0-9_]*"),
    ("EQ",       r"=="), ("NE", r"!="), ("LE", r"<="), ("GE", r">="),
    ("ASSIGN",   r"="), ("LT", r"<"), ("GT", r">"),
    ("PLUS",     r"\+"), ("MINUS", r"-"), ("STAR", r"\*"), ("SLASH", r"/"),
    ("LPAREN",   r"\("), ("RPAREN", r"\)"),
    ("LBRACE",   r"\{"), ("RBRACE", r"\}"),
    ("SEMI",     r";"), ("COMMA", r","),
    ("NEWLINE",  r"\n"), ("SKIP", r"[ \t\r]+"),
    ("MISMATCH", r"."),
]
TOKEN_RE = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))
KEYWORDS = {"let", "print", "if", "else", "while", "true", "false"}

class MiniLangError(Exception):
    pass

def tokenize(source):
    tokens = []
    line = 1
    for match in TOKEN_RE.finditer(source):
        kind, value = match.lastgroup, match.group()
        if kind == "NEWLINE":
            line += 1
        elif kind in ("SKIP",):
            continue
        elif kind == "MISMATCH":
            raise MiniLangError(f"Unexpected character {value!r} on line {line}")
        else:
            if kind == "ID" and value in KEYWORDS:
                kind = value.upper()
            tokens.append((kind, value, line))
    tokens.append(("EOF", "", line))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens, self.pos = tokens, 0

    def current(self):
        return self.tokens[self.pos]

    def check(self, kind):
        return self.current()[0] == kind

    def advance(self):
        token = self.current()
        if not self.check("EOF"):
            self.pos += 1
        return token

    def expect(self, kind):
        if not self.check(kind):
            got = self.current()
            raise MiniLangError(f"Line {got[2]}: expected {kind}, got {got[1]!r}")
        return self.advance()

    def parse(self):
        statements = []
        while not self.check("EOF"):
            statements.append(self.statement())
        return ("block", statements)

    def statement(self):
        if self.check("LET"):
            self.advance()
            name = self.expect("ID")[1]
            self.expect("ASSIGN")
            value = self.expression()
            self.expect("SEMI")
            return ("let", name, value)
        if self.check("PRINT"):
            self.advance()
            self.expect("LPAREN")
            value = self.expression()
            self.expect("RPAREN")
            self.expect("SEMI")
            return ("print", value)
        if self.check("IF"):
            self.advance()
            self.expect("LPAREN")
            condition = self.expression()
            self.expect("RPAREN")
            then_branch = self.block()
            else_branch = None
            if self.check("ELSE"):
                self.advance()
                else_branch = self.block()
            return ("if", condition, then_branch, else_branch)
        if self.check("WHILE"):
            self.advance()
            self.expect("LPAREN")
            condition = self.expression()
            self.expect("RPAREN")
            return ("while", condition, self.block())
        if self.check("ID"):
            name = self.advance()[1]
            self.expect("ASSIGN")
            value = self.expression()
            self.expect("SEMI")
            return ("assign", name, value)
        raise MiniLangError(f"Line {self.current()[2]}: invalid statement near {self.current()[1]!r}")

    def block(self):
        self.expect("LBRACE")
        statements = []
        while not self.check("RBRACE"):
            if self.check("EOF"):
                raise MiniLangError("Unclosed block: expected '}'")
            statements.append(self.statement())
        self.expect("RBRACE")
        return ("block", statements)

    def expression(self):
        return self.equality()

    def equality(self):
        node = self.comparison()
        while self.check("EQ") or self.check("NE"):
            op = self.advance()[1]
            node = ("binary", op, node, self.comparison())
        return node

    def comparison(self):
        node = self.term()
        while self.check("LT") or self.check("GT") or self.check("LE") or self.check("GE"):
            op = self.advance()[1]
            node = ("binary", op, node, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.check("PLUS") or self.check("MINUS"):
            op = self.advance()[1]
            node = ("binary", op, node, self.factor())
        return node

    def factor(self):
        node = self.unary()
        while self.check("STAR") or self.check("SLASH"):
            op = self.advance()[1]
            node = ("binary", op, node, self.unary())
        return node

    def unary(self):
        if self.check("MINUS"):
            self.advance()
            return ("unary", "-", self.unary())
        return self.primary()

    def primary(self):
        if self.check("NUMBER"):
            raw = self.advance()[1]
            return ("literal", float(raw) if "." in raw else int(raw))
        if self.check("STRING"):
            raw = self.advance()[1]
            return ("literal", bytes(raw[1:-1], "utf-8").decode("unicode_escape"))
        if self.check("TRUE"):
            self.advance()
            return ("literal", True)
        if self.check("FALSE"):
            self.advance()
            return ("literal", False)
        if self.check("ID"):
            return ("variable", self.advance()[1])
        if self.check("LPAREN"):
            self.advance()
            node = self.expression()
            self.expect("RPAREN")
            return node
        token = self.current()
        raise MiniLangError(f"Line {token[2]}: expected an expression, got {token[1]!r}")

class Interpreter:
    def __init__(self):
        self.env = {}

    def evaluate(self, node):
        kind = node[0]
        if kind == "literal":
            return node[1]
        if kind == "variable":
            name = node[1]
            if name not in self.env:
                raise MiniLangError(f"Undefined variable: {name}")
            return self.env[name]
        if kind == "unary":
            return -self.evaluate(node[2])
        if kind == "binary":
            op, left_node, right_node = node[1], node[2], node[3]
            left, right = self.evaluate(left_node), self.evaluate(right_node)
            operations = {
                "+": lambda: left + right, "-": lambda: left - right,
                "*": lambda: left * right, "/": lambda: left / right,
                "==": lambda: left == right, "!=": lambda: left != right,
                "<": lambda: left < right, ">": lambda: left > right,
                "<=": lambda: left <= right, ">=": lambda: left >= right,
            }
            try:
                return operations[op]()
            except ZeroDivisionError:
                raise MiniLangError("Division by zero")
            except TypeError:
                raise MiniLangError(f"Incompatible values for operator {op}")
        raise MiniLangError("Invalid expression node")

    def execute(self, node):
        kind = node[0]
        if kind == "block":
            for statement in node[1]:
                self.execute(statement)
        elif kind == "let":
            name, expression = node[1], node[2]
            if name in self.env:
                raise MiniLangError(f"Variable already declared: {name}")
            self.env[name] = self.evaluate(expression)
        elif kind == "assign":
            name, expression = node[1], node[2]
            if name not in self.env:
                raise MiniLangError(f"Cannot assign to undeclared variable: {name}")
            self.env[name] = self.evaluate(expression)
        elif kind == "print":
            print(self.evaluate(node[1]))
        elif kind == "if":
            condition = self.evaluate(node[1])
            self.execute(node[2] if condition else (node[3] or ("block", [])))
        elif kind == "while":
            count = 0
            while self.evaluate(node[1]):
                self.execute(node[2])
                count += 1
                if count > 100000:
                    raise MiniLangError("Loop safety limit exceeded")
        else:
            raise MiniLangError("Invalid statement")

def run(source):
    tokens = tokenize(source)
    tree = Parser(tokens).parse()
    Interpreter().execute(tree)

def main():
    if len(sys.argv) != 2:
        print("Usage: python minilang.py <program.mini>")
        raise SystemExit(1)
    try:
        with open(sys.argv[1], "r", encoding="utf-8") as file:
            run(file.read())
    except (MiniLangError, OSError) as error:
        print(f"MiniLang error: {error}", file=sys.stderr)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
