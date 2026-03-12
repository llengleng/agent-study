class ToolExecutor:

    def __init__(self, registry):
        self.registry = registry

    def execute(self, tool_name, params):

        tool = self.registry.get(tool_name)

        if not tool:
            raise Exception(f"Tool {tool_name} not found")

        return tool.run(**params)