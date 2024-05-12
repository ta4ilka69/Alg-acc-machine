import sys

from isa import BITMASK, MEMORY_SIZE, TEMPORARY_MEMORY_ADDRESS, AddressingMode, Opcode, write_code


def parse_code(code):
    statements = []
    lines = code.strip().split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("while"):
            condition = line.split("(")[1].split(")")[0]
            inner_statements, i = parse_block(lines, i + 1)
            statements.append(
                {
                    "name": "while",
                    "condition": condition,
                    "statements": inner_statements,
                }
            )
        elif line.startswith("if"):
            condition = line.split("(")[1].split(")")[0]
            inner_statements, i = parse_block(lines, i + 1)
            statements.append({"name": "if", "condition": condition, "statements": inner_statements})
        elif line.startswith("{") or line.endswith("}"):
            i += 1
        else:
            statements.append(line)
            i += 1
    return statements


def parse_block(lines, start_index):
    statements = []
    i = start_index
    while i < len(lines):
        line = lines[i].strip()
        if line.endswith(";"):
            statements.append(line[:-1])
            i += 1
        elif line.startswith("}"):
            break
        else:
            if line.startswith("while"):
                condition = line.split("(")[1].split(")")[0]
                inner_statements, i = parse_block(lines, i + 1)
                statements.append(
                    {
                        "name": "while",
                        "condition": condition,
                        "statements": inner_statements,
                    }
                )
            elif line.startswith("if"):
                condition = line.split("(")[1].split(")")[0]
                inner_statements, i = parse_block(lines, i + 1)
                statements.append(
                    {
                        "name": "if",
                        "condition": condition,
                        "statements": inner_statements,
                    }
                )
            i += 1
    return statements, i


def check_brakes(code):
    stack = []
    opening_braces = ["{", "(", "["]
    closing_braces = ["}", ")", "]"]
    brace_pairs = {"{": "}", "(": ")", "[": "]"}
    line_count = 1
    for char in code:
        if char == "\n":
            line_count += 1
        if char in opening_braces:
            stack.append((char, line_count))
        elif char in closing_braces:
            assert stack, f"Unexpected closing brace '{char}' at line {line_count}"
            top = stack.pop()
            assert brace_pairs[top[0]] == char, f"Mismatched braces '{top[0]}' and '{char}' at line {line_count}"
    assert not stack, f"Unclosed brace '{stack[-1][0]}' at line {stack[-1][1]}"
    return True


def text2sentences(text):
    check_brakes(text)
    return parse_code(text)


def translate_expression_to_polish(expression):
    output = []
    operator_stack = []
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2}

    i = 0
    while i < len(expression):
        char = expression[i]

        if char.isalnum():  # Operand
            j = i + 1
            while j < len(expression) and expression[j].isalnum():
                j += 1
            output.append(expression[i:j])
            i = j - 1
        elif char == "(":
            operator_stack.append(char)
        elif char == ")":
            while operator_stack[-1] != "(":
                output.append(operator_stack.pop())
            operator_stack.pop()  # Remove "("
        elif char in precedence:  # Operator
            while operator_stack and operator_stack[-1] != "(" and precedence[char] <= precedence[operator_stack[-1]]:
                output.append(operator_stack.pop())
            operator_stack.append(char)
        i += 1

    while operator_stack:
        output.append(operator_stack.pop())
    return output


