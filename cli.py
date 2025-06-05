from academic_agent import create_academic_workflow
from academic_tools import AcademicTools
from typing import Dict, Any
import json

def print_welcome():
    print("""
欢迎使用学术智能体！
这是一个基于 Qwen API 的学术助手，可以帮助您：
1. 检索和总结学术文献
2. 润色学术写作
3. 分析研究数据
4. 生成标准引用

输入 'help' 查看帮助信息
输入 'exit' 退出程序
    """)

def print_help():
    print("""
可用命令：
1. search <关键词> - 搜索相关文献
2. summarize <文献ID> - 生成文献摘要
3. polish <文本> - 润色学术文本
4. analyze <数据类型> - 分析研究数据
5. cite <文献ID> [格式] - 生成引用（支持 APA/MLA 格式）
6. help - 显示此帮助信息
7. exit - 退出程序

示例：
search 人工智能教育应用
summarize 1
polish 这是一段需要润色的学术文本
analyze descriptive
cite 1 apa
    """)

def parse_command(cmd: str) -> Dict[str, Any]:
    """解析用户输入的命令"""
    parts = cmd.strip().split(' ', 1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    return {
        "command": command,
        "args": args
    }

def main():
    # 初始化工具和工作流
    tools = AcademicTools()
    workflow = create_academic_workflow()
    
    # 存储会话状态
    session_state = {
        "messages": [],
        "task_type": None,
        "literature_results": [],
        "summary": None,
        "citations": [],
        "analysis_results": None
    }
    
    print_welcome()
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n请输入命令或问题：").strip()
            
            # 处理特殊命令
            if user_input.lower() == 'exit':
                print("感谢使用学术智能体，再见！")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            # 解析命令
            cmd = parse_command(user_input)
            
            # 根据命令类型设置任务类型
            if cmd["command"] == "search":
                session_state["task_type"] = "search"
            elif cmd["command"] == "summarize":
                session_state["task_type"] = "summary"
            elif cmd["command"] == "polish":
                session_state["task_type"] = "writing"
            elif cmd["command"] == "analyze":
                session_state["task_type"] = "analysis"
            elif cmd["command"] == "cite":
                session_state["task_type"] = "references"
            
            # 执行工作流
            result = workflow.invoke(session_state)
            
            # 更新会话状态
            session_state.update(result)
            
            # 显示结果
            if cmd["command"] == "search":
                print("\n找到以下文献：")
                for i, paper in enumerate(session_state["literature_results"], 1):
                    print(f"\n{i}. {paper['title']}")
                    print(f"   作者：{paper['authors']}")
                    print(f"   年份：{paper['year']}")
            
            elif cmd["command"] == "summarize":
                if session_state["summary"]:
                    print("\n文献摘要：")
                    print(session_state["summary"])
            
            elif cmd["command"] == "polish":
                if session_state.get("polished_text"):
                    print("\n润色后的文本：")
                    print(session_state["polished_text"])
            
            elif cmd["command"] == "analyze":
                if session_state["analysis_results"]:
                    print("\n分析结果：")
                    print(json.dumps(session_state["analysis_results"], indent=2, ensure_ascii=False))
            
            elif cmd["command"] == "cite":
                if session_state["citations"]:
                    print("\n引用格式：")
                    for citation in session_state["citations"]:
                        print(citation)
            
            else:
                print("\n抱歉，我不理解这个命令。输入 'help' 查看可用命令。")
        
        except Exception as e:
            print(f"\n发生错误：{str(e)}")
            print("输入 'help' 查看帮助信息")

if __name__ == "__main__":
    main() 