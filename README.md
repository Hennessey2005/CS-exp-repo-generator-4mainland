# 实验报告自动生成系统

## 系统介绍

本系统是一个基于大语言模型的实验报告自动生成工具，能够根据源代码和实验要求文档，利用LLM技术自动生成符合规范的Word格式实验报告。系统支持多种编程语言的代码分析，多种格式的实验要求文档输入，并提供了命令行和图形界面两种操作方式。

### 核心功能

- **多格式支持**：支持PDF、Word和文本格式的实验要求文档输入
- **代码分析**：自动解析多种编程语言的源代码文件或目录
- **模块化生成**：支持按模块生成报告内容，包括标题、引言、背景、实现、结果、分析和结论
- **LLM集成**：支持接入OpenAI、Anthropic和DeepSeek等主流大模型API（默认使用DeepSeek）
- **Word导出**：自动生成格式规范的Word文档，支持代码高亮显示
- **多界面支持**：提供命令行交互界面和图形用户界面
- **进度管理**：支持进度保存和加载，方便中断后继续工作

## 系统架构

```
report_generator/
├── modules/             # 核心功能模块
│   ├── file_reader.py         # 文件读取模块
│   ├── code_parser.py         # 代码解析模块
│   ├── llm_api.py             # LLM API接入模块（支持OpenAI/Anthropic/DeepSeek）
│   ├── report_generator.py    # 报告生成模块
│   ├── word_exporter.py       # Word导出模块
│   └── formula_converter.py   # 公式转换模块
├── utils/               # 工具函数
├── configs/             # 配置文件
│   ├── config.json            # 主配置文件
│   └── default_config.json    # 默认配置文件
├── output/              # 输出目录
├── main.py              # 主程序入口
├── gui.py               # 图形界面实现
├── requirements.txt     # 依赖包列表
├── .env                 # 环境变量文件
├── .env.example         # 环境变量示例
└── README.md            # 说明文档
```

## 安装配置

### 1. 环境要求

- Python 3.8 及以上版本
- 安装依赖包
- 配置大模型API密钥（OpenAI或Anthropic）

### 2. 安装步骤

#### 2.1 克隆仓库

```bash
# 克隆仓库
cd C:\Users\zhw\Documents\Project
```

#### 2.2 安装依赖

```bash
# 创建并激活虚拟环境（可选但推荐）
python -m venv venv
# Windows 激活
venv\Scripts\activate
# macOS/Linux 激活
# source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

#### 2.3 配置API密钥

1. 复制环境变量示例文件：

```bash
# Windows
copy report_generator\.env.example report_generator\.env
# macOS/Linux
# cp report_generator/.env.example report_generator/.env
```

2. 编辑 `.env` 文件，填入您的API密钥：

```
# DeepSeek API 配置（默认使用，推荐）
DEEPSEEK_API_KEY=your_actual_deepseek_api_key

# OpenAI API 配置（可选）
# OPENAI_API_KEY=your_actual_openai_api_key

# Anthropic API 配置（可选）
# ANTHROPIC_API_KEY=your_actual_anthropic_api_key
```

3. 配置模型参数（可选）：

编辑 `report_generator/configs/config.json` 文件，可修改以下参数：
- `llm_provider`：LLM提供商，可选值为 "openai", "anthropic" 或 "deepseek"（默认）
- `openai_model`：OpenAI模型名称
- `anthropic_model`：Anthropic模型名称
- `deepseek_model`：DeepSeek模型名称
- `temperature`：生成温度，控制输出的随机性
- `max_tokens`：最大生成令牌数

## 使用方法

### 1. 交互式模式（命令行）

```bash
cd report_generator
python -m main --interactive
```

进入交互式界面后，可以按照提示完成以下操作：

- 加载实验要求文件（PDF、Word或文本格式）
- 分析源代码（单个文件或整个目录）
- 选择性生成报告模块
- 导出完整的Word格式报告
- 保存和加载工作进度

### 2. 图形界面模式（推荐）

```bash
cd report_generator
python gui.py
```

图形界面提供了直观的操作方式，支持：

- 多选代码文件
- 多选实验要求文件
- 友好的进度显示
- 操作日志实时展示
- 一键生成报告

### 3. 命令行自动模式

```bash
python -m report_generator.main --auto \
    --requirements "path/to/requirements.pdf" \
    --code "path/to/source/code" \
    --output "output/report.docx"
