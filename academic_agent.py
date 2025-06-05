from typing import Annotated, TypedDict, Sequence
from langgraph.graph import Graph, StateGraph
from langchain_core.messages import HumanMessage, AIMessage
# from langchain_openai import ChatOpenAI # 不需要 ChatOpenAI 了，我们直接使用 AcademicTools
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from academic_tools import AcademicTools # 导入 AcademicTools

# 加载环境变量
load_dotenv()

# 定义状态类型
class AgentState(TypedDict):
    messages: Sequence[HumanMessage | AIMessage]
    task_type: str | None # 用户请求的任务类型 (e.g., "search", "summary", "parse_bibtex")
    user_input: str | None # 原始用户输入
    search_query: str | None # 搜索任务的查询词
    search_method: str | None # 搜索方法偏好 ("scholarly" or "qwen")
    literature_results: list | None # 文献搜索结果
    summary: str | None # 文献摘要结果
    citations: list | None # 引用生成结果
    analysis_results: dict | None # 数据分析结果
    text_to_polish: str | None # 需要润色的文本
    paper_to_summarize_index: int | None # 需要总结的文献在 literature_results 中的索引
    paper_to_cite_index: int | None # 需要生成引用的文献索引
    citation_style: str | None # 引用格式
    bibtex_input: str | None # 用户输入的 BibTeX 文本
    pdf_path: str | None # PDF 文件路径
    pdf_sections: dict | None # PDF 章节内容
    pdf_analysis: dict | None # PDF 分析结果

# 定义各个节点函数，接收 tools 和 state
def scholarly_search_node(state: AgentState, tools: AcademicTools) -> AgentState:
    """使用 scholarly 进行文献检索节点"""
    print("[DEBUG] 进入 scholarly_search_node")
    search_query = state.get("search_query")
    if not search_query:
        print("[DEBUG] scholarly_search_node: 缺少搜索查询词")
        return {**state, "literature_results": []}
        
    try:
        # 调用 AcademicTools 中的 scholarly 搜索方法
        results = tools.search_papers(search_query)
        print(f"[DEBUG] scholarly_search_node: 找到 {len(results)} 篇文献")
        return {**state, "literature_results": results}
    except Exception as e:
        print(f"[DEBUG] scholarly_search_node 执行失败: {str(e)}")
        return {**state, "literature_results": []}

def qwen_search_node(state: AgentState, tools: AcademicTools) -> AgentState:
    """使用 Qwen 联网搜索进行文献检索节点"""
    print("[DEBUG] 进入 qwen_search_node")
    search_query = state.get("search_query")
    if not search_query:
        print("[DEBUG] qwen_search_node: 缺少搜索查询词")
        return {**state, "literature_results": []}
        
    try:
        # 调用 AcademicTools 中的 Qwen 联网搜索方法
        results = tools.qwen_search_papers(search_query)
        print(f"[DEBUG] qwen_search_node: 找到 {len(results)} 篇文献")
        return {**state, "literature_results": results}
    except Exception as e:
        print(f"[DEBUG] qwen_search_node 执行失败: {str(e)}")
        return {**state, "literature_results": []}

def parse_bibtex_node(state: AgentState, tools: AcademicTools) -> AgentState:
    """解析 BibTeX 文本节点"""
    print("[DEBUG] 进入 parse_bibtex_node")
    bibtex_input = state.get("bibtex_input")
    
    if not bibtex_input:
        print("[DEBUG] parse_bibtex_node: 缺少 BibTeX 输入")
        return {**state, "literature_results": []}
        
    try:
        # 调用 AcademicTools 中的 parse_bibtex 方法
        results = tools.parse_bibtex(bibtex_input)
        print(f"[DEBUG] parse_bibtex_node: 解析出 {len(results)} 篇文献")
        return {**state, "literature_results": results} # 将解析结果存入 literature_results
    except Exception as e:
        print(f"[DEBUG] parse_bibtex_node 执行失败: {str(e)}")
        return {**state, "literature_results": []}

def summarize_and_explain_node(state: AgentState, tools: AcademicTools) -> AgentState:
    """文献摘要与术语解释节点"""
    print("[DEBUG] 进入 summarize_and_explain_node")
    literature_results = state.get("literature_results")
    paper_index = state.get("paper_to_summarize_index")
    
    if literature_results is None or paper_index is None or paper_index < 0 or paper_index >= len(literature_results):
        print("[DEBUG] summarize_and_explain_node: 无效的文献索引或搜索结果")
        return {**state, "summary": "无法生成摘要，请先进行文献搜索或提供有效的文献信息。"}
        
    try:
        paper_to_summarize = literature_results[paper_index]
        # 调用 AcademicTools 中的 summarize_paper 方法
        summary = tools.summarize_paper(paper_to_summarize)
        print("[DEBUG] summarize_and_explain_node: 摘要生成完成")
        return {**state, "summary": summary}
    except Exception as e:
        print(f"[DEBUG] summarize_and_explain_node 执行失败: {str(e)}")
        return {**state, "summary": f"生成摘要时发生错误: {str(e)}"}

