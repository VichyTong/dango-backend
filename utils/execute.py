from dsl.utils import (
    insert,
    drop,
    assign,
    move,
    copy,
    swap,
    merge,
    concatenate,
    split,
    transpose,
    aggregate,
    test,
)


def execute_dsl(sheet, function, arguments, target_sheet=None):
    if function == "insert":
        return insert(sheet, *arguments)
    elif function == "drop":
        return drop(sheet, *arguments)
    elif function == "assign":
        return assign(sheet, *arguments)
    elif function == "copy":
        return copy(sheet, arguments[0], target_sheet, *arguments[1:])
    elif function == "move":
        return move(sheet, arguments[0], target_sheet, *arguments[1:])
    elif function == "swap":
        return swap(sheet, arguments[0], target_sheet, *arguments[1:])
    elif function == "merge":
        return merge(sheet, target_sheet, *arguments)
    elif function == "concatenate":
        return concatenate(sheet, *arguments)
    elif function == "split":
        return split(sheet, *arguments)
    elif function == "transpose":
        return transpose(sheet)
    elif function == "aggregate":
        return aggregate(sheet, *arguments)
    elif function == "test":
        return test(sheet, *arguments)
    else:
        return "Invalid function"
