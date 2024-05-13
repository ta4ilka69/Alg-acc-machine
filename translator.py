import sys

from isa import BITMASK, TEMPORARY_MEMORY_ADDRESS, AddressingMode, Opcode, write_code

OPERATIONS = {"+": Opcode.ADD, "-": Opcode.SUB, "*": Opcode.MUL, "/": Opcode.DIV, "%": Opcode.MOD}


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
        elif line.startswith("print"):
            sentence = line.split("(")[1].split(")")[0]
            statements.append({"name": "print", "sentence": sentence})
            i += 1
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
        if line.startswith("while") or line.startswith("if"):
            condition = line.split("(")[1].split(")")[0]
            inner_statements, i = parse_block(lines, i + 1)
            statements.append(
                {
                    "name": "if" if line.split()[0].startswith("if") else "while",
                    "condition": condition,
                    "statements": inner_statements,
                }
            )
        elif line.startswith("print"):
            sentence = line.split("(")[1].split(")")[0]
            statements.append({"name": "print", "sentence": sentence})
            i += 1
        elif line.startswith("}"):
            i += 1
            break
        else:
            statements.append(line)
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


def translate_expression_to_polish(expression):  # noqa: C901
    output = []
    operator_stack = []
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2}
    i = 0
    while i < len(expression):
        char = expression[i]

        if char.isalnum():
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
            operator_stack.pop()
        elif char in precedence:
            while operator_stack and operator_stack[-1] != "(" and precedence[char] <= precedence[operator_stack[-1]]:
                output.append(operator_stack.pop())
            operator_stack.append(char)
        i += 1

    while operator_stack:
        output.append(operator_stack.pop())
    return output


def translate_expression(expression, data, code, next_available_memory):
    polish_notation = translate_expression_to_polish(expression)
    stack_last = TEMPORARY_MEMORY_ADDRESS
    for token in polish_notation:
        if token in "+-*/%":
            opcode = OPERATIONS[token]
            stack_last += 1
            code.append(
                {
                    "opcode": Opcode.LD,
                    "arg": stack_last + 1,
                    "addressing_mode": AddressingMode.ABSOLUTE,
                    "index": len(code),
                }
            )
            code.append(
                {
                    "opcode": opcode,
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
                    "index": len(code),
                }
            )
            stack_last -= 1
    return code, data, next_available_memory


def _declare_variable(data, variable_name, variable_type, next_available_memory):
    assert variable_type in ["int", "char"], f"Invalid data type: {variable_type}"
    if variable_name not in data:
        data[variable_name] = next_available_memory
        next_available_memory += 1
    return data, next_available_memory


def _handle_assignment(code, data, variable_name, expression, next_available_memory):
    code, data, next_available_memory = translate_expression(expression, data, code, next_available_memory)
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
            "index": len(code),
        }
    )
    return code, data, next_available_memory


def _handle_input(code, data, variable_name):
    code.append({"opcode": Opcode.IN, "index": len(code)})
    code.append(
        {
            "opcode": Opcode.ST,
            "arg": data[variable_name],
            "index": len(code),
        }
    )
    return code, data


def translate_string(code, data, sentence, next_available_memory):
    parts = sentence.replace(";", "").split("=")
    variable_type = parts[0].strip().split()[0]

    if len(parts[0].strip().split()) > 1:
        variable_name = parts[0].strip().split()[1]
        data, next_available_memory = _declare_variable(data, variable_name, variable_type, next_available_memory)

        if len(parts) == 2:
            if variable_type == "int":
                expression = parts[1].strip()
                code, data, next_available_memory = _handle_assignment(
                    code, data, variable_name, expression, next_available_memory
                )
            elif variable_type == "char":
                if "input()" in parts[1]:
                    code, data = _handle_input(code, data, variable_name)
                else:
                    assert parts[1].strip() in data, f"Unsupported operation for char type: {sentence}"
                    code, data, next_available_memory = _handle_assignment(
                        code, data, variable_name, parts[1].strip(), next_available_memory
                    )

        return code, data, next_available_memory

    variable_name = variable_type
    if len(parts) == 2:
        assert variable_name in data, f"Variable {variable_name} not found"
        expression = parts[1].strip()
        if "input()" in expression:
            code, data = _handle_input(code, data, variable_name)
        else:
            code, data, next_available_memory = _handle_assignment(
                code, data, variable_name, expression, next_available_memory
            )
    else:
        code, data, next_available_memory = translate_expression(parts[0].strip(), data, code, next_available_memory)
    return code, data, next_available_memory


