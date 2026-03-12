from .tool_registry import ToolRegistry
from .tool.weater_tool import WeatherTool
from .tool.city_tool import CityTool

registry = ToolRegistry()

registry.register(WeatherTool())
registry.register(CityTool())