import unittest
from academic_tools import AcademicTools
from academic_agent import create_academic_workflow

class TestAcademicAgent(unittest.TestCase):
    def setUp(self):
        self.tools = AcademicTools()
        self.workflow = create_academic_workflow()

    def test_search_papers(self):
        """测试文献搜索功能"""
        results = self.tools.search_papers("人工智能教育应用")
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)
        if results:
            self.assertIn('title', results[0])
            self.assertIn('abstract', results[0])

    def test_summarize_paper(self):
        """测试文献摘要功能"""
        paper = {
            'title': 'Test Paper',
            'authors': 'Test Author',
            'year': '2024',
            'abstract': 'This is a test paper about AI in education.'
        }
        summary = self.tools.summarize_paper(paper)
        self.assertIsNotNone(summary)
        self.assertIsInstance(summary, str)

    def test_polish_text(self):
        """测试文本润色功能"""
        text = "这是一个测试文本，需要润色。"
        polished = self.tools.polish_text(text)
        self.assertIsNotNone(polished)
        self.assertIsInstance(polished, str)

    def test_generate_reference(self):
        """测试引用生成功能"""
        paper = {
            'title': 'Test Paper',
            'authors': 'Test Author',
            'year': '2024',
            'journal': 'Test Journal'
        }
        apa_ref = self.tools.generate_reference(paper, 'apa')
        mla_ref = self.tools.generate_reference(paper, 'mla')
        
        self.assertIsNotNone(apa_ref)
        self.assertIsNotNone(mla_ref)
        self.assertIsInstance(apa_ref, str)
        self.assertIsInstance(mla_ref, str)

    def test_workflow(self):
        """测试工作流功能"""
        initial_state = {
            "messages": [],
            "task_type": "writing",
            "literature_results": None,
            "summary": None,
            "citations": None,
            "analysis_results": None
        }
        
        result = self.workflow.invoke(initial_state)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

if __name__ == '__main__':
    unittest.main() 