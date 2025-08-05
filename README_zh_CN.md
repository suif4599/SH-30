# AutoFOAM: 能源动力工程智能仿真代理

[English](README.md) | 简体中文

## 概述

AutoFOAM 是一个专为能源动力工程应用设计的智能代理工具组件。它作为大型语言模型(LLM)的工具，能够自动执行计算流体力学(CFD)仿真。给定仿真算例描述后，系统自动选择合适的工具，执行仿真，迭代纠错，并返回仿真结果。

目前，系统实现了 OpenFOAM 仿真的自动调用、错误纠正和迭代功能。

## 功能特性

- **智能自动化**: 自动解释仿真需求并配置 OpenFOAM 算例
- **错误纠正**: 内置错误检测和自动纠正机制
- **迭代优化**: 持续改进仿真设置直至成功执行
- **LLM 集成**: 设计为与大型语言模型无缝协作的工具组件
- **配置生成**: 基于算例描述自动生成 OpenFOAM 配置文件
- **全面日志**: 详细的执行日志和监控功能

## 项目结构

```
SH-30/
├── interface/                 # 核心接口模块
│   ├── __init__.py
│   ├── case.py               # OpenFOAM 算例管理
│   ├── file.py               # 文件操作和解析
│   └── foam_parser.py        # OpenFOAM 文件格式解析器
├── run/                      # 主要执行模块
│   ├── main.py              # 主执行脚本
│   ├── implement_chain.py    # 仿真链实现
│   ├── config_generator.py   # 配置文件生成器
│   ├── interface_display.py  # 接口演示
│   ├── chat_api_test.py     # API 测试工具
│   ├── config.py            # 配置设置
│   ├── config.json          # 配置文件
│   ├── cavity/              # 示例 OpenFOAM 算例
│   └── log/                 # 执行日志
└── README.md                # 项目说明文件
```

## 安装

### 环境要求

- Python 3.8+
- OpenFOAM v2406 或更高版本
- 所需的 Python 包（见下方依赖项）

### 依赖项

```bash
pip install -r requirements.txt
```

### 环境配置

1. 确保 OpenFOAM 正确安装并已加载环境
2. 设置 `FOAM_RUN` 环境变量
3. 在 `config.py` 中配置 API 密钥

## 使用方法

```diff
- 注意：本项目非常不成熟，所有API均有极大概率被修改或弃用，请勿直接用于工程实践
```

### 基本用法

```python
from implement_chain import run_and_log

# 运行带有自动重试和错误纠正的仿真
result = run_and_log(
    max_attempts=3,
    log_file="log/run.log"
)

print(f"状态: {result['status']}")
print(f"输出: {result['output']}")
```

### 算例描述格式

用自然语言提供详细的仿真参数：

```
[示例占位符 - 待填入具体算例描述]

示例算例描述格式：
- 流体性质（密度、粘度）
- 流动条件（速度、压力）
- 求解器类型和数值格式
- 边界条件
- 仿真时间和收敛准则
```

### 配置文件生成

```python
from config_generator import call_llm, write_content_to_file

# 生成特定配置文件
response = call_llm(
    boundary_file=boundary_info,
    case_description=case_desc,
    config_type="U",  # 或 "p", "transportProperties" 等
    last_version=previous_config,
    error_information=error_msg
)

write_content_to_file(response, "path/to/config/file")
```

## API 参考

### 核心函数

#### `run_and_log(max_attempts, delay, log_file)`
执行带有重试逻辑和全面日志记录的仿真。

**参数:**
- `max_attempts` (int): 最大重试次数
- `delay` (int): 重试间隔时间（秒）
- `log_file` (str): 日志文件路径

**返回:**
- `dict`: 包含状态、输出和错误信息的执行结果

#### `call_llm(boundary_file, case_description, config_type, last_version, error_information)`
使用 LLM 生成 OpenFOAM 配置文件。

**参数:**
- `boundary_file` (str): 网格字典信息，确保命名一致性
- `case_description` (str): 包含所有参数的完整算例描述
- `config_type` (str): 配置文件类型（p, U, transportProperties 等）
- `last_version` (str): 配置文件的上一版本
- `error_information` (str): 上次执行的错误信息

**返回:**
- `str`: 生成的配置文件内容

### 接口类

#### `Case`
管理 OpenFOAM 算例操作，包括文件访问、执行和错误处理。

#### `File`
处理 OpenFOAM 文件操作，具有快照和回滚功能。

## 示例

### 示例 1: 基础仿真
```python
[示例占位符 - 基础空腔流动仿真]
```

### 示例 2: 复杂流动配置
```python
[示例占位符 - 带有自定义边界条件的高级算例]
```

### 示例 3: 错误恢复
```python
[示例占位符 - 自动错误纠正演示]
```

## 配置

### API 配置
在 `config.py` 中更新您的 LLM API 设置：

```python
API_KEY = "your-api-key-here"
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL = "Qwen/Qwen3-235B-A22B-Instruct-2507"
```

### OpenFOAM 设置
确保正确的 OpenFOAM 环境配置：

```bash
source /path/to/OpenFOAM/etc/bashrc
export FOAM_RUN=/path/to/your/run/directory
```

## 日志和监控

系统提供全面的日志功能：

- **执行日志**: 详细的仿真进度和结果
- **错误跟踪**: 自动错误检测和日志记录
- **性能指标**: 时间和尝试次数统计
- **调试信息**: 详细的故障排除数据

日志文件存储在 `log/` 目录中，包含时间戳和执行详情。

## 故障排除

### 常见问题

1. **OpenFOAM 环境**: 确保 OpenFOAM 正确加载
2. **API 配置**: 验证 API 密钥和端点设置
3. **文件权限**: 检查算例目录的读写权限
4. **依赖问题**: 确保安装了所有必需的 Python 包

### 错误代码

- `UNMATCHED_FIELD`: 边界条件不匹配
- `CONVERGENCE_FAILURE`: 数值收敛问题
- `FILE_NOT_FOUND`: 缺少配置文件
- `SYNTAX_ERROR`: OpenFOAM 语法错误

## 贡献

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目基于 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- OpenFOAM 基金会提供的 CFD 工具包
- LangChain 提供的 LLM 集成功能
- 贡献者和开源社区

## 联系方式

- 项目链接: [https://github.com/suif4599/SH-30](https://github.com/suif4599/SH-30)
- 问题反馈: [https://github.com/suif4599/SH-30/issues](https://github.com/suif4599/SH-30/issues)

---

## 开发路线图

- [ ] 支持更多 CFD 求解器
- [ ] 高级错误诊断和纠正
- [ ] Web 界面
- [ ] 实时监控仪表板
- [ ] 集成更多 LLM 提供商
- [ ] 自动网格生成功能
