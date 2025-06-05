from scholarly import scholarly
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
import pandas as pd
import numpy as np

class AcademicTools:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview")
    
    def search_papers(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """搜索学术论文"""
        try:
            search_query = scholarly.search_pubs(query)
            results = []
            for _ in range(max_results):
                try:
                    paper = next(search_query)
                    results.append({
                        'title': paper.bib.get('title', ''),
                        'authors': paper.bib.get('author', ''),
                        'year': paper.bib.get('year', ''),
                        'abstract': paper.bib.get('abstract', ''),
                        'url': paper.bib.get('url', '')
                    })
                except StopIteration:
                    break
            return results
        except Exception as e:
            print(f"搜索论文时出错: {str(e)}")
            return []

    def summarize_paper(self, paper: Dict[str, Any]) -> str:
        """生成论文摘要"""
        prompt = f"""
        请对以下论文进行摘要：
        标题：{paper['title']}
        作者：{paper['authors']}
        年份：{paper['year']}
        摘要：{paper['abstract']}
        
        请提供：
        1. 主要研究问题
        2. 研究方法
        3. 主要发现
        4. 研究意义
        """
        response = self.llm.invoke(prompt)
        return response.content

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
        response = self.llm.invoke(prompt)
        return response.content

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
        if style == 'apa':
            return f"{paper['authors']} ({paper['year']}). {paper['title']}. {paper.get('journal', '')}"
        elif style == 'mla':
            return f"{paper['authors']}. \"{paper['title']}.\" {paper.get('journal', '')} {paper['year']}"
        else:
            return f"{paper['authors']} ({paper['year']}). {paper['title']}" 