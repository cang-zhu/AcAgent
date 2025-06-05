from scholarly import scholarly
# from dashscope import Generation
# import dashscope
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from openai import OpenAI # 导入 OpenAI 客户端
import json # 添加导入 json 库
import fitz  # PyMuPDF

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

    def qwen_search_papers(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """使用 Qwen 模型自带联网搜索功能搜索学术论文"""
        results = []
        try:
            print(f"[DEBUG] 使用 Qwen 联网搜索: {query}")
            messages = [
                {"role": "system", "content": "你是一个帮助用户搜索学术论文的助手，请根据用户的搜索请求利用你的联网能力查找相关文献。"},
                {"role": "user", "content": f"请帮我搜索关于\"{query}\"的学术论文。请提供找到的文献的标题、作者、发表年份、摘要和可能的链接。请尝试找到至少 {max_results} 篇相关文献。"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.5,
                max_tokens=self.max_tokens,
                extra_body={"enable_search": True}
            )
            
            if response and response.choices and response.choices[0].message.content:
                raw_content = response.choices[0].message.content
                print(f"[DEBUG] Qwen 联网搜索原始返回内容: {raw_content[:500]}...")
                
                # 尝试提示模型以 JSON 格式返回，并解析
                prompt_for_json = f"""
                请根据您刚才关于\"{query}\"的联网搜索结果，将找到的文献信息 정리하여 以 JSON 数组格式返回。每个对象包含以下字段：title, authors (作者列表), year, abstract, url (如果可用)。如果找不到文献，返回空数组 []。
                """
                
                messages_for_json = [
                     {"role": "system", "content": "你是一个学术文献信息提取助手，请将提供的文本中的文献信息转化为指定的 JSON 格式。"},
                     {"role": "user", "content": f"原始搜索结果:\n{raw_content}\n\n请将其转换为 JSON 数组格式，字段包括 title, authors, year, abstract, url。"}
                ]
                
                try:
                    response_json = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages_for_json,
                        temperature=0.1,
                        max_tokens=self.max_tokens,
                        extra_body={"enable_thinking": False}
                    )
                    
                    if response_json and response_json.choices and response_json.choices[0].message.content:
                        json_text = response_json.choices[0].message.content.strip()
                        # 清理可能的Markdown代码块
                        if json_text.startswith('```json'):
                             json_text = json_text[len('```json'):].strip()
                        if json_text.endswith('```'):
                             json_text = json_text[:-len('```')].strip()
                             
                        parsed_results = json.loads(json_text)
                        if isinstance(parsed_results, list):
                             # 进一步处理结果，如生成 friendly_summary (可选)
                             final_results = []
                             for paper_info in parsed_results:
                                 # 在这里可以添加生成 friendly_summary 的逻辑，或者在工作流后续步骤处理
                                 final_results.append(paper_info)
                             return final_results[:max_results]
                        else:
                             print(f"[DEBUG] Qwen 联网搜索 JSON 解析结果非列表: {parsed_results}")
                             return []
                    else:
                         print("[DEBUG] Qwen 联网搜索 JSON 提取失败或返回为空")
                         return []
                         
                except json.JSONDecodeError:
                    print(f"[DEBUG] 无法解析 Qwen 联网搜索返回的 JSON 数据: {json_text}")
                    return []
                except Exception as json_e:
                     print(f"[DEBUG] 处理 Qwen 联网搜索结果时发生错误: {str(json_e)}")
                     return []
            else:
                print("[DEBUG] Qwen 联网搜索 API 返回为空或格式不正确")
                return []
                
        except Exception as e:
            print(f"[DEBUG] Qwen 联网搜索时发生错误: {str(e)}")
            return []

    def parse_bibtex(self, bibtex_string: str) -> List[Dict[str, Any]]:
        """解析 BibTeX 字符串，提取文献信息"""
        results = []
        try:
            import bibtexparser
            
            # 解析 BibTeX 字符串
            bib_database = bibtexparser.loads(bibtex_string)
            
            print(f"[DEBUG] BibTeX 解析找到 {len(bib_database.entries)} 条目")
            
            # 转换 BibTeX 条目为内部格式
            for entry in bib_database.entries:
                # 提取常用字段，并进行一些基本的清理和格式化
                title = entry.get('title', '').replace('{', '').replace('}', '')
                authors_str = entry.get('author', '')
                authors = [a.strip() for a in authors_str.replace('and', ',').split(',')] if authors_str else []
                year = entry.get('year', '')
                abstract = entry.get('abstract', '').replace('{', '').replace('}', '')
                # 尝试从多个字段获取 URL
                url = entry.get('url', entry.get('link', entry.get('doi', '')))
                
                # 创建内部格式字典
                paper_info = {
                    'title': title,
                    'authors': authors,
                    'year': year,
                    'abstract': abstract,
                    'url': url,
                    'source_type': 'bibtex' # 标记来源
                }
                
                results.append(paper_info)
                
            print(f"[DEBUG] BibTeX 解析并格式化 {len(results)} 篇文献信息")
            return results
        
        except ImportError:
             print("[DEBUG] 错误：未安装 bibtexparser 库。请运行 pip install bibtexparser")
             return []
        except Exception as e:
            print(f"[DEBUG] 解析 BibTeX 时出错: {str(e)}")
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

    def test_placeholder(self):
        """这是一个占位函数"""
        print("Placeholder function called")

    def parse_pdf(self, pdf_path: str, max_pages: Optional[int] = None) -> Dict[str, Any]:
        """解析 PDF 文件并提取内容
        
        Args:
            pdf_path: PDF 文件路径
            max_pages: 最大解析页数，None 表示解析所有页面
            
        Returns:
            Dict 包含以下字段：
            - title: 文档标题
            - text: 完整文本内容
            - metadata: 文档元数据
            - page_count: 总页数
            - parsed_pages: 实际解析的页数
        """
        try:
            # 打开 PDF 文件
            doc = fitz.open(pdf_path)
            
            # 获取文档信息
            metadata = doc.metadata
            title = metadata.get('title', os.path.basename(pdf_path))
            page_count = len(doc)
            
            # 确定要解析的页数
            pages_to_parse = min(max_pages, page_count) if max_pages else page_count
            
            # 提取文本
            text = ""
            for page_num in range(pages_to_parse):
                page = doc[page_num]
                text += page.get_text()
            
            # 关闭文档
            doc.close()
            
            return {
                'title': title,
                'text': text,
                'metadata': metadata,
                'page_count': page_count,
                'parsed_pages': pages_to_parse
            }
            
        except Exception as e:
            print(f"[DEBUG] PDF 解析错误: {str(e)}")
            return {
                'title': os.path.basename(pdf_path),
                'text': '',
                'metadata': {},
                'page_count': 0,
                'parsed_pages': 0,
                'error': str(e)
            }

    def extract_pdf_sections(self, pdf_path: str, section_keywords: List[str] = None) -> Dict[str, str]:
        """从 PDF 中提取特定章节
        
        Args:
            pdf_path: PDF 文件路径
            section_keywords: 章节关键词列表，如 ['abstract', 'introduction', 'conclusion']
            
        Returns:
            Dict 包含章节名称和对应的内容
        """
        if section_keywords is None:
            section_keywords = ['abstract', 'introduction', 'methodology', 'results', 'conclusion']
            
        try:
            # 首先解析整个 PDF
            pdf_content = self.parse_pdf(pdf_path)
            full_text = pdf_content['text'].lower()
            
            # 提取各个章节
            sections = {}
            for keyword in section_keywords:
                # 使用 Qwen API 帮助定位章节
                prompt = f"""
                请从以下论文文本中提取 {keyword} 章节的内容。只返回该章节的文本，不要添加任何额外说明。
                
                论文文本：
                {full_text[:5000]}  # 限制文本长度以避免 token 超限
                """
                
                messages = [
                    {"role": "system", "content": "你是一个论文章节提取助手，请准确提取指定章节的内容。"},
                    {"role": "user", "content": prompt}
                ]
                
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        temperature=0.3,
                        max_tokens=1000,
                        extra_body={"enable_thinking": False}
                    )
                    
                    if response and response.choices and response.choices[0].message.content:
                        sections[keyword] = response.choices[0].message.content.strip()
                    else:
                        sections[keyword] = ""
                        
                except Exception as e:
                    print(f"[DEBUG] 提取 {keyword} 章节时出错: {str(e)}")
                    sections[keyword] = ""
            
            return sections
            
        except Exception as e:
            print(f"[DEBUG] 提取 PDF 章节时出错: {str(e)}")
            return {keyword: "" for keyword in section_keywords}

    def analyze_pdf_content(self, pdf_path: str) -> Dict[str, Any]:
        """分析 PDF 内容并生成摘要
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            Dict 包含分析结果：
            - summary: 文档摘要
            - key_points: 关键点列表
            - methodology: 研究方法
            - findings: 主要发现
        """
        try:
            # 解析 PDF
            pdf_content = self.parse_pdf(pdf_path)
            
            # 使用 Qwen API 分析内容
            prompt = f"""
            请分析以下学术论文内容，并提供：
            1. 简要摘要
            2. 3-5个关键点
            3. 研究方法
            4. 主要发现
            
            论文内容：
            {pdf_content['text'][:3000]}  # 限制文本长度
            
            请以 JSON 格式返回结果，包含以下字段：
            - summary: 摘要
            - key_points: 关键点列表
            - methodology: 研究方法
            - findings: 主要发现
            """
            
            messages = [
                {"role": "system", "content": "你是一个学术论文分析助手，请提供结构化的分析结果。"},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.5,
                max_tokens=2000,
                extra_body={"enable_thinking": False}
            )
            
            if response and response.choices and response.choices[0].message.content:
                try:
                    analysis = json.loads(response.choices[0].message.content)
                    return analysis
                except json.JSONDecodeError:
                    print("[DEBUG] 无法解析分析结果 JSON")
                    return {
                        'summary': '无法生成摘要',
                        'key_points': [],
                        'methodology': '无法提取研究方法',
                        'findings': '无法提取主要发现'
                    }
            else:
                return {
                    'summary': '无法生成摘要',
                    'key_points': [],
                    'methodology': '无法提取研究方法',
                    'findings': '无法提取主要发现'
                }
                
        except Exception as e:
            print(f"[DEBUG] 分析 PDF 内容时出错: {str(e)}")
            return {
                'summary': f'分析过程中出错: {str(e)}',
                'key_points': [],
                'methodology': '无法提取研究方法',
                'findings': '无法提取主要发现'
            } 