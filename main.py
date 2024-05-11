class Statement:
    def __init__(self, statement):
        self.statement = statement

class WhileStatement:
    def __init__(self, condition):
        self.condition = condition
        self.statements = []

    def add_statement(self, statement):
        self.statements.append(statement)

class IfStatement:
    def __init__(self, condition):
        self.condition = condition
        self.statements = []

    def add_statement(self, statement):
        self.statements.append(statement)

# Example usage
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

# Splitting the code into individual statements
statements = code.split(';')
statements = [s.strip() for s in statements if s.strip()]  # Remove empty strings

# Parsing statements into objects
parsed_statements = []
for s in statements:
    if s.startswith("while"):
        condition = s.split('(')[1].split(')')[0]
        while_statement = WhileStatement(condition)
        parsed_statements.append(while_statement)
    elif s.startswith("if"):
        condition = s.split('(')[1].split(')')[0]
        if_statement = IfStatement(condition)
        parsed_statements.append(if_statement)
    else:
        parsed_statements.append(Statement(s))

# Printing parsed statements
for statement in parsed_statements:
    if isinstance(statement, WhileStatement):
        print("while ({})".format(statement.condition))
        for sub_statement in statement.statements:
            print("\t{}".format(sub_statement.statement))
    elif isinstance(statement, IfStatement):
        print("if ({})".format(statement.condition))
        for sub_statement in statement.statements:
            print("\t{}".format(sub_statement.statement))
    else:
        print(statement.statement)
