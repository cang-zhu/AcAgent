from academic_agent import create_academic_workflow
from academic_tools import AcademicTools
from typing import Dict, Any
import json
import os

def print_welcome():
    print("""
欢迎使用学术智能体！
这是一个基于 Qwen API 的学术助手，可以帮助您：
1. 检索和总结学术文献
2. 润色学术写作
3. 分析研究数据
4. 生成标准引用
5. 解析 BibTeX 文本
6. 解析和分析 PDF 文件

您可以直接用自然语言描述您的需求，例如：
"请帮我搜索关于人工智能在教育领域的应用" 或 "总结我找到的第1篇文献" 或 "解析以下 BibTeX 文本：..."
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
- **解析 BibTeX**: 提供 BibTeX 格式的文献信息进行解析，例如 "解析以下 BibTeX：..."
- **PDF 处理**: 
  * 解析 PDF 文件：例如 "解析这个 PDF 文件：/path/to/paper.pdf"
  * 分析 PDF 内容：例如 "分析这个 PDF 文件：/path/to/paper.pdf"
- **帮助**: 输入 'help'。
- **退出**: 输入 'exit'。

示例：
请搜索关于新能源汽车技术的最新研究
总结第3篇文献
润色我的论文引言部分：...
生成第1篇文献的 MLA 引用
解析以下 BibTeX：@article{...}
解析这个 PDF 文件：/path/to/paper.pdf
分析这个 PDF 文件：/path/to/paper.pdf
    """)

