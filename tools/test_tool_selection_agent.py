"""
测试 ToolSelectionAgent 工具选择智能体
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from llm.llm_client import OpenAICompatibleClient
from tools import registry
from tools.tool_executor import ToolExecutor
from tools.tool_selection_agent import ToolSelectionAgent

# 加载环境变量
load_dotenv()


def test_tool_selection():
    """测试工具选择功能"""
    print("=" * 60)
    print("测试 ToolSelectionAgent")
    print("=" * 60)
    print()

    # 初始化 LLM 客户端
    try:
        llm_client = OpenAICompatibleClient()
    except ValueError as e:
        print(f"❌ 初始化LLM客户端失败: {e}")
        print("请确保已配置 .env 文件中的 LLM_MODEL_ID, LLM_API_KEY, LLM_BASE_URL")
        return

    # 初始化工具执行器
    tool_executor = ToolExecutor(registry)

    # 初始化工具选择智能体
    agent = ToolSelectionAgent(llm_client, registry.schemas())

    # 测试用例
    test_cases = [
        "帮我查询北京的天气",
        "我想知道上海的旅游景点推荐",
        "搜索一下人工智能的最新发展",
        "帮我查询杭州的天气和景点推荐"
    ]

    print("\n" + "=" * 60)
    print("开始测试工具选择和执行")
    print("=" * 60)
    print()

    for i, user_input in enumerate(test_cases, 1):
        print(f"\n{'=' * 60}")
        print(f"测试用例 {i}: {user_input}")
        print('=' * 60)

        # 执行工具选择和执行
        results = agent.execute_selected_tools(user_input, tool_executor)

        # 打印执行结果
        if results:
            print(f"\n📊 执行结果:")
            for j, result in enumerate(results, 1):
                print(f"{j}. {result}")
        else:
            print("没有执行任何工具")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


def test_tool_selection_only():
    """仅测试工具选择功能，不执行工具"""
    print("=" * 60)
    print("测试工具选择功能（仅选择，不执行）")
    print("=" * 60)
    print()

    # 初始化 LLM 客户端
    try:
        llm_client = OpenAICompatibleClient()
    except ValueError as e:
        print(f"❌ 初始化LLM客户端失败: {e}")
        return

    # 初始化工具选择智能体
    agent = ToolSelectionAgent(llm_client, registry.schemas())

    # 测试用例
    test_cases = [
        "帮我查询深圳的天气",
        "推荐一些成都的景点",
        "搜索Python教程"
    ]

    for i, user_input in enumerate(test_cases, 1):
        print(f"\n{'=' * 60}")
        print(f"测试用例 {i}: {user_input}")
        print('=' * 60)

        # 仅选择工具
        result = agent.select_tools(user_input)

        # 打印选择结果
        print(f"\n📋 工具选择结果:")
        print(f"   推理过程: {result.get('reasoning', '')}")
        print(f"   需要更多信息: {result.get('requires_further_info', False)}")

        if result.get('selected_tools'):
            print(f"   选中的工具:")
            for tool in result['selected_tools']:
                print(f"      - {tool['tool_name']}: {tool['reason']} (优先级: {tool['priority']})")

        if result.get('requires_further_info'):
            print(f"   建议询问的问题:")
            for q in result.get('suggested_questions', []):
                print(f"      - {q}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    # 选择测试模式
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--select-only":
        test_tool_selection_only()
    else:
        test_tool_selection()
