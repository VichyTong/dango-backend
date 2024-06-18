class DependenciesManager:
    def __init__(self):
        self.nodes = []

    def add_node(self, sheet_id, dependencies=None):
        if dependencies is None:
            dependencies = []
        node = {
            'sheet_id': sheet_id,
            'dependency': dependencies
        }
        self.nodes.append(node)

    def get_node(self, sheet_id):
        for node in self.nodes:
            if node['sheet_id'] == sheet_id:
                return node
        return None

    def get_all_nodes(self):
        return self.nodes

    def clear_all_nodes(self):
        self.nodes = []

    def remove_node(self, sheet_id):
        self.nodes = [node for node in self.nodes if node['sheet_id'] != sheet_id]

    def add_dependency(self, sheet_id, dependency):
        for node in self.nodes:
            if node['sheet_id'] == sheet_id and not self.is_dependency_exists(sheet_id, dependency):
                node['dependency'].append(dependency)
                return True
        return False

    def is_dependency_exists(self, sheet_id, dependency):
        for node in self.nodes:
            if node['sheet_id'] == sheet_id:
                for dep in node['dependency']:
                    if dep['sheet_id'] == dependency['sheet_id'] and dep['action'] == dependency['action']:
                        return True
        return False

    def is_exists(self, sheet_id):
        for node in self.nodes:
            if node['sheet_id'] == sheet_id:
                return True
        return False

    def display_nodes(self):
        for node in self.nodes:
            print(f"Sheet ID: {node['sheet_id']}, Dependencies: {node['dependency']}")

    def update_dependency(self, function, arguments):
        print(f"&&&& Function: {function}, Arguments: {arguments}")
        if function == 'drop':
            return self.handle_drop_statement(arguments)
        return False

    def handle_drop_statement(self, arguments):
        sheet_id = arguments[0]
        # Heart Disease Prediction dataset_v0.csv
        file_name = sheet_id.split('_')[0]
        version = int(sheet_id.split('_')[-1].split('.')[0].replace('v', ''))
        new_version = version + 1
        new_sheet_id = f"{file_name}_v{new_version}.csv"
        index = arguments[1]
        action = 'drop'
        if arguments[2] == 'index':
            action += " row " + str(index)
        else:
            action += " column " + str(index)
        dependency = {
            'sheet_id': sheet_id,
            'action': action
        }
        if self.is_exists(new_sheet_id):
            self.add_dependency(new_sheet_id, dependency)
        else:
            self.add_node(new_sheet_id, [dependency])
        self.display_nodes()
        return True




[{'sheet_id': '', 'dependency': [{'sheet_id': '', 'action': ''}, {...}]},       ]