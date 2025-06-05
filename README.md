# 学术智能体 (Academic Agent)

这是一个基于LangGraph构建的学术智能体，能够帮助研究人员进行文献检索、论文分析、写作润色等学术工作。

## 功能特点

- 文献检索与摘要
- 引用验证与格式化
- 学术写作润色
- 数据分析支持
- 参考文献生成

## 安装要求

1. Python 3.8+
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 `.env` 文件并添加以下内容：
```
OPENAI_API_KEY=your_api_key_here
```

## 使用方法

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
    "task_type": "writing",  # 可选: "writing", "analysis", "references"
    "literature_results": None,
    "summary": None,
    "citations": None,
    "analysis_results": None
}

# 运行工作流
result = workflow.invoke(initial_state)
```

## 工作流程

1. 文献检索 (search_literature)
2. 摘要与解释 (summarize_and_explain)
3. 引用验证 (check_citation_validity)
4. 根据任务类型执行：
   - 写作润色 (polish_writing)
   - 数据分析 (analyze_data)
   - 生成参考文献 (generate_references)

## 注意事项

- 确保有稳定的网络连接
- 需要有效的OpenAI API密钥
- 建议在使用前先测试各个功能模块

## 贡献

欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证

MIT License 