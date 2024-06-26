from dsl.utils import (
    insert,
    drop,
    assign,
    move,
    copy,
    merge,
    split,
    transpose,
    aggregate,
)


def execute_dsl(sheet, function, arguments, target_sheet=None):
    if function == "insert":
        return insert(sheet, *arguments)
    elif function == "drop":
        return drop(sheet, *arguments)
    elif function == "assign":
        return assign(sheet, *arguments)
    elif function == "move":
        return move(sheet, arguments[0], target_sheet, *arguments[1:])
    elif function == "copy":
        return copy(sheet, arguments[0], target_sheet, *arguments[1:])
    elif function == "merge":
        return merge(sheet, *arguments)
    elif function == "split":
        return split(sheet, *arguments)
    elif function == "transpose":
        return transpose(sheet)
    elif function == "aggregate":
        return aggregate(sheet, *arguments)
    else:
        return "Invalid function"
