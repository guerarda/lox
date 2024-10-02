BASE_CLASS = "Expression"
VISITOR_CLASS = "Visitor"

EXPRESSIONS = {
    "Binary": ["left", "operator", "right"],
    "Grouping": ["expression"],
    "Literal": ["value"],
    "Unary": ["operator", "right"],
}


def generate_base_class():
    str = f"class {BASE_CLASS}:\n"
    str += f"\tdef accept(self, _{VISITOR_CLASS.lower()}):\n"
    str += "\t\traise NotImplementedError()\n\n\n"

    return str


def generate_expression(name, fields):

    # Generate class name
    str = f"class {name}({BASE_CLASS}):\n"

    # Generate init function with fields
    str += f"\tdef __init__(self, {", ".join(fields)}):\n"

    for field in fields:
        str += f"\t\tself.{field} = {field}\n"

    str += "\n"

    # Generate accept fucntion
    str += f"\tdef accept(self, {VISITOR_CLASS.lower()}):\n"
    str += f"\t\treturn {VISITOR_CLASS.lower()}.visit_{name.lower()}(self)\n"

    str += "\n\n"

    return str


def generate_visitor_interface(expr_names):
    str = f"class {VISITOR_CLASS}:\n"

    for expr in expr_names:
        str += f"\tdef visit_{expr.lower()}(self, _expr):\n"
        str += "\t\traise NotImplementedError()\n\n"

    str += "\n"

    return str


def main():
    filename = f"{BASE_CLASS.lower()}.py"
    with open(filename, "w") as file:
        str = "# This file is generated by running tools/generate_ast.py\n\n"

        str += generate_visitor_interface(EXPRESSIONS.keys())
        str += generate_base_class()

        for name, fields in EXPRESSIONS.items():
            str += generate_expression(name, fields)

        file.write(str.expandtabs(4))


if __name__ == "__main__":
    main()
