# Архитектура компьютера. Лабораторная работа №3

- Балин Артем Алексеевич, P3212
- alg| acc | harv | hw | instr | struct | stream | port | cstr | prob1 |
- Базовый вариант (без усложнения)

## Язык программирования

Синтаксис в расширенной БНФ.

```ebnf
program ::= sentence { sentence }

sentence ::= simple_sentence
        | while_block
        | if_block
        | comment

simple_sentence ::= print_sentence
                    | declare_and_assign
                    | assign

assign ::= char_assign | int_assign

char_assign ::= variable_name "=input()"

int_assign ::= variable_name "=" math_equathion

print_sentence ::= print_string | print_char

print_string ::= "print(" string ")"

string ::= "\"" { <any symbol except "\t \n"> } "\""
         | "\'" { <any symbol except "\t \n"> } "\'"

print_char ::= "print(" variable_name ")"

comment ::= "//" { <any symbol except "\n"> }

variable_name ::= variable_name ::= <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }

math_equation ::= term { ("+" | "-") term }

term ::= factor { ("*" | "/") factor }

factor ::= variable_name | integer | "(" math_equation ")"

integer ::= digit { digit }

digit ::= <any of "0-9">

declare_and_assign ::= "int" int_assign
                     | "char" char_assign

while_block ::= "while(" condition ")" "{" program "}"

if_block ::= "if(" condition ")" "{" program "}"

condition ::= math_equation
            | "!" math_equation

```

# here is diagram in svg:

<img src="./media/CU.svg">
<img src="./media/DP.svg">