def check_citation_validity_node(state: AgentState, tools: AcademicTools) -> AgentState:
    """引用与元数据验证节点"""
    print("[DEBUG] 进入 check_citation_validity_node")
    # TODO: 实现引用验证逻辑
    # 当前不做实际验证，直接返回状态
    print("[DEBUG] check_citation_validity_node: 引用验证（待实现）")
    return state

def polish_writing_node(state: AgentState, tools: AcademicTools) -> AgentState:
    """语言提升与翻译节点"""
    print("[DEBUG] 进入 polish_writing_node")
    text_to_polish = state.get("text_to_polish")
    
    if not text_to_polish:
        print("[DEBUG] polish_writing_node: 没有需要润色的文本")
        return {**state, "polished_text": "没有提供需要润色的文本。"}
        
    try:
        # 调用 AcademicTools 中的 polish_text 方法
        polished_text = tools.polish_text(text_to_polish)
        print("[DEBUG] polish_writing_node: 文本润色完成")
        return {**state, "polished_text": polished_text}
    except Exception as e:
        print(f"[DEBUG] polish_writing_node 执行失败: {str(e)}")
        return {**state, "polished_text": f"文本润色失败: {str(e)}"}

def analyze_data_node(state: AgentState, tools: AcademicTools) -> AgentState:
    """数据解析节点"""
    print("[DEBUG] 进入 analyze_data_node")
    # TODO: 实现数据分析逻辑
    print("[DEBUG] analyze_data_node: 数据分析（待实现）")
    # 目前没有实际数据和分析逻辑，直接返回状态
    return state # {**state, "analysis_results": "数据分析功能待实现"}

def generate_references_node(state: AgentState, tools: AcademicTools) -> AgentState:
    """格式化引用节点"""
    print("[DEBUG] 进入 generate_references_node")
    literature_results = state.get("literature_results")
    paper_index = state.get("paper_to_cite_index")
    style = state.get("citation_style", "apa")
    
    if literature_results is None or paper_index is None or paper_index < 0 or paper_index >= len(literature_results):
         print("[DEBUG] generate_references_node: 无效的文献索引或搜索结果")
         return {**state, "citations": ["无法生成引用，请先进行文献搜索或提供有效的文献信息。"]}
         
    try:
        paper_to_cite = literature_results[paper_index]
        # 调用 AcademicTools 中的 generate_reference 方法
        citation = tools.generate_reference(paper_to_cite, style)
        print("[DEBUG] generate_references_node: 引用生成完成")
        return {**state, "citations": [citation]}
    except Exception as e:
        print(f"[DEBUG] generate_references_node 执行失败: {str(e)}")
        return {**state, "citations": [f"生成引用时发生错误: {str(e)}"]}

def parse_pdf_node(state: AgentState, tools: AcademicTools) -> AgentState:
    """解析 PDF 文件节点"""
    print("[DEBUG] 进入 parse_pdf_node")
    pdf_path = state.get("pdf_path")
    
    if not pdf_path:
        print("[DEBUG] parse_pdf_node: 缺少 PDF 文件路径")
        return {**state, "pdf_sections": {}}
        
    try:
        # 调用 AcademicTools 中的 PDF 解析方法
        sections = tools.extract_pdf_sections(pdf_path)
        print(f"[DEBUG] parse_pdf_node: 成功提取 {len(sections)} 个章节")
        return {**state, "pdf_sections": sections}
    except Exception as e:
        print(f"[DEBUG] parse_pdf_node 执行失败: {str(e)}")
        return {**state, "pdf_sections": {}}

def analyze_pdf_node(state: AgentState, tools: AcademicTools) -> AgentState:
    """分析 PDF 内容节点"""
    print("[DEBUG] 进入 analyze_pdf_node")
    pdf_path = state.get("pdf_path")
    
    if not pdf_path:
        print("[DEBUG] analyze_pdf_node: 缺少 PDF 文件路径")
        return {**state, "pdf_analysis": {}}
        
    try:
        # 调用 AcademicTools 中的 PDF 分析方法
        analysis = tools.analyze_pdf_content(pdf_path)
        print("[DEBUG] analyze_pdf_node: 成功分析 PDF 内容")
        return {**state, "pdf_analysis": analysis}
    except Exception as e:
        print(f"[DEBUG] analyze_pdf_node 执行失败: {str(e)}")
        return {**state, "pdf_analysis": {}}