def translate_while(code, data, sentence, next_available_memory, jump_stack):
    condition, sentences = sentence["condition"], sentence["statements"]
    start = len(code)
    if condition.startswith("!"):
        code, data, next_available_memory = translate_string(code, data, condition[1:], next_available_memory)
        code.append(
            {
                "opcode": Opcode.LD,
                "arg": TEMPORARY_MEMORY_ADDRESS,
                "addressing_mode": AddressingMode.ABSOLUTE,
                "index": len(code),
            }
        )
        code.append({"opcode": Opcode.JNZ, "index": len(code)})
    else:
        code, data, next_available_memory = translate_string(code, data, condition, next_available_memory)
        code.append(
            {
                "opcode": Opcode.LD,
                "arg": TEMPORARY_MEMORY_ADDRESS,
                "addressing_mode": AddressingMode.ABSOLUTE,
                "index": len(code),
            }
        )
        code.append({"opcode": Opcode.JZ, "index": len(code)})
    jump_stack.append(len(code) - 1)
    for sentence_deep in sentences:
        code, data, next_available_memory, jump_stack = translate_sentence(
            code, data, sentence_deep, next_available_memory, jump_stack
        )
    code.append({"opcode": Opcode.JMP, "arg": start, "index": len(code)})
    code[jump_stack[-1]]["arg"] = len(code)
    jump_stack.pop()
    return code, data, next_available_memory, jump_stack


def translate_if(code, data, sentence, next_available_memory, jump_stack):
    condition, sentences = sentence["condition"], sentence["statements"]
    if condition.startswith("!"):
        code, data, next_available_memory = translate_string(code, data, condition[1:], next_available_memory)
        code.append(
            {
                "opcode": Opcode.LD,
                "arg": TEMPORARY_MEMORY_ADDRESS,
                "addressing_mode": AddressingMode.ABSOLUTE,
                "index": len(code),
            }
        )
        code.append({"opcode": Opcode.JZ, "arg": len(code) + 2, "index": len(code)})
    else:
        code, data, next_available_memory = translate_string(code, data, condition, next_available_memory)
        code.append(
            {
                "opcode": Opcode.LD,
                "arg": TEMPORARY_MEMORY_ADDRESS,
                "addressing_mode": AddressingMode.ABSOLUTE,
                "index": len(code),
            }
        )
        code.append({"opcode": Opcode.JNZ, "arg": len(code) + 2, "index": len(code)})
    code.append({"opcode": Opcode.JMP, "index": len(code)})
    jump_stack.append(len(code) - 1)
    for sentence_deep in sentences:
        code, data, next_available_memory, jump_stack = translate_sentence(
            code, data, sentence_deep, next_available_memory, jump_stack
        )
    code[jump_stack[-1]]["arg"] = len(code)
    jump_stack.pop()
    return code, data, next_available_memory, jump_stack


