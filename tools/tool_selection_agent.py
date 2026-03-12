"""
工具选择智能体 - 根据用户输入自动选择需要使用的工具
"""
from typing import Dict, List, Optional
from llm.llm_client import OpenAICompatibleClient
import json


class ToolSelectionAgent:
    def __init__(self, llm_client: OpenAICompatibleClient, tools_registry: Dict):
        """
        初始化工具选择智能体

        Args:
            llm_client: LLM客户端
            tools_registry: 工具注册表，包含所有可用工具的信息
        """
        self.llm_client = llm_client
        self.tools_registry = tools_registry

        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """
        构建系统提示词，包含工具信息
        """
        tools_description = self._format_tools_description()

        return f"""你是一个智能工具选择助手。你的任务是根据用户的需求，从可用工具列表中选择最合适的工具。

# 可用工具列表:
{tools_description}

# 工作流程:
1. 仔细分析用户的请求，理解用户想要完成什么任务
2. 从可用工具列表中识别出最符合用户需求的工具
3. 如果需要多个工具，按照优先级排序
4. 如果没有合适的工具，说明原因

# 输出格式:
你必须严格按照JSON格式输出，不要包含任何其他文字说明。输出格式如下:

```json
{{
  "reasoning": "你的思考过程，解释为什么选择这些工具",
  "selected_tools": [
    {{
      "tool_name": "工具名称",
      "reason": "选择这个工具的原因",
      "priority": 1
    }}
  ],
  "requires_further_info": false,
  "suggested_questions": []
}}
```

字段说明:
- reasoning: 你的思考过程
- selected_tools: 选择的工具列表（按优先级排序，priority越小优先级越高）
- requires_further_info: 是否需要向用户询问更多信息
- suggested_questions: 如果需要更多信息，列出建议询问的问题

# 注意事项:
- 如果用户的请求不明确或缺少必要参数，将 requires_further_info 设为 true
- 优先选择能够直接解决问题的工具
- 如果需要多个工具协作，按执行顺序排列
- 确保输出的JSON格式正确，可以被解析
"""

    def _format_tools_description(self) -> str:
        """
        格式化工具描述
        """
        descriptions = []

        # 兼容两种输入格式：字典或列表
        if isinstance(self.tools_registry, dict):
            for tool_name, tool_info in self.tools_registry.items():
                desc = f"- **{tool_name}**: {tool_info.get('description', '')}"
                descriptions.append(desc)
        elif isinstance(self.tools_registry, list):
            for tool_info in self.tools_registry:
                tool_name = tool_info.get('name', '')
                desc = f"- **{tool_name}**: {tool_info.get('description', '')}"
                descriptions.append(desc)

        return "\n".join(descriptions)

    def select_tools(self, user_input: str) -> Dict:
        """
        根据用户输入选择工具

        Args:
            user_input: 用户输入的信息

        Returns:
            包含选择结果和推理过程的字典
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"用户请求: {user_input}"}
        ]

        print(f"🤖 正在为用户请求选择工具...")
        print(f"📝 用户输入: {user_input}\n")

        response = self.llm_client.think(messages, temperature=0)

        if not response:
            return {
                "reasoning": "LLM调用失败",
                "selected_tools": [],
                "requires_further_info": True,
                "suggested_questions": ["请稍后重试"]
            }

        try:
            # 尝试提取JSON部分
            json_str = self._extract_json(response)
            result = json.loads(json_str)

            print(f"✅ 工具选择完成")
            print(f"📋 推理过程: {result.get('reasoning', '')}\n")

            if result.get('selected_tools'):
                print(f"🔧 选中的工具:")
                for tool in result['selected_tools']:
                    print(f"   - {tool['tool_name']} (优先级: {tool['priority']})")

            if result.get('requires_further_info'):
                print(f"\n❓ 需要更多信息:")
                for q in result.get('suggested_questions', []):
                    print(f"   - {q}")

            print()

            return result

        except json.JSONDecodeError as e:
            print(f"❌ 解析JSON失败: {e}")
            print(f"原始响应: {response}\n")
            return {
                "reasoning": "工具选择响应格式错误",
                "selected_tools": [],
                "requires_further_info": True,
                "suggested_questions": ["请重新描述您的需求"]
            }

    def _extract_json(self, text: str) -> str:
        """
        从文本中提取JSON部分
        """
        # 尝试找到 ```json ``` 代码块
        import re
        pattern = r'```json\s*({.*?})\s*```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)

        # 尝试找到最外层的 { ... }
        pattern = r'\{.*\}'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(0)

        # 如果都没找到，返回原文本
        return text

    def execute_selected_tools(self, user_input: str, tool_executor) -> List[str]:
        """
        选择工具并执行

        Args:
            user_input: 用户输入
            tool_executor: 工具执行器实例

        Returns:
            工具执行结果列表
        """
        selection_result = self.select_tools(user_input)

        if selection_result.get('requires_further_info'):
            print("需要更多信息才能完成任务")
            for q in selection_result.get('suggested_questions', []):
                print(f"  - {q}")
            return []

        results = []
        for tool_info in selection_result.get('selected_tools', []):
            tool_name = tool_info['tool_name']
            reason = tool_info['reason']

            print(f"🔧 执行工具: {tool_name}")
            print(f"   原因: {reason}")

            # 使用另一个agent来解析工具参数
            params = self._parse_tool_parameters(user_input, tool_name)

            try:
                result = tool_executor.execute(tool_name, params)
                results.append(result)
                print(f"✅ 执行成功: {str(result)[:100]}...\n")
            except Exception as e:
                error_msg = f"工具执行失败: {e}"
                print(f"❌ {error_msg}\n")
                results.append(error_msg)

        return results

    def _parse_tool_parameters(self, user_input: str, tool_name: str) -> Dict:
        """
        使用LLM从用户输入中解析工具所需的参数

        Args:
            user_input: 用户输入
            tool_name: 工具名称

        Returns:
            解析出的参数字典
        """
        # 获取工具的参数定义
        from tools import registry
        tool = registry.get(tool_name)
        if not tool:
            return {}

        param_schema = tool.parameters
        param_desc = json.dumps(param_schema, ensure_ascii=False, indent=2)

        messages = [
            {
                "role": "system",
                "content": f"""你是一个参数解析助手。根据用户输入和工具参数定义，提取出工具所需的参数值。

工具名称: {tool_name}

工具参数定义:
```json
{param_desc}
```

请严格按照JSON格式输出参数值，不要包含任何其他文字说明。输出格式:
```json
{{
  "参数名1": "参数值1",
  "参数名2": "参数值2"
}}
```

注意事项:
- 只输出工具定义中 required 的参数
- 如果用户输入中缺少必要参数，将对应的值设为 null
- 如果工具不需要参数，输出空对象 {{}}"""
            },
            {
                "role": "user",
                "content": f"用户输入: {user_input}"
            }
        ]

        try:
            response = self.llm_client.think(messages, temperature=0)
            if response:
                json_str = self._extract_json(response)
                params = json.loads(json_str)
                # 过滤掉 null 值
                params = {k: v for k, v in params.items() if v is not None}
                return params
        except Exception as e:
            print(f"⚠️ 参数解析失败: {e}")

        return {}