def main():
    # 初始化工具和工作流
    tools = AcademicTools()
    workflow = create_academic_workflow()
    
    # 存储会话状态
    session_state = {
        "messages": [],
        "task_type": None,
        "search_query": None,
        "search_method": None,
        "literature_results": [],
        "summary": None,
        "citations": [],
        "analysis_results": None,
        "user_input": None,
        "text_to_polish": None,
        "paper_to_summarize_index": None,
        "paper_to_cite_index": None,
        "citation_style": None,
        "bibtex_input": None,
        "pdf_path": None, # 添加 PDF 文件路径
        "pdf_sections": None, # 添加 PDF 章节内容
        "pdf_analysis": None # 添加 PDF 分析结果
    }
    
    print_welcome()
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n请输入您的请求：").strip()
            session_state["user_input"] = user_input
            
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

            print(f"[DEBUG] 识别到意图: {intent}, 参数: {parameters}")

            # 根据意图设置任务类型和相关参数到状态中
            if intent == "search":
                query = parameters.get('query')
                if not query:
                    print("抱歉，我没有在您的请求中找到搜索关键词。请再试一次，例如：搜索关于人工智能教育应用的文献。")
                    continue

                # 询问是否需要搜索和总结文献
                confirm = input(f"您想让我搜索关于 '{query}' 的学术文献并总结吗？(是/否): ").strip().lower()
                if confirm == '是':
                    # 询问用户偏好的搜索方法
                    search_method_choice = input("请选择搜索方式 (scholarly/qwen): ").strip().lower()
                    if search_method_choice in ['scholarly', 'qwen']:
                        session_state["task_type"] = "search"
                        session_state["search_query"] = query
                        session_state["search_method"] = search_method_choice # 将搜索方法存入状态
                        # workflow.invoke(session_state) 将在循环末尾调用
                    else:
                        print("无效的搜索方式选择，请选择 'scholarly' 或 'qwen'。")
                        session_state["task_type"] = None # 重置 task_type
                        continue # 跳过工作流调用
                else:
                    print("好的，已取消搜索请求。")
                    session_state["task_type"] = None # 重置 task_type
                    continue # 跳过工作流调用

            elif intent == "parse_bibtex":
                bibtex_string = parameters.get('bibtex_string', user_input) # 如果参数中没有，尝试使用整个用户输入
                if not bibtex_string or not bibtex_string.strip().startswith('@'): # 简单的格式检查
                    print("抱歉，我没有在您的请求中找到有效的 BibTeX 文本。请提供以 '@' 开头的 BibTeX 格式文本。")
                    session_state["task_type"] = None
                    continue
                    
                session_state["task_type"] = "parse_bibtex"
                session_state["bibtex_input"] = bibtex_string # 将 BibTeX 文本存入状态

            elif intent == "parse_pdf": # 添加 PDF 解析处理
                pdf_path = parameters.get('pdf_path')
                if not pdf_path:
                    print("抱歉，我没有在您的请求中找到 PDF 文件路径。请提供完整的文件路径。")
                    continue
                    
                if not os.path.exists(pdf_path):
                    print(f"抱歉，找不到文件：{pdf_path}")
                    continue
                    
                if not pdf_path.lower().endswith('.pdf'):
                    print("抱歉，请提供 PDF 文件。")
                    continue
                    
                session_state["task_type"] = "parse_pdf"
                session_state["pdf_path"] = pdf_path

            elif intent == "analyze_pdf": # 添加 PDF 分析处理
                pdf_path = parameters.get('pdf_path')
                if not pdf_path:
                    print("抱歉，我没有在您的请求中找到 PDF 文件路径。请提供完整的文件路径。")
                    continue
                    
                if not os.path.exists(pdf_path):
                    print(f"抱歉，找不到文件：{pdf_path}")
                    continue
                    
                if not pdf_path.lower().endswith('.pdf'):
                    print("抱歉，请提供 PDF 文件。")
                    continue
                    
                session_state["task_type"] = "analyze_pdf"
                session_state["pdf_path"] = pdf_path

            elif intent == "summarize":
                paper_id_str = parameters.get('paper_id')
                if not paper_id_str:
                    print("抱歉，我没有在您的请求中找到要总结的文献ID。请指定文献编号，例如：总结第1篇文献。")
                    continue
                try:
                    paper_id = int(paper_id_str) - 1 # 文献ID通常从1开始，转换为列表索引
                    if session_state.get("literature_results") and 0 <= paper_id < len(session_state["literature_results"]):
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
                        print("请先进行文献搜索或解析。")
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
                    if session_state.get("literature_results") and 0 <= paper_id < len(session_state["literature_results"]):
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
                        print("请先进行文献搜索或解析。")
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
                 if session_state['task_type'] == 'search':
                     print(f"[DEBUG] 准备使用 {session_state.get('search_method', '默认方式')} 进行文献搜索...")
                 elif session_state['task_type'] == 'parse_bibtex':
                      print("[DEBUG] 准备解析 BibTeX 文本...")
                 elif session_state['task_type'] == 'parse_pdf':
                      print("[DEBUG] 准备解析 PDF 文件...")
                 elif session_state['task_type'] == 'analyze_pdf':
                      print("[DEBUG] 准备分析 PDF 内容...")

                 print(f"[DEBUG] 执行工作流，任务类型: {session_state['task_type']}")

                 # 清空之前的输出结果，避免干扰（保留 literature_results 如果是解析或搜索的结果）
                 if session_state['task_type'] not in ['search', 'parse_bibtex', 'parse_pdf', 'analyze_pdf']:
                     session_state["literature_results"] = []
                 session_state["summary"] = None
                 session_state["citations"] = []
                 session_state["analysis_results"] = None
                 session_state["polished_text"] = None
                 session_state["bibtex_input"] = None
                 session_state["pdf_sections"] = None
                 session_state["pdf_analysis"] = None

                 result = workflow.invoke(session_state)

                 # 更新会话状态
                 session_state.update(result)

                 # 显示结果 (根据意图进行更自然的输出)
                 if intent == "search" or intent == "parse_bibtex": # 搜索和解析 BibTeX 都显示文献列表
                     if session_state.get("literature_results"):
                         print("\n找到以下文献：")
                         for i, paper in enumerate(session_state["literature_results"], 1):
                             print(f"\n{i}. {paper.get('title', '未知标题')}")
                             print(f"   作者：{paper.get('authors', '未知作者')}")
                             print(f"   年份：{paper.get('year', '未知年份')}")
                             # 如果有 friendly_summary，也显示
                             if paper.get('friendly_summary'):
                                  print(f"   概括：{paper['friendly_summary']}")
                             elif paper.get('abstract'):
                                  print(f"   摘要：{paper['abstract'][:200]}...") # 显示部分摘要
                             if paper.get('url'):
                                  print(f"   链接：{paper['url']}")
                     else:
                         print("抱歉，没有找到相关的文献或解析失败。")

                 elif intent == "parse_pdf":
                     if session_state.get("pdf_sections"):
                         print("\nPDF 章节内容：")
                         for section, content in session_state["pdf_sections"].items():
                             print(f"\n{section.upper()}:")
                             print(content[:500] + "..." if len(content) > 500 else content)
                     else:
                         print("抱歉，无法解析 PDF 文件。")

                 elif intent == "analyze_pdf":
                     if session_state.get("pdf_analysis"):
                         analysis = session_state["pdf_analysis"]
                         print("\nPDF 分析结果：")
                         print("\n摘要：")
                         print(analysis.get('summary', '无法生成摘要'))
                         print("\n关键点：")
                         for point in analysis.get('key_points', []):
                             print(f"- {point}")
                         print("\n研究方法：")
                         print(analysis.get('methodology', '无法提取研究方法'))
                         print("\n主要发现：")
                         print(analysis.get('findings', '无法提取主要发现'))
                     else:
                         print("抱歉，无法分析 PDF 内容。")

                 elif intent == "summarize":
                     if session_state.get("summary"):
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
                     if session_state.get("analysis_results"):
                         print("\n分析结果：")
                         print(json.dumps(session_state["analysis_results"], indent=2, ensure_ascii=False))
                     else:
                         print("抱歉，无法进行数据分析。")

                 elif intent == "cite":
                     if session_state.get("citations"):
                         print("\n引用格式：")
                         for citation in session_state["citations"]:
                             print(citation)
                     else:
                         print("抱歉，无法生成引用格式。请确保您已搜索或解析文献，并提供有效的文献编号。")

            # 在每次交互结束时重置 task_type 和 bibtex_input，以便下一次意图识别
            session_state["task_type"] = None
            session_state["bibtex_input"] = None
            session_state["pdf_path"] = None
            session_state["pdf_sections"] = None
            session_state["pdf_analysis"] = None

        except Exception as e:
            print(f"\n发生错误：{str(e)}")
            # 发生错误时也重置 task_type 和 bibtex_input
            session_state["task_type"] = None
            session_state["bibtex_input"] = None
            session_state["pdf_path"] = None
            session_state["pdf_sections"] = None
            session_state["pdf_analysis"] = None
            #print("输入 'help' 查看帮助信息") # 可以选择保留或删除此行

if __name__ == "__main__":
    main() 