def translate_print_arg(code, data, sentence, next_available_memory):
    if (sentence.startswith('"') and sentence.endswith('"')) or (sentence.startswith("'") and sentence.endswith("'")):
        ind = len(data["print"])
        sentence = sentence[1:-1]
        data["print"].append({"start": next_available_memory, "chars": [len(sentence)]})
        next_available_memory += 1
        for char in sentence:
            data["print"][ind]["chars"].append(ord(char))
            next_available_memory += 1
        code.append(
            {
                "opcode": Opcode.LD,
                "arg": data["print"][ind]["start"] + 1,
                "addressing_mode": AddressingMode.DIRECT,
                "index": len(code),
            }
        )
        code.append(
            {
                "opcode": Opcode.ST,
                "arg": TEMPORARY_MEMORY_ADDRESS - 1,
                "index": len(code),
            }
        )
        code.append(
            {
                "opcode": Opcode.LD,
                "arg": data["print"][ind]["start"],
                "addressing_mode": AddressingMode.ABSOLUTE,
                "index": len(code),
            }
        )
        code.append(
            {
                "opcode": Opcode.ST,
                "arg": TEMPORARY_MEMORY_ADDRESS,
                "index": len(code),
            }
        )
        start = len(code)
        code.append(
            {
                "opcode": Opcode.LD,
                "arg": TEMPORARY_MEMORY_ADDRESS,
                "addressing_mode": AddressingMode.ABSOLUTE,
                "index": start,
            }
        )
        jz = len(code)
        code.append(
            {
                "opcode": Opcode.JZ,
                "index": jz,
            }
        )
        code.append(
            {
                "opcode": Opcode.LD,
                "arg": TEMPORARY_MEMORY_ADDRESS - 1,
                "addressing_mode": AddressingMode.RELATIVE,
                "index": len(code),
            }
        )
        code.append(
            {
                "opcode": Opcode.OUT,
                "index": len(code),
            }
        )
        code.append(
            {
                "opcode": Opcode.LD,
                "arg": TEMPORARY_MEMORY_ADDRESS - 1,
                "addressing_mode": AddressingMode.ABSOLUTE,
                "index": len(code),
            }
        )
        code.append(
            {
                "opcode": Opcode.INC,
                "index": len(code),
            }
        )
        code.append(
            {
                "opcode": Opcode.ST,
                "arg": TEMPORARY_MEMORY_ADDRESS - 1,
                "index": len(code),
            }
        )
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
                "opcode": Opcode.DEC,
                "index": len(code),
            }
        )
        code.append(
            {
                "opcode": Opcode.ST,
                "arg": TEMPORARY_MEMORY_ADDRESS,
                "index": len(code),
            }
        )
        code.append(
            {
                "opcode": Opcode.JMP,
                "arg": start,
                "index": len(code),
            }
        )
        code[jz]["arg"] = len(code)
        return code, data, next_available_memory
    code, data, next_available_memory = translate_expression(sentence, data, code, next_available_memory)
    code.append(
        {
            "opcode": Opcode.LD,
            "arg": TEMPORARY_MEMORY_ADDRESS,
            "addressing_mode": AddressingMode.ABSOLUTE,
            "index": len(code),
        }
    )
    code.append({"opcode": Opcode.OUT, "index": len(code)})
    return code, data, next_available_memory


def translate_print(code, data, sentence, next_available_memory):
    return translate_print_arg(code, data, sentence, next_available_memory)


def translate_sentence(code, data, sentence, next_available_memory, jump_stack):
    if isinstance(sentence, str) and sentence not in ["", "{", "}"]:
        code, data, next_available_memory = translate_string(code, data, sentence, next_available_memory)
    elif isinstance(sentence, dict):
        if sentence["name"] == "while":
            code, data, next_available_memory, jump_stack = translate_while(
                code, data, sentence, next_available_memory, jump_stack
            )
        elif sentence["name"] == "if":
            code, data, next_available_memory, jump_stack = translate_if(
                code, data, sentence, next_available_memory, jump_stack
            )
        elif sentence["name"] == "print":
            code, data, next_available_memory = translate_print(code, data, sentence["sentence"], next_available_memory)
    return code, data, next_available_memory, jump_stack


def translate(text):
    sentences = text2sentences(text)
    code = []
    data = {"print": []}
    jump_stack = []
    next_available_memory = 0
    for sentence in sentences:
        if sentence in ["", "{", "}"]:
            continue
        code, data, next_available_memory, jump_stack = translate_sentence(
            code, data, sentence, next_available_memory, jump_stack
        )
    code.append({"opcode": Opcode.HLT, "index": len(code)})
    return code, data


def main(source, target):
    with open(source) as f:
        source = f.read()
    code, data = translate(source)
    write_code(code, data["print"], target)
    print("source LoC:", len(source.split("\n")), "code instr:", len(code))


if __name__ == "__main__":
    # assert len(sys.argv) == 3, "Wrong arguments: translator <input_file> <target_file>"
    # _, source, target = sys.argv
    source = "./examples/hello_user_alg.js"
    target = "./examples/hello_user_alg_out.txt"
    main(source, target)
