# MiniLang — Design Your Own Programming Language

A small educational programming language built in Python. It demonstrates the main compiler-design stages:
1. Lexical analysis (tokenizer)
2. Syntax analysis (recursive-descent parser)
3. CFG-based grammar
4. Abstract syntax tree (AST)
5. Interpretation / execution
6. Basic error reporting

## Requirements
- Python 3.8 or later
- No third-party packages

## Run
```bash
python minilang.py example.mini
```

## MiniLang features
- Variables: `let score = 10;`
- Assignment: `score = score + 2;`
- Output: `print(score);`
- Arithmetic: `+ - * /` and unary minus
- Comparisons: `== != < > <= >=`
- Conditional: `if (...) { ... } else { ... }`
- Loop: `while (...) { ... }`
- Numbers, strings, and Boolean values (`true`, `false`)

## Example
```text
let x = 10;
let y = 20;
let result = x + y;
print(result);
```

## Design note
This is an interpreter for a custom language rather than a native machine-code compiler. It still demonstrates compiler construction fundamentals: source text is converted to tokens, tokens are parsed according to a context-free grammar, an AST is built, and the AST is executed.

## Limitations
- No functions, arrays, user input, or static type checker.
- No comments in source programs.
- Variables use a single global scope.
- Error messages are educational/basic rather than production-grade.