```

或者对于GUI兼容的参数：

```bash
python -m report_generator.main --auto \
    --code_file "path/to/file1.py" \
    --code_file "path/to/file2.py" \
    --requirement_files "path/to/requirements.pdf" \
    --output_file "output/report.docx"

### 4. 直接运行GUI脚本

Windows用户可以直接双击运行：

```
start_gui.bat
```

## 功能说明

### 文件读取功能

支持读取以下格式的实验要求文档：
- PDF文件（使用PyPDF2库）
- Word文档（.docx格式，使用python-docx库）

### 代码分析功能

支持解析以下编程语言的代码：
- Python (.py)
- Java (.java)
- C (.c)
- C++ (.cpp, .cc)
- JavaScript (.js)
- TypeScript (.ts)

分析内容包括：
- 代码结构和组织
- 函数和类的定义
- 核心算法和实现
- 注释提取

### 报告生成功能

系统会自动生成以下模块的内容：

1. **标题和基本信息**：根据实验要求和代码内容生成
2. **引言/实验目的**：根据实验要求文档生成
3. **实验背景和原理**：结合要求文档和代码分析生成
4. **实验实现（代码分析）**：详细分析源代码的结构和功能
5. **实验结果**：基于代码分析生成模拟的实验结果
6. **结果分析**：对生成的实验结果进行深入分析
7. **结论**：总结实验成果和收获

### Word导出功能

生成的Word文档包含：
- 格式化的标题页
- 自动生成的目录
- 结构化的章节内容
- 高亮显示的代码块
- 自动编号的章节和段落

## 配置说明

### 主要配置文件

1. **`report_generator/configs/config.json`**：
   - `llm_provider`：LLM提供商，可选值为 "openai", "anthropic" 或 "deepseek"
   - `openai_model`：OpenAI模型名称
   - `anthropic_model`：Anthropic模型名称
   - `deepseek_model`：DeepSeek模型名称
   - `temperature`：生成温度，建议值0.2-0.7
   - `max_tokens`：最大生成令牌数

2. **`report_generator/.env`**：
   - 存储API密钥等敏感信息
   - 支持配置多个提供商的API密钥

### 环境变量优先级

系统会按以下优先级加载配置：
1. 环境变量（`.env`文件）
2. 配置文件（`configs/config.json`）
3. 程序默认值（DeepSeek作为默认提供商）

## 常见问题

### 1. API连接失败

解决方案：
- 检查API密钥是否正确（尤其是DeepSeek API密钥）
- 确认网络连接正常
- 如需代理，请在`.env`文件中配置代理服务器
- 检查API使用额度是否足够
- 尝试切换到其他LLM提供商

### 2. 文档读取错误

解决方案：
- 确认文件格式正确（PDF或.docx）
- 检查文件是否损坏
- 对于受保护的PDF，可能需要预先解密

### 3. 代码分析不准确

解决方案：
- 确保代码有足够的注释
- 对于非标准格式的代码，可能需要手动调整
- 复杂的代码结构可能需要更多的上下文理解

## 开发说明

### 添加新功能

1. **添加新的LLM提供商**：
   - 在 `modules/llm_api.py` 中继承 `LLMClient` 基类
   - 实现 `generate` 方法
   - 在 `APIClientFactory` 中添加新的工厂方法

2. **支持新的编程语言**：
   - 在 `modules/code_parser.py` 中扩展 `CodeParser` 类
   - 添加新语言的解析方法
   - 更新文件扩展名映射

3. **添加新的报告模块**：
   - 在 `modules/report_generator.py` 中更新 `REPORT_MODULES` 列表
   - 添加相应的生成方法

### 测试

运行测试套件：

```bash
python -m pytest tests/
```

## 许可证

[MIT License](https://opensource.org/licenses/MIT)

## 免责声明

- 本工具生成的报告仅供参考，用户应根据实际情况进行修改和完善
- 使用本工具需遵守各LLM提供商的服务条款
- 对于代码分析结果，用户应进行验证

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目仓库: [https://github.com/ZhangHuaiwen51/CS-exp-repo-generator-4mainland](https://github.com/ZhangHuaiwen51/CS-exp-repo-generator-4mainland)

- 问题反馈: 请在GitHub上提交Issues