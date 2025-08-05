# AutoFOAM: Intelligent Simulation Agent for Energy and Power Engineering

[简体中文](README_zh_CN.md) | English

## Overview

AutoFOAM is an intelligent agent tool component designed for energy and power engineering applications. It serves as a tool for large language models (LLMs) to automatically perform computational fluid dynamics (CFD) simulations. Given a simulation case description, the system automatically selects appropriate tools, performs simulations, iteratively corrects errors, and returns simulation results.

Currently, the system implements automatic invocation, error correction, and iteration capabilities for OpenFOAM simulations.

## Features

- **Intelligent Automation**: Automatically interprets simulation requirements and configures OpenFOAM cases
- **Error Correction**: Built-in error detection and automatic correction mechanisms
- **Iterative Refinement**: Continuously improves simulation setup until successful execution
- **LLM Integration**: Designed to work seamlessly with large language models as a tool component
- **Configuration Generation**: Automatically generates OpenFOAM configuration files based on case descriptions
- **Comprehensive Logging**: Detailed execution logs and monitoring capabilities

## Project Structure

```
SH-30/
├── interface/                 # Core interface modules
│   ├── __init__.py
│   ├── case.py               # OpenFOAM case management
│   ├── file.py               # File operations and parsing
│   └── foam_parser.py        # OpenFOAM file format parser
├── run/                      # Main execution modules
│   ├── main.py              # Main execution script
│   ├── implement_chain.py    # Simulation chain implementation
│   ├── config_generator.py   # Configuration file generator
│   ├── interface_display.py  # Interface demonstration
│   ├── chat_api_test.py     # API testing utilities
│   ├── config.py            # Configuration settings
│   ├── config.json          # Configuration file
│   ├── cavity/              # Example OpenFOAM case
│   └── log/                 # Execution logs
└── README.md                # This file
```

## Installation

### Prerequisites

- Python 3.8+
- OpenFOAM v2406 or later
- Required Python packages (see requirements below)

### Dependencies

```bash
pip install -r requirements.txt
```

### Environment Setup

1. Ensure OpenFOAM is properly installed and sourced
2. Set up the `FOAM_RUN` environment variable
3. Configure API keys in `config.py`

## Usage

```diff
- This project is highly experimental. All APIs are subject to breaking changes or deprecation. DO NOT USE IN PRODUCTION ENVIRONMENTS DIRECTLY.
```

### Basic Usage

```python
from implement_chain import run_and_log

# Run simulation with automatic retry and error correction
result = run_and_log(
    max_attempts=3,
    log_file="log/run.log"
)

print(f"Status: {result['status']}")
print(f"Output: {result['output']}")
```

### Case Description Format

Provide detailed simulation parameters in natural language:

```
[EXAMPLE PLACEHOLDER - To be filled with specific case descriptions]

Example case description format:
- Fluid properties (density, viscosity)
- Flow conditions (velocity, pressure)
- Solver type and numerical schemes
- Boundary conditions
- Simulation time and convergence criteria
```

### Configuration File Generation

```python
from config_generator import call_llm, write_content_to_file

# Generate specific configuration files
response = call_llm(
    boundary_file=boundary_info,
    case_description=case_desc,
    config_type="U",  # or "p", "transportProperties", etc.
    last_version=previous_config,
    error_information=error_msg
)

write_content_to_file(response, "path/to/config/file")
```

## API Reference

### Core Functions

#### `run_and_log(max_attempts, delay, log_file)`
Execute simulation with retry logic and comprehensive logging.

**Parameters:**
- `max_attempts` (int): Maximum number of retry attempts
- `delay` (int): Delay between attempts in seconds
- `log_file` (str): Path to log file

**Returns:**
- `dict`: Execution results with status, output, and error information

#### `call_llm(boundary_file, case_description, config_type, last_version, error_information)`
Generate OpenFOAM configuration files using LLM.

**Parameters:**
- `boundary_file` (str): Mesh dictionary information for naming consistency
- `case_description` (str): Complete case description with all parameters
- `config_type` (str): Configuration file type (p, U, transportProperties, etc.)
- `last_version` (str): Previous version of the configuration file
- `error_information` (str): Error messages from previous execution

**Returns:**
- `str`: Generated configuration file content

### Interface Classes

#### `Case`
Manages OpenFOAM case operations including file access, execution, and error handling.

#### `File`
Handles OpenFOAM file operations with snapshot and rollback capabilities.

## Examples

Unfinished

## Configuration

### API Configuration
Update `config.py` with your LLM API settings:

```python
API_KEY = "your-api-key-here"
```

### OpenFOAM Settings
Ensure proper OpenFOAM environment setup:

```bash
source /path/to/OpenFOAM/etc/bashrc
export FOAM_RUN=/path/to/your/run/directory
```

## Logging and Monitoring

The system provides comprehensive logging capabilities:

- **Execution logs**: Detailed simulation progress and results
- **Error tracking**: Automatic error detection and logging
- **Performance metrics**: Timing and attempt statistics
- **Debug information**: Detailed troubleshooting data

Log files are stored in the `log/` directory with timestamps and execution details.

## Troubleshooting

### Common Issues

1. **OpenFOAM Environment**: Ensure OpenFOAM is properly sourced
2. **API Configuration**: Verify API keys and endpoint settings
3. **File Permissions**: Check read/write permissions for case directories
4. **Dependency Issues**: Ensure all required Python packages are installed

### Error Codes

- `UNMATCHED_FIELD`: Boundary condition mismatch
- `CONVERGENCE_FAILURE`: Numerical convergence issues
- `FILE_NOT_FOUND`: Missing configuration files
- `SYNTAX_ERROR`: OpenFOAM syntax errors

## License

This project is licensed under the GPL-v3 License - see the [LICENSE](LICENSE.txt) file for details.
