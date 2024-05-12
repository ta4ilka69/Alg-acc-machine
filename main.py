def parse_code(code):
    statements = []
    lines = code.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('while'):
            condition = line.split('(')[1].split(')')[0]
            inner_statements, i = parse_block(lines, i+1)
            statements.append({
                'name': 'while',
                'condition': condition,
                'statements': inner_statements
            })
        elif line.startswith('if'):
            condition = line.split('(')[1].split(')')[0]
            inner_statements, i = parse_block(lines, i+1)
            statements.append({
                'name': 'if',
                'condition': condition,
                'statements': inner_statements
            })
        elif line.startswith('{') or line.endswith('}'):
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
        if line.endswith(';'):
            statements.append(line[:-1])  # Removing the ending semicolon
            i += 1
        elif line.startswith('}'):
            break
        else:
            # Nested control flow structure
            if line.startswith('while'):
                condition = line.split('(')[1].split(')')[0]
                inner_statements, i = parse_block(lines, i+1)
                statements.append({
                    'name': 'while',
                    'condition': condition,
                    'statements': inner_statements
                })
            elif line.startswith('if'):
                condition = line.split('(')[1].split(')')[0]
                inner_statements, i = parse_block(lines, i+1)
                statements.append({
                    'name': 'if',
                    'condition': condition,
                    'statements': inner_statements
                })
            i += 1
    return statements, i

# Example usage
code = """
char c = input();
int a = 5;
int b = a*5+6/2-3%2;
while(c){
    print(c);
    c = input();
    if(c == 'q'){
        break;
    }
}
print(b);
if(!b){
    print("bye!");
}
"""

parsed_code = parse_code(code)
print(parsed_code)