def translate_expression(expression, data, code, next_available_memory):  # noqa: C901
    polish_notation = translate_expression_to_polish(expression)
    stack_last = TEMPORARY_MEMORY_ADDRESS
    for token in polish_notation:
        if token in "+-*/%":
            stack_last += 1
            code.append(
                {
                    "opcode": Opcode.LD,
                    "arg": stack_last+1,
                    "addressing_mode": AddressingMode.ABSOLUTE,
                    "index": len(code),
                }
            )
            if token == "+":
                code.append(
                    {
                        "opcode": Opcode.ADD,
                        "arg": stack_last,
                        "addressing_mode": AddressingMode.ABSOLUTE,
                        "index": len(code),
                    }
                )
            elif token == "-":
                code.append(
                    {
                        "opcode": Opcode.SUB,
                        "arg": stack_last,
                        "addressing_mode": AddressingMode.ABSOLUTE,
                        "index": len(code),
                    }
                )
            elif token == "*":
                code.append(
                    {
                        "opcode": Opcode.MUL,
                        "arg": stack_last,
                        "addressing_mode": AddressingMode.ABSOLUTE,
                        "index": len(code),
                    }
                )
            elif token == "/":
                code.append(
                    {
                        "opcode": Opcode.DIV,
                        "arg": stack_last,
                        "addressing_mode": AddressingMode.ABSOLUTE,
                        "index": len(code),
                    }
                )
            elif token == "%":
                code.append(
                    {
                        "opcode": Opcode.MOD,
                        "arg": stack_last,
                        "addressing_mode": AddressingMode.ABSOLUTE,
                        "index": len(code),
                    }
                )
            stack_last += 1
            code.append(
                {
                    "opcode": Opcode.ST,
                    "arg": stack_last,
                    "addressing_mode": AddressingMode.ABSOLUTE,
                    "index": len(code),
                }
            )
            stack_last -= 1
        elif token.isdigit():
            code.append(
                {
                    "opcode": Opcode.LD,
                    "arg": int(token) & BITMASK,
                    "addressing_mode": AddressingMode.DIRECT,
                    "index": len(code),
                }
            )
            code.append(
                {
                    "opcode": Opcode.ST,
                    "arg": stack_last,
                    "addressing_mode": AddressingMode.ABSOLUTE,
                    "index": len(code),
                }
            )
            stack_last -= 1
        else:
            code.append(
                {
                    "opcode": Opcode.LD,
                    "arg": data[token],
                    "addressing_mode": AddressingMode.ABSOLUTE,
                    "index": len(code),
                }
            )
            code.append(
                {
                    "opcode": Opcode.ST,
                    "arg": stack_last,
                    "addressing_mode": AddressingMode.ABSOLUTE,
                    "index": len(code),
                }
            )
            stack_last -= 1
    return data, code, next_available_memory


def translate_string(code, data, sentence, next_available_memory):
    parts = sentence.replace(";", "").split("=")
    variable_type = parts[0].strip().split()[0]
    variable_name = parts[0].strip().split()[1]
    assert variable_type in ["int", "char"], f"Invalid data type: {variable_type}"
    if variable_name not in data:
        data[variable_name] = next_available_memory
        next_available_memory += 1
    if variable_type == "int":
        expression = parts[1].strip()
        data, code, next_available_memory = translate_expression(expression, data, code, next_available_memory)
        code.append(
            {
                "opcode": Opcode.LD,
                "arg": TEMPORARY_MEMORY_ADDRESS,
                "addressing_mode": AddressingMode.ABSOLUTE,
                "index": len(code),
            }
        )
        code.append(
            {
                "opcode": Opcode.ST,
                "arg": data[variable_name],
                "addressing_mode": AddressingMode.ABSOLUTE,
                "index": len(code),
            }
        )
    elif variable_type == "char":
        assert "input()" in parts[1] or parts[1].strip() in data, f"Unsupported operation for char type: {sentence}"
        if "input()" in parts[1]:
            code.append(
                {
                    "opcode": Opcode.IN,
                    "index": len(code),
                }
            )
        else:
            code.append(
                {
                    "opcode": Opcode.LD,
                    "arg": data[parts[1].strip()],
                    "addressing_mode": AddressingMode.ABSOLUTE,
                    "index": len(code),
                }
            )
        code.append(
            {
                "opcode": Opcode.ST,
                "arg": data[variable_name],
                "addressing_mode": AddressingMode.ABSOLUTE,
                "index": len(code),
            }
        )
    return code, data, next_available_memory

def translate_while(code, data, sentence, next_available_memory):
    pass

def translate_if(code, data, sentence, next_available_memory):
    pass

def translate_sentence(code, data, sentence, next_available_memory):
    if isinstance(sentence, str):
        code, data, next_available_memory = translate_string(code, data, sentence, next_available_memory)
    elif isinstance(sentence, dict):
        if sentence["name"] == "while":
            pass
        elif sentence["name"] == "if":
            pass
    return code, data, next_available_memory


def translate(text):
    sentences = text2sentences(text)
    code = []
    data = {}
    next_available_memory = 0
    for sentence in sentences:
        code, data, next_available_memory = translate_sentence(code, data, sentence, next_available_memory)
    code.append({"opcode": Opcode.HLT, "index": len(code)})
    return code


def main(source, target):
    with open(source) as f:
        source = f.read()
    code = translate(source)
    write_code(target, code)
    print("source LoC:", len(source.split("\n")), "code instr:", len(code))


if __name__ == "__main__":
    # assert len(sys.argv) == 3, "Wrong arguments: translator <input_file> <target_file>"
    # _, source, target = sys.argv
    source = "./examples/test.js"
    target = "output.txt"
    main(source, target)
