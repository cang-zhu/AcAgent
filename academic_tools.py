from scholarly import scholarly
from dashscope import Generation
import dashscope
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

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
        self.max_tokens = int(os.getenv('QWEN_MAX_TOKENS', '128000'))
        
        # 设置 Qwen API key
        dashscope.api_key = self.api_key
    
    def search_papers(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """搜索学术论文"""
        try:
            search_query = scholarly.search_pubs(query)
            results = []
            for _ in range(max_results):
                try:
                    paper = next(search_query)
                    # 使用 get 方法安全地获取属性
                    results.append({
                        'title': getattr(paper, 'bib', {}).get('title', ''),
                        'authors': getattr(paper, 'bib', {}).get('author', ''),
                        'year': getattr(paper, 'bib', {}).get('year', ''),
                        'abstract': getattr(paper, 'bib', {}).get('abstract', ''),
                        'url': getattr(paper, 'bib', {}).get('url', '')
                    })
                except StopIteration:
                    break
            return results
        except Exception as e:
            print(f"搜索论文时出错: {str(e)}")
            return []

    def summarize_paper(self, paper: Dict[str, Any]) -> str:
        """生成论文摘要"""
        # 确保必要的字段存在
        title = paper.get('title', '未知标题')
        authors = paper.get('authors', '未知作者')
        year = paper.get('year', '未知年份')
        abstract = paper.get('abstract', '无摘要')
        
        prompt = f"""
        请对以下论文进行摘要：
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
        try:
            response = Generation.call(
                model=self.model_name,
                prompt=prompt,
                result_format='message',
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            if response and response.output and response.output.text:
                return response.output.text
            else:
                return "无法生成摘要，请检查 API 响应"
        except Exception as e:
            print(f"生成摘要时出错: {str(e)}")
            return "生成摘要时发生错误"

    def check_citation(self, citation: Dict[str, Any]) -> bool:
        """验证引用信息"""
        required_fields = ['title', 'authors', 'year']
        return all(field in citation and citation[field] for field in required_fields)

    def polish_text(self, text: str, target_language: str = 'zh') -> str:
        """润色文本"""
        prompt = f"""
        请对以下学术文本进行润色和优化：
        {text}
        
        要求：
        1. 保持学术严谨性
        2. 提高语言流畅度
        3. 确保逻辑连贯
        4. 使用规范的学术用语
        """
        try:
            response = Generation.call(
                model=self.model_name,
                prompt=prompt,
                result_format='message',
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            if response and response.output and response.output.text:
                return response.output.text
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