# MiniLang Context-Free Grammar (EBNF-style)

program       -> statement*
statement     -> "let" IDENTIFIER "=" expression ";"
               | IDENTIFIER "=" expression ";"
               | "print" "(" expression ")" ";"
               | "if" "(" expression ")" block ("else" block)?
               | "while" "(" expression ")" block
block         -> "{" statement* "}"

expression    -> equality
equality      -> comparison (("==" | "!=") comparison)*
comparison    -> term (("<" | ">" | "<=" | ">=") term)*
term          -> factor (("+" | "-") factor)*
factor        -> unary (("*" | "/") unary)*
unary         -> "-" unary | primary
primary       -> NUMBER | STRING | "true" | "false"
               | IDENTIFIER | "(" expression ")"
