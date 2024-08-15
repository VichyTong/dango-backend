from functions import DangoFunction

class DangoSubtable(DangoFunction):
    def __init__(self):
        super().__init__(function_type="A")

    def execute(self, table, label_list, new_name, axis=1):
        """
        Returns a sub-table containing only the specified rows or columns.
        Parameters:
        - table_name (str): The name of the table to extract the rows/columns from.
        - label_list (list[str/int]): The list of row/column labels to extract.
        - new_name (str): The name of the new table.
        - axis (str or int):
            - 0 or "index": Indicates to extract rows. The label_list contains row indexes.
            - 1 or "columns": Indicates to extract columns. The label_list contains column names.
        """

        axis = self.classify_axis(axis)
        if axis == 0:
            return table.loc[label_list]
        elif axis == 1:
            return table[label_list]
        else:
            raise ValueError("Invalid axis. Choose from 0 or 'index', 1 or 'columns'.")