# 定义路由函数
def route_by_task_type(state: AgentState) -> str:
    print(f"[DEBUG] 进入路由: route_by_task_type, task_type: {state.get('task_type')}")
    task_type = state.get("task_type")
    
    if task_type == "search":
        search_method = state.get("search_method")
        if search_method == "scholarly":
            return "scholarly_search"
        elif search_method == "qwen":
            return "qwen_search"
        else:
            print("[DEBUG] 未知或未指定搜索方法，路由到 scholarly_search")
            return "scholarly_search" # 默认使用 scholarly
    elif task_type == "parse_bibtex":
        return "parse_bibtex"
    elif task_type == "parse_pdf": # 添加 PDF 解析路由
        return "parse_pdf"
    elif task_type == "analyze_pdf": # 添加 PDF 分析路由
        return "analyze_pdf"
    elif task_type == "summary":
        if state.get("literature_results"):
            return "summarize_and_explain"
        else:
            print("[DEBUG] 总结任务：缺少文献结果，路由到结束")
            return "__END__"
    elif task_type == "references":
        if state.get("literature_results"):
            return "generate_references"
        else:
            print("[DEBUG] 生成引用任务：缺少文献结果，路由到结束")
            return "__END__"
    elif task_type == "writing":
        return "polish_writing"
    elif task_type == "analysis":
        return "analyze_data"
    else:
        print("[DEBUG] 未知任务类型，结束工作流")
        return "__END__"

# 创建工作流图
def create_academic_workflow() -> Graph:
    # 创建工作流
    workflow = StateGraph(AgentState)
    
    # 实例化工具
    tools = AcademicTools()
    
    # 添加节点，并绑定工具
    workflow.add_node("scholarly_search", lambda state: scholarly_search_node(state, tools))
    workflow.add_node("qwen_search", lambda state: qwen_search_node(state, tools))
    workflow.add_node("parse_bibtex", lambda state: parse_bibtex_node(state, tools))
    workflow.add_node("parse_pdf", lambda state: parse_pdf_node(state, tools)) # 添加 PDF 解析节点
    workflow.add_node("analyze_pdf", lambda state: analyze_pdf_node(state, tools)) # 添加 PDF 分析节点
    workflow.add_node("summarize_and_explain", lambda state: summarize_and_explain_node(state, tools))
    workflow.add_node("check_citation_validity", lambda state: check_citation_validity_node(state, tools))
    workflow.add_node("polish_writing", lambda state: polish_writing_node(state, tools))
    workflow.add_node("analyze_data", lambda state: analyze_data_node(state, tools))
    workflow.add_node("generate_references", lambda state: generate_references_node(state, tools))
    
    # 设置入口点和路由逻辑
    workflow.set_entry_point("route_by_task_type")
    
    # 添加条件边，从路由函数到各个任务节点
    workflow.add_conditional_edges(
        "route_by_task_type",
        route_by_task_type,
        {
            "scholarly_search": "scholarly_search",
            "qwen_search": "qwen_search",
            "parse_bibtex": "parse_bibtex",
            "parse_pdf": "parse_pdf", # 添加 PDF 解析路由
            "analyze_pdf": "analyze_pdf", # 添加 PDF 分析路由
            "summarize_and_explain": "summarize_and_explain",
            "polish_writing": "polish_writing",
            "analyze_data": "analyze_data",
            "generate_references": "generate_references",
            "__END__": "__END__"
        }
    )
    
    # 添加各任务节点完成后的路由
    workflow.add_edge("scholarly_search", "__END__")
    workflow.add_edge("qwen_search", "__END__")
    workflow.add_edge("parse_bibtex", "__END__")
    workflow.add_edge("parse_pdf", "__END__") # PDF 解析完成后结束
    workflow.add_edge("analyze_pdf", "__END__") # PDF 分析完成后结束
    workflow.add_edge("summarize_and_explain", "__END__")
    workflow.add_edge("check_citation_validity", "__END__")
    workflow.add_edge("polish_writing", "__END__")
    workflow.add_edge("analyze_data", "__END__")
    workflow.add_edge("generate_references", "__END__")
    
    return workflow.compile()

# 主函数 (cli.py 会导入和使用 create_academic_workflow)
# def main():
#     # 创建工作流实例
#     workflow = create_academic_workflow()
    
#     # 初始化状态 (CLI 中会处理)
#     # initial_state = {
#     #     "messages": [],
#     #     "task_type": None,
#     #     "literature_results": None,
#     #     "summary": None,
#     #     "citations": None,
#     #     "analysis_results": None
#     # }
    
#     # # 运行工作流
#     # result = workflow.invoke(initial_state)
#     # return result

# if __name__ == "__main__":
#     main() # CLI 中会调用 main 函数 