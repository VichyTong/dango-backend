from lark import Lark, Transformer, Tree
import utils


# Define the grammar for the DSL
# LABELS menas index or column labels
dsl_grammar = """
    start: command+
    command: drop | move | copy | merge | split | transpose | aggregate | test
    drop: "drop(" "table=" NAME "," "label=" label "," "axis=" AXIS ")"
    move: "move(" "table=" NAME "," "label=" label "," "target_table=" NAME "," "target_label=" label "," "axis=" AXIS ")"
    copy: "copy(" "table=" NAME "," "label=" label "," "target_table=" NAME "," "target_label=" label "," "axis=" AXIS ")"
    merge: "merge(" "table=" NAME "," "label_1=" label "," "label_2=" label "," "glue=" string "," "new_label=" label "," "axis=" AXIS ")"
    split: "split(" "table=" NAME "," "label=" label "," "delimiter=" string "," "new_labels=" labels "," "axis=" AXIS ")"
    transpose: "transpose(" "table=" NAME ")"
    aggregate: "aggregate(" "table=" NAME "," "functions=" functions "," "axis=" AXIS ")"

    labels: "[" [label ("," label)*] "]"
    label: NAME | NUMBER
    string : /"[^"]*"/
    functions: "[" [FUNCTION ("," FUNCTION)*] "]"

    FUNCTION: "mean" | "median" | "prod" | "sum" | "std" | "var" | "min" | "max"
    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
    AXIS: "0" | "1" | "index" | "columns"
    
    STRATEGY: "t-test" | "z-test" | "chi-squared"

    %import common.NUMBER
    %import common.WS
    %ignore WS
"""
# TODO: Rethink the return type of function `test`
# test: "test(" "table=" NAME "," "label1=" label "," "label2=" label "," "strategy=" STRATEGY "," "axis=" AXIS ")"


class DSLTransformer(Transformer):
    def drop(self, args):
        return {"drop": {"table": args[0], "label": args[1], "axis": args[2]}}

    def move(self, args):
        return {
            "move": {
                "table": args[0],
                "label": args[1],
                "target_table": args[2],
                "target_label": args[3],
                "axis": args[4],
            }
        }

    def copy(self, args):
        return {
            "copy": {
                "table": args[0],
                "label": args[1],
                "target_table": args[2],
                "target_label": args[3],
                "axis": args[4],
            }
        }

    def merge(self, args):
        return {
            "merge": {
                "table": args[0],
                "label1": args[1],
                "label2": args[2],
                "glue": args[3],
                "new_label": args[4],
                "axis": args[5],
            }
        }

    def split(self, args):
        return {
            "split": {
                "table": args[0],
                "label": args[1],
                "delimiter": args[2],
                "new_labels": args[3],
                "axis": args[4],
            }
        }

    def transpose(self, args):
        return {"transpose": {"table": args[0]}}

    def aggregate(self, args):
        return {
            "aggregate": {
                "table": args[0],
                "functions": args[1],
                "axis": args[2],
            }
        }

    # def test(self, args):
    #     return {
    #         "test": {
    #             "table": args[0],
    #             "label1": args[1],
    #             "label2": args[2],
    #             "strategy": args[3],
    #             "axis": args[4],
    #         }
    #     }

    def labels(self, args):
        # Convert the list of label Trees into a list of label values
        return [label.children[0].value for label in args]

    def string(self, args):
        return args[0][1:-1]
        
    def functions(self, args):
        funs = [function.value for function in args]
        # only keep unique functions
        return list(set(funs))


# Initialize Lark with the grammar
dsl_parser = Lark(dsl_grammar, parser="lalr", transformer=DSLTransformer())

def convert_axis(token):
    if token.value.isdigit():
        return int(token.value)
    elif token.value in ['index', 'columns']:
        return token.value
    else:
        raise ValueError(f"Unexpected token value: {token.value}")


# Function to parse and execute commands
def execute_dsl(tables, dsl_code):
    parsed = dsl_parser.parse(dsl_code)
    # print(parsed.pretty())  # This line prints the parsed tree in a readable format.

    for command in parsed.children:
        # print("Executing command:", command)
        if isinstance(command, Tree):
            command = command.children[0]
            command_type = list(command.keys())[0]

            table_name = command[command_type]["table"]
            table = tables[table_name]

            if command_type == "drop":
                label = command["drop"]["label"].children[0].value
                axis = convert_axis(command["drop"]["axis"])
                tables[table_name] = utils.drop(table, label, axis)
            elif command_type == "move":
                label = command["move"]["label"].children[0].value
                target_table = command["move"]["target_table"]
                target_label = command["move"]["target_label"].children[0].value
                axis = convert_axis(command["move"]["axis"])
                tables[table_name], tables[target_table] = utils.move(
                    table, label, tables[target_table], target_label, axis
                )
            elif command_type == "copy":
                label = command["copy"]["label"].children[0].value
                target_table = command["copy"]["target_table"]
                target_label = command["copy"]["target_label"].children[0].value
                axis = convert_axis(command["copy"]["axis"])
                tables[table_name] = utils.copy(
                    table, label, tables[target_table], target_label, axis
                )
            elif command_type == "merge":
                label1 = command["merge"]["label1"].children[0].value
                label2 = command["merge"]["label2"].children[0].value
                glue = command["merge"]["glue"]
                new_label = command["merge"]["new_label"].children[0].value
                axis = convert_axis(command["merge"]["axis"])
                tables[table_name] = utils.merge(table, label1, label2, glue, new_label, axis)
            elif command_type == "split":
                label = command["split"]["label"].children[0].value
                delimiter = command["split"]["delimiter"]
                new_labels = command["split"]["new_labels"]
                axis = convert_axis(command["split"]["axis"])
                tables[table_name] = utils.split(table, label, delimiter, new_labels, axis)
            elif command_type == "transpose":
                tables[table_name] = utils.transpose(table)
            elif command_type == "aggregate":
                functions = command["aggregate"]["functions"]
                axis = convert_axis(command["aggregate"]["axis"])
                tables[table_name] = utils.aggregate(table, functions, axis)
            # elif command_type == "test":
            #     label1 = command["test"]["label1"]
            #     label2 = command["test"]["label2"]
            #     strategy = command["test"]["strategy"]
            #     axis = convert_axis(command["test"]["axis"])
            #     tables[table_name] = utils.test(table, label1, label2, strategy, axis)
        else:
            print("Invalid command:", command)
        
        return tables
