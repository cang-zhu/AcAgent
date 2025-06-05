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

您可以直接用自然语言描述您的需求，例如：
"请帮我搜索关于人工智能在教育领域的应用" 或 "总结我找到的第1篇文献"
输入 'help' 查看帮助信息
输入 'exit' 退出程序
    """)

def print_help():
    print("""
学术智能体支持以下类型的请求：
- **文献搜索与总结**: 询问关于某个主题的文献，例如 "找一些关于气候变化的论文"。
- **文献总结**: 请求总结已经找到的文献列表中的某一篇，例如 "总结第2篇文献"。
- **文本润色**: 提供一段文本并请求润色，例如 "请帮我润色这段文字：..."。
- **数据分析**: 询问进行某种类型的数据分析。
- **生成引用**: 请求生成找到的文献的引用格式，例如 "请给我第1篇文献的 APA 引用"。
- **帮助**: 输入 'help'。
- **退出**: 输入 'exit'。

示例：
请搜索关于新能源汽车技术的最新研究
总结第3篇文献
润色我的论文引言部分：...
生成第1篇文献的 MLA 引用
    """)

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
        "analysis_results": None,
        "user_input": None # 添加 user_input 到状态中
    }
    
    print_welcome()
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n请输入您的请求：").strip()
            session_state["user_input"] = user_input # 更新状态中的用户输入
            
            # 处理特殊命令
            if user_input.lower() == 'exit':
                print("感谢使用学术智能体，再见！")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            # 使用意图识别工具
            intent_data = tools.identify_intent(user_input)
            intent = intent_data.get('intent', 'unknown')
            parameters = intent_data.get('parameters', {})

            print(f"[DEBUG] 识别到意图: {intent}, 参数: {parameters}") # Debug 输出

            # 根据意图设置任务类型和相关参数到状态中
            if intent == "search":
                query = parameters.get('query')
                if not query:
                    print("抱歉，我没有在您的请求中找到搜索关键词。请再试一次，例如：搜索关于人工智能教育应用的文献。")
                    continue

                # 询问是否需要搜索和总结文献
                confirm = input(f"您想让我搜索关于 '{query}' 的学术文献并总结吗？(是/否): ").strip().lower()
                if confirm == '是':
                    session_state["task_type"] = "search"
                    session_state["search_query"] = query # 将查询词存入状态
                    # workflow.invoke(session_state) 将在循环末尾调用
                else:
                    print("好的，已取消搜索请求。")
                    session_state["task_type"] = None # 重置 task_type
                    continue # 跳过工作流调用

            elif intent == "summarize":
                paper_id_str = parameters.get('paper_id')
                if not paper_id_str:
                    print("抱歉，我没有在您的请求中找到要总结的文献ID。请指定文献编号，例如：总结第1篇文献。")
                    continue
                try:
                    paper_id = int(paper_id_str) - 1 # 文献ID通常从1开始，转换为列表索引
                    if 0 <= paper_id < len(session_state.get("literature_results", [])):
                         # 询问是否需要总结指定文献
                        confirm = input(f"您想让我总结第 {paper_id + 1} 篇文献吗？(是/否): ").strip().lower()
                        if confirm == '是':
                            session_state["task_type"] = "summary"
                            session_state["paper_to_summarize_index"] = paper_id # 将要总结的文献索引存入状态
                            # workflow.invoke(session_state) 将在循环末尾调用
                        else:
                             print("好的，已取消总结请求。")
                             session_state["task_type"] = None # 重置 task_type
                             continue # 跳过工作流调用
                    else:
                        print(f"抱歉，文献ID {paper_id_str} 无效。当前已找到 {len(session_state.get("literature_results", []))} 篇文献。")
                        session_state["task_type"] = None # 重置 task_type
                        continue # 跳过工作流调用

                except ValueError:
                    print("抱歉，文献ID格式不正确。请输入一个数字，例如：总结第1篇文献。")
                    session_state["task_type"] = None # 重置 task_type
                    continue # 跳过工作流调用

            elif intent == "polish":
                text_to_polish = parameters.get('text')
                if not text_to_polish:
                     # 如果用户没有直接提供文本，可以提示用户输入或从之前的结果中获取
                     print("请提供您需要润色的文本：")
                     text_to_polish = input().strip()
                     if not text_to_polish:
                          print("未输入文本，取消润色请求。")
                          session_state["task_type"] = None
                          continue
                session_state["task_type"] = "writing" # 使用 writing 任务类型进行润色
                session_state["text_to_polish"] = text_to_polish # 将要润色的文本存入状态

            elif intent == "analyze":
                 data_type = parameters.get('data_type')
                 if not data_type:
                      print("请指定数据分析的类型，例如：进行描述性统计分析。")
                      session_state["task_type"] = None
                      continue
                 # 注意：当前没有数据输入和加载逻辑，此处仅设置任务类型
                 print("当前数据分析功能尚未完全实现，需要先加载数据。")
                 session_state["task_type"] = None # 暂时不执行，或设置为analysis等待数据
                 continue # 暂时跳过工作流调用

            elif intent == "cite":
                paper_id_str = parameters.get('paper_id')
                style = parameters.get('style', 'apa').lower() # 默认为 apa 格式

                if not paper_id_str:
                    print("请指定需要生成引用的文献ID，例如：生成第1篇文献的引用。")
                    session_state["task_type"] = None
                    continue

                try:
                    paper_id = int(paper_id_str) - 1 # 文献ID通常从1开始，转换为列表索引
                    if 0 <= paper_id < len(session_state.get("literature_results", [])):
                         if style not in ['apa', 'mla']:
                             print(f"不支持的引用格式: {style}。支持的格式有 APA 和 MLA。")
                             session_state["task_type"] = None
                             continue
                         session_state["task_type"] = "references"
                         session_state["paper_to_cite_index"] = paper_id # 将要引用的文献索引存入状态
                         session_state["citation_style"] = style # 将引用格式存入状态
                         # workflow.invoke(session_state) 将在循环末尾调用
                    else:
                        print(f"抱歉，文献ID {paper_id_str} 无效。当前已找到 {len(session_state.get("literature_results", []))} 篇文献。")
                        session_state["task_type"] = None # 重置 task_type
                        continue # 跳过工作流调用

                except ValueError:
                    print("抱歉，文献ID格式不正确。请输入一个数字，例如：生成第1篇文献的引用。")
                    session_state["task_type"] = None # 重置 task_type
                    continue # 跳过工作流调用

            elif intent == "unknown":
                print("抱歉，我不理解您的请求。您可以输入 'help' 查看我能做什么。")
                session_state["task_type"] = None # 重置 task_type
                continue # 跳过工作流调用

            else:
                 # 如果意图识别返回了未处理的已知意图，也认为是 unknown
                 print("抱歉，我暂时无法处理您的请求。您可以输入 'help' 查看我能做什么。")
                 session_state["task_type"] = None
                 continue

            # 如果 task_type 被成功设置，则执行工作流
            if session_state.get("task_type"):
                 # 在调用工作流前，可以根据 task_type 准备 workflow 的输入
                 # 目前工作流直接从 session_state 读取，所以这里不需要额外准备
                 print(f"[DEBUG] 执行工作流，任务类型: {session_state['task_type']}")

                 # 清空之前的输出结果，避免干扰
                 session_state["literature_results"] = []
                 session_state["summary"] = None
                 session_state["citations"] = []
                 session_state["analysis_results"] = None
                 session_state["polished_text"] = None # 清空润色文本结果

                 result = workflow.invoke(session_state)

                 # 更新会话状态
                 session_state.update(result)

                 # 显示结果 (根据意图进行更自然的输出)
                 if intent == "search":
                     if session_state["literature_results"]:
                         print("\n为您找到以下文献：")
                         for i, paper in enumerate(session_state["literature_results"], 1):
                             print(f"\n{i}. {paper.get('title', '未知标题')}")
                             print(f"   作者：{paper.get('authors', '未知作者')}")
                             print(f"   年份：{paper.get('year', '未知年份')}")
                     else:
                         print("抱歉，没有找到相关的文献。")

                 elif intent == "summarize":
                     if session_state["summary"]:
                         print("\n文献摘要：")
                         print(session_state["summary"])
                     else:
                         print("抱歉，无法生成文献摘要。")

                 elif intent == "polish":
                     if session_state.get("polished_text"):
                         print("\n润色后的文本：")
                         print(session_state["polished_text"])
                     else:
                         print("抱歉，文本润色失败。")

                 elif intent == "analyze":
                     if session_state["analysis_results"]:
                         print("\n分析结果：")
                         print(json.dumps(session_state["analysis_results"], indent=2, ensure_ascii=False))
                     else:
                         print("抱歉，无法进行数据分析。")

                 elif intent == "cite":
                     if session_state["citations"]:
                         print("\n引用格式：")
                         for citation in session_state["citations"]:
                             print(citation)
                     else:
                         print("抱歉，无法生成引用格式。")

            # 在每次交互结束时重置 task_type，以便下一次意图识别
            session_state["task_type"] = None

        except Exception as e:
            print(f"\n发生错误：{str(e)}")
            # 发生错误时也重置 task_type
            session_state["task_type"] = None
            #print("输入 'help' 查看帮助信息") # 可以选择保留或删除此行

if __name__ == "__main__":
    main() 