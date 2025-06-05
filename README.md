# 学术智能体 (AcAgent)

这是一个基于 LangGraph 和 Qwen API 构建的学术智能体，能够帮助研究人员进行文献检索、论文分析、写作润色等学术工作。

## 功能特点

- 文献检索与摘要
- 引用验证与格式化
- 学术写作润色
- 数据分析支持
- 参考文献生成
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
- `help` - 显示帮助信息
- `exit` - 退出程序

3. 使用示例：
```
> search 人工智能教育应用
> summarize 1
> polish 这是一段需要润色的学术文本
> analyze descriptive
> cite 1 apa
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
    "task_type": "writing",  # 可选: "writing", "analysis", "references"
    "literature_results": None,
    "summary": None,
    "citations": None,
    "analysis_results": None
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

1. `test_search_papers`: 测试文献搜索功能（使用 scholarly 和 Qwen API 生成友好摘要）
   - 验证搜索结果格式
   - 检查必要字段（标题、摘要等）
   - 测试错误处理

2. `test_summarize_paper`: 测试文献摘要功能
   - 验证摘要生成
   - 测试字段缺失处理
   - 检查 API 响应处理

3. `test_polish_text`: 测试文本润色功能
   - 验证文本润色
   - 测试 API 错误处理
   - 检查响应格式

4. `test_generate_reference`: 测试引用生成功能
   - 验证 APA 和 MLA 格式
   - 测试字段缺失处理
   - 检查格式化输出

5. `test_workflow`: 测试工作流功能
   - 验证工作流执行
   - 测试状态转换
   - 检查结果格式

## 工作流程

1. 文献检索 (search_literature)
2. 摘要与解释 (summarize_and_explain)
3. 引用验证 (check_citation_validity)
4. 根据任务类型执行：
   - 写作润色 (polish_writing)
   - 数据分析 (analyze_data)
   - 生成参考文献 (generate_references)

## 技术特点

- 使用 Qwen API 进行自然语言处理（包括摘要精炼）
- 集成 scholarly 库进行专业的谷歌学术文献检索
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

## 注意事项

- 确保有稳定的网络连接
- 需要有效的 Qwen API 密钥
- 建议在使用前先测试各个功能模块
- 根据实际需求调整模型参数
- 命令行界面支持多轮对话，可以连续执行多个任务
- 运行测试前请确保已正确配置 API 密钥

## 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。

## 许可证

MIT License 