from scholarly import scholarly
# from dashscope import Generation
# import dashscope
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from openai import OpenAI # 导入 OpenAI 客户端
import json # 添加导入 json 库

# 加载环境变量
load_dotenv()

class AcademicTools:
    def __init__(self):
        # 从环境变量加载配置
        self.api_key = os.getenv('DASHSCOPE_API_KEY') or os.getenv('QWEN_API_KEY')
        if not self.api_key:
            raise ValueError("请设置 DASHSCOPE_API_KEY 或 QWEN_API_KEY 环境变量")
            
        self.model_name = os.getenv('QWEN_MODEL_NAME', 'qwen3-235b-a22b')
        self.temperature = float(os.getenv('QWEN_TEMPERATURE', '0.5'))
        self.max_tokens = int(os.getenv('QWEN_MAX_TOKENS', '16384'))
        
        # 初始化 OpenAI 客户端，指向 DashScope 兼容模式
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    
    def search_papers(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """搜索学术论文并生成友好摘要"""
        results = []
        try:
            # 1. 使用 scholarly 进行谷歌学术搜索
            print(f"[DEBUG] 使用 scholarly 搜索: {query}")
            search_query = scholarly.search_pubs(query)
            
            scholarly_results = []
            for _ in range(max_results):
                try:
                    paper = next(search_query)
                    # 使用 get 方法安全地获取属性
                    scholarly_results.append({
                        'title': getattr(paper, 'bib', {}).get('title', ''),
                        'authors': getattr(paper, 'bib', {}).get('author', ''),
                        'year': getattr(paper, 'bib', {}).get('year', ''),
                        'abstract': getattr(paper, 'bib', {}).get('abstract', ''),
                        'url': getattr(paper, 'bib', {}).get('url', '')
                    })
                except StopIteration:
                    break
                    
            print(f"[DEBUG] scholarly 找到 {len(scholarly_results)} 篇文献")
                    
            # 2. 使用 Qwen API 处理搜索结果，生成友好摘要
            for paper in scholarly_results:
                title = paper.get('title', '未知标题')
                abstract = paper.get('abstract', '无摘要')
                
                # 如果没有摘要，跳过 Qwen 处理
                if not abstract or abstract == '无摘要':
                    results.append(paper)
                    continue
                    
                prompt = f"""
                请用一两句话概括以下论文的摘要，使其更易于快速理解。只返回概括性的句子，不要添加任何额外说明。
                
                论文标题: {title}
                论文摘要: {abstract}
                """
                
                messages = [
                    {"role": "system", "content": "你是一个论文摘要精炼助手，请用简洁友好的语言概括提供的摘要。"},
                    {"role": "user", "content": prompt}
                ]
                
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        temperature=0.3, # 较低温度以保持摘要准确性
                        max_tokens=200, # 限制摘要长度
                        extra_body={"enable_thinking": False}
                    )
                    
                    friendly_summary = ""
                    if response and response.choices and response.choices[0].message.content:
                        friendly_summary = response.choices[0].message.content.strip()
                        
                    # 将友好摘要添加到结果中
                    paper['friendly_summary'] = friendly_summary
                    results.append(paper)
                    
                except Exception as e:
                    print(f"[DEBUG] 使用 Qwen 生成友好摘要时出错: {str(e)}")
                    # 如果出错，仍然添加原始文献信息
                    results.append(paper)

            return results
                
        except Exception as e:
            print(f"[DEBUG] 搜索论文时发生错误: {str(e)}")
            return []

    def summarize_paper(self, paper: Dict[str, Any]) -> str:
        """生成论文摘要"""
        # 确保必要的字段存在
        title = paper.get('title', '未知标题')
        authors = paper.get('authors', '未知作者')
        year = paper.get('year', '未知年份')
        # 优先使用 friendly_summary，如果没有，再使用原始 abstract
        abstract = paper.get('friendly_summary', paper.get('abstract', '无摘要'))
        
        prompt = f"""
        请对以下论文进行详细摘要：
        标题：{title}
        作者：{authors}
        年份：{year}
        摘要：{abstract}
        
        请提供：
        1. 主要研究问题
        2. 研究方法
        3. 主要发现
        4. 研究意义
        """
        
        messages = [
            {"role": "system", "content": "你是一个学术助手，请根据提供的论文信息生成详细摘要。"},
            {"role": "user", "content": prompt}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                extra_body={"enable_thinking": False}
            )
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            else:
                print("[DEBUG] 无法生成摘要，Qwen API 返回为空或格式不正确")
                return "无法生成摘要，请检查 API 响应"
        except Exception as e:
            print(f"[DEBUG] 生成摘要时出错: {str(e)}")
            return "生成摘要时发生错误"

    def identify_intent(self, user_input: str) -> Dict[str, Any]:
        """识别用户输入意图并提取参数"""
        prompt = f"""
        你是一个负责理解用户关于学术研究意图的助手。请分析用户输入的文本，识别用户的意图以及任何相关的参数。支持的意图包括：
        - search: 搜索学术文献。参数：query (搜索关键词)。
        - summarize: 总结指定文献。参数：paper_id (文献ID)。
        - polish: 润色文本。参数：text (需要润色的文本)。
        - analyze: 数据分析。参数：data_type (数据类型，如 descriptive)。
        - cite: 生成文献引用。参数：paper_id (文献ID)，style (引用格式，apa或mla，默认为apa)。
        - help: 查看帮助信息。
        - exit: 退出程序。
        - unknown: 无法识别的意图。

        请以 JSON 格式返回结果，包含以下字段：
        - intent: 识别到的意图（search, summarize, polish, analyze, cite, help, exit, unknown）。
        - parameters: 一个字典，包含与意图相关的参数。如果意图没有参数，parameters 字段应为空字典 {{}}。

        用户输入：{user_input}
        
        请只返回 JSON 格式的输出，不要包含任何额外说明文本。
        """
        
        messages = [
            {"role": "system", "content": "你是一个帮助用户识别学术研究意图的助手，请严格按照要求以 JSON 格式输出意图和参数。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.2, # 使用较低的温度以获得更稳定的意图识别结果
                max_tokens=200, # 限制 token 数，意图识别通常不需要很多 token
                extra_body={"enable_thinking": False}
            )
            
            if response and response.choices and response.choices[0].message.content:
                text_content = response.choices[0].message.content.strip()
                # 尝试清理 Markdown 代码块
                if text_content.startswith('```json'):
                    text_content = text_content[len('```json'):].strip()
                if text_content.endswith('```'):
                    text_content = text_content[:-len('```')].strip()
                    
                try:
                    intent_data = json.loads(text_content)
                    # 验证 JSON 结构
                    if isinstance(intent_data, dict) and "intent" in intent_data and "parameters" in intent_data:
                        return intent_data
                    else:
                        print(f"API 返回的 JSON 格式不符合预期: {text_content}")
                        return {"intent": "unknown", "parameters": {}}
                except json.JSONDecodeError:
                    print(f"无法解析API返回的JSON数据进行意图识别: {text_content}")
                    return {"intent": "unknown", "parameters": {}}
            else:
                print("意图识别 API 返回为空或格式不正确")
                return {"intent": "unknown", "parameters": {}}
                
        except Exception as e:
            print(f"意图识别时出错: {str(e)}")
            return {"intent": "unknown", "parameters": {}}

    def check_citation(self, citation: Dict[str, Any]) -> bool:
        """验证引用信息"""
        required_fields = ['title', 'authors', 'year']
        return all(field in citation and citation[field] for field in required_fields)

    def polish_text(self, text: str, target_language: str = 'zh') -> str:
        """润色文本"""
        messages = [
            {"role": "system", "content": "你是一个学术写作助手，请对提供的文本进行润色和优化。"},
            {"role": "user", "content": f"""
            请对以下学术文本进行润色和优化：
            {text}
            
            要求：
            1. 保持学术严谨性
            2. 提高语言流畅度
            3. 确保逻辑连贯
            4. 使用规范的学术用语
            """}
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                extra_body={"enable_thinking": False}
            )
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            else:
                return "无法润色文本，请检查 API 响应"
        except Exception as e:
            print(f"润色文本时出错: {str(e)}")
            return "润色文本时发生错误"

    def analyze_data(self, data: pd.DataFrame, analysis_type: str) -> Dict[str, Any]:
        """数据分析"""
        results = {}
        if analysis_type == 'descriptive':
            results['summary'] = data.describe().to_dict()
            results['correlation'] = data.corr().to_dict()
        elif analysis_type == 'regression':
            # TODO: 实现回归分析
            pass
        return results

    def generate_reference(self, paper: Dict[str, Any], style: str = 'apa') -> str:
        """生成格式化引用"""
        # 确保必要的字段存在
        authors = paper.get('authors', '未知作者')
        year = paper.get('year', '未知年份')
        title = paper.get('title', '未知标题')
        journal = paper.get('journal', '')
        
        if style == 'apa':
            return f"{authors} ({year}). {title}. {journal}"
        elif style == 'mla':
            return f"{authors}. \"{title}.\" {journal} {year}"
        else:
            return f"{authors} ({year}). {title}" 