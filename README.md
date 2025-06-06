# AcAgent - 智能学术助手

这是一个基于 LangGraph 和 Qwen API 构建的学术智能体，能够帮助研究人员进行文献检索、论文分析、写作润色等学术工作。

## 功能特点

- 文献检索与摘要
- 引用验证与格式化
- 学术写作润色
- 数据分析支持
- 参考文献生成
- BibTeX 文本解析
- PDF 文件处理
  * PDF 文本提取
  * 章节内容识别
  * 智能内容分析
  * 结构化摘要生成
- 支持多轮对话交互

## 安装要求

1. Python 3.8+
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 `.env` 文件并添加以下内容：
```
# Qwen API 配置
QWEN_API_KEY=your_qwen_api_key_here
DASHSCOPE_API_KEY=your_qwen_api_key_here  # 新版 dashscope 需要
QWEN_MODEL_NAME=qwen3-235b-a22b
QWEN_TEMPERATURE=0.5
QWEN_MAX_TOKENS=16384
```

## 使用方法

### 命令行界面

1. 启动智能体：
```bash
python cli.py
```

2. 可用命令：
- `search <关键词>` - 搜索相关文献
- `summarize <文献ID>` - 生成文献摘要
- `polish <文本>` - 润色学术文本
- `analyze <数据类型>` - 分析研究数据
- `cite <文献ID> [格式]` - 生成引用（支持 APA/MLA 格式）
- `parse_bibtex <BibTeX 文本>` - 解析 BibTeX 格式的文献信息
- `parse_pdf <PDF文件路径>` - 解析 PDF 文件并提取内容
- `analyze_pdf <PDF文件路径>` - 分析 PDF 文件内容并生成摘要
- `help` - 显示帮助信息
- `exit` - 退出程序

3. 使用示例：
```
> search 人工智能教育应用
> summarize 1
> polish 这是一段需要润色的学术文本
> analyze descriptive
> cite 1 apa
> parse_bibtex @article{...}
> parse_pdf /path/to/paper.pdf
> analyze_pdf /path/to/paper.pdf
```

### PDF 处理功能

1. PDF 解析功能：
```python
from academic_tools import AcademicTools

tools = AcademicTools()

# 解析 PDF 文件
pdf_content = tools.parse_pdf("path/to/paper.pdf")
print(f"标题: {pdf_content['title']}")
print(f"页数: {pdf_content['page_count']}")
print(f"内容: {pdf_content['text'][:500]}...")  # 显示前500个字符

# 提取特定章节
sections = tools.extract_pdf_sections("path/to/paper.pdf", 
    section_keywords=['abstract', 'introduction', 'conclusion'])
for section, content in sections.items():
    print(f"\n{section.upper()}:")
    print(content[:200] + "...")  # 显示每个章节的前200个字符
```

2. PDF 内容分析：
```python
# 分析 PDF 内容
analysis = tools.analyze_pdf_content("path/to/paper.pdf")
print("摘要:", analysis['summary'])
print("\n关键点:")
for point in analysis['key_points']:
    print(f"- {point}")
print("\n研究方法:", analysis['methodology'])
print("\n主要发现:", analysis['findings'])
```

### 编程接口

1. 基本使用：
```python
from academic_agent import main

# 运行智能体
result = main()
```

2. 自定义工作流：
```python
from academic_agent import create_academic_workflow
from academic_tools import AcademicTools

# 创建工作流实例
workflow = create_academic_workflow()

# 初始化工具
tools = AcademicTools()

# 设置初始状态
initial_state = {
    "messages": [],
    "task_type": "parse_pdf",  # 可选: "writing", "analysis", "references", "parse_pdf", "analyze_pdf"
    "pdf_path": "path/to/paper.pdf",  # PDF 文件路径
    "literature_results": None,
    "summary": None,
    "citations": None,
    "analysis_results": None,
    "pdf_sections": None,
    "pdf_analysis": None
}

# 运行工作流
result = workflow.invoke(initial_state)
```

## 测试说明

项目包含完整的单元测试，可以通过以下命令运行测试：

```bash
python test_agent.py
```

测试用例包括：

1. `test_search_papers`: 测试文献搜索功能
2. `test_summarize_paper`: 测试文献摘要功能
3. `test_polish_text`: 测试文本润色功能
4. `test_generate_reference`: 测试引用生成功能
5. `test_workflow`: 测试工作流功能
6. `test_pdf_parsing`: 测试 PDF 解析功能
   - 验证 PDF 文本提取
   - 检查章节识别
   - 测试元数据提取
7. `test_pdf_analysis`: 测试 PDF 分析功能
   - 验证内容分析
   - 检查摘要生成
   - 测试关键点提取

## 工作流程

1. 文献检索 (search_literature)
2. 摘要与解释 (summarize_and_explain)
3. 引用验证 (check_citation_validity)
4. PDF 处理
   - PDF 解析 (parse_pdf)
   - 内容分析 (analyze_pdf)
5. 根据任务类型执行：
   - 写作润色 (polish_writing)
   - 数据分析 (analyze_data)
   - 生成参考文献 (generate_references)

## 技术特点

- 使用 Qwen API 进行自然语言处理
- 集成 scholarly 库进行专业的谷歌学术文献检索
- 使用 PyMuPDF 进行 PDF 文件处理
- 基于 LangGraph 的工作流管理
- 支持多智能体协作
- 模块化设计，易于扩展
- 可配置的模型参数
- 交互式命令行界面
- 完整的单元测试覆盖

## 配置说明

在 `.env` 文件中可以配置以下参数：

- `QWEN_API_KEY`: Qwen API 密钥（兼容旧版）
- `DASHSCOPE_API_KEY`: DashScope API 密钥（新版必需）
- `QWEN_MODEL_NAME`: 使用的模型名称（默认：qwen3-235b-a22b）
- `QWEN_TEMPERATURE`: 生成温度（默认：0.5）
- `QWEN_MAX_TOKENS`: 最大生成 token 数（默认：16384，范围：[1, 16384]）

## PDF 处理说明

### 功能特点

1. PDF 解析
   - 提取完整文本内容
   - 获取文档元数据
   - 支持分页处理
   - 自动识别文档结构

2. 章节提取
   - 自动识别常见章节（摘要、引言、方法等）
   - 支持自定义章节关键词
   - 智能内容分段
   - 保持章节结构完整性

3. 内容分析
   - 生成结构化摘要
   - 提取关键研究点
   - 识别研究方法
   - 总结主要发现

### 使用限制

- PDF 文件必须可读且未加密
- 建议使用文本型 PDF（非扫描件）
- 大文件处理可能需要较长时间
- 章节识别效果取决于 PDF 格式质量

## 注意事项

- 确保有稳定的网络连接
- 需要有效的 Qwen API 密钥
- 建议在使用前先测试各个功能模块
- 根据实际需求调整模型参数
- 命令行界面支持多轮对话，可以连续执行多个任务
- 运行测试前请确保已正确配置 API 密钥
- PDF 处理功能需要安装 PyMuPDF 库
- 处理大型 PDF 文件时注意内存使用

## 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。

## 许可证

MIT License 