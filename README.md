# 工具选择智能体

这个智能体能够根据用户输入自动选择最合适的外部工具。

## 功能特点

- 智能分析用户需求
- 从可用工具列表中选择最合适的工具
- 支持多工具协作
- 当信息不足时主动询问

## 使用方法

```python
from tool_selection_agent import ToolSelectionAgent
from tools.tool_executor import ToolExecutor
from llm.llm_client import OpenAICompatibleClient

# 初始化
llm_client = OpenAICompatibleClient()
tool_executor = ToolExecutor()

# 注册工具
tool_executor.registerTool("tool_name", "工具描述", tool_function)

# 创建工具选择智能体
tool_selector = ToolSelectionAgent(llm_client, tool_executor.tools)

# 选择工具
result = tool_selector.select_tools("用户输入")
```

## 输出格式

```json
{
  "reasoning": "推理过程",
  "selected_tools": [
    {
      "tool_name": "工具名称",
      "reason": "选择原因",
      "priority": 1
    }
  ],
  "requires_further_info": false,
  "suggested_questions": []
}
```
