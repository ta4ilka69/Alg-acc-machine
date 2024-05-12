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
            statements.append(
                {"name": "if", "condition": condition, "statements": inner_statements}
            )
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
            assert (
                brace_pairs[top[0]] == char
            ), f"Mismatched braces '{top[0]}' and '{char}' at line {line_count}"
    assert not stack, f"Unclosed brace '{stack[-1][0]}' at line {stack[-1][1]}"
    return True


def text2sentences(text):
    check_brakes(text)
    return parse_code(text)

code = """
char c = input();
int a = 5;
int b = a*5+6/2-3%2;
while(c){
    print(c);
    c = input();
}
print(b);
if(!b){
    print("bye!");
}
"""
print(text2sentences(code))
