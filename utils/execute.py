from dsl.utils import drop, move, copy, merge, split, transpose, aggregate

def execute_dsl(sheet, dsl, arguments):
    if dsl == "drop":
        return drop(sheet, *arguments)
    elif dsl == "move":
        return move(sheet, *arguments)
    elif dsl == "copy":
        return copy(sheet, *arguments)
    elif dsl == "merge":
        return merge(sheet, *arguments)
    elif dsl == "split":
        return split(sheet, *arguments)
    elif dsl == "transpose":
        return transpose(sheet, *arguments)
    elif dsl == "aggregate":
        return aggregate(sheet, *arguments)
    else:
        return "Invalid function"