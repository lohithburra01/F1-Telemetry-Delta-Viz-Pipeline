# Complete Setup Guide

This guide will walk you through setting up the F1 Telemetry Delta Calculator repository from scratch, including integration with your existing 3D visualization pipeline.

## Quick Setup Commands

```bash
# 1. Create and setup the repository
mkdir f1-telemetry-delta-calculator
cd f1-telemetry-delta-calculator
git init

# 2. Create the directory structure
mkdir -p f1_telemetry examples tests docs integration data scripts .github/workflows
mkdir -p data/sample_exports data/test_data data/reference_deltas
mkdir -p .github/ISSUE_TEMPLATE

# 3. Create __init__.py files for Python packages
touch f1_telemetry/__init__.py
touch examples/__init__.py
touch tests/__init__.py
touch integration/__init__.py

# 4. Initialize git repository
git add .
git commit -m "Initial repository structure"

# 5. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 6. Install dependencies
pip install -r requirements.txt
pip install -e .  # Install package in development mode
```

## Step-by-Step Setup

### 1. Repository Initialization

First, create your GitHub repository:

1. Go to GitHub and create a new repository named `f1-telemetry-delta-calculator`
2. Clone it locally:
```bash
git clone https://github.com/yourusername/f1-telemetry-delta-calculator.git
cd f1-telemetry-delta-calculator
```

### 2. File Creation

Create all the files I've provided above in the correct directory structure:

```
f1-telemetry-delta-calculator/
├── README.md
├── LICENSE
├── setup.py
├── requirements.txt
├── .gitignore
├── PROJECT_STRUCTURE.md
├── SETUP_GUIDE.md
├── f1_telemetry/
│   ├── __init__.py
│   ├── delta_calculator.py  # Your original code
│   ├── visualization.py
│   └── utils.py
└── examples/
    ├── basic_usage.py
    └── advanced_usage.py
```

### 3. Update Your Original Code

Replace your original paste.txt content with the modularized version in `f1_telemetry/delta_calculator.py`. The main changes:

- Import statements updated for the package structure
- Added integration with visualization module
- Added data export capabilities
- Enhanced error handling

### 4. Package Installation

```bash
# Install in development mode
pip install -e .

# Verify installation
python -c "from f1_telemetry import F1TelemetryDeltaCalculator; print('Installation successful!')"
```

### 5. Test the Installation

Create a simple test script:

```python
# test_installation.py
from f1_telemetry import F1TelemetryDeltaCalculator

try:
    # Test basic import and initialization
    calculator = F1TelemetryDeltaCalculator(2024, 'Q', 'BAHRAIN')
    print("✅ Installation successful!")
    print(f"Available drivers: {calculator.get_available_drivers()}")
except Exception as e:
    print(f"❌ Installation failed: {e}")
```

## Integration with 3D Visualization Pipeline

### Linking to Your Existing Repository

1. **Add submodule reference** (in your main 3D viz repo):
```bash
cd /path/to/F1-3D-VISUALIZATION
git submodule add https://github.com/yourusername/f1-telemetry-delta-calculator.git telemetry-calculator
```

2. **Cross-reference in README** (add to both repositories):

In your F1-3D-VISUALIZATION README.md:
```markdown
## Data Processing Pipeline

This project uses the [F1 Telemetry Delta Calculator](https://github.com/yourusername/f1-telemetry-delta-calculator) for high-precision telemetry processing.

### Setup
1. Clone this repository
2. Install the telemetry calculator: `pip install git+https://github.com/yourusername/f1-telemetry-delta-calculator.git`
3. Process data: `python scripts/process_telemetry.py`
4. Run 3D visualization
```

In your telemetry calculator README.md:
```markdown
## 3D Visualization Integration

This calculator integrates with the [F1 3D Visualization Pipeline](https://github.com/lohithburra01/F1-3D-VISUALIZATION) for automated race animation.

### Workflow
```python
# 1. Calculate delta
calculator = F1TelemetryDeltaCalculator(2024, 'Q', 'MONACO')
delta, distances, summary_df, t1, t2 = calculator.calculate_delta('VER', 'LEC')

# 2. Export for 3D pipeline
filename = calculator.export_data(delta, distances, summary_df, 'VER', 'LEC', t1, t2)

# 3. Use in 3D application
# Load the JSON file in your 3D visualization system
```

### Data Flow Integration

Create a bridge script in your 3D visualization repo:

```python
# scripts/process_telemetry.py (in your 3D viz repo)
import sys
sys.path.append('../telemetry-calculator')  # If using submodule

from f1_telemetry import F1TelemetryDeltaCalculator
import json

def process_race_data(year, session_type, session_name, driver1, driver2):
    """Process F1 telemetry data for 3D visualization"""
    
    # Initialize calculator
    calc = F1TelemetryDeltaCalculator(year, session_type, session_name)
    
    # Calculate delta
    delta, distances, summary_df, t1, t2 = calc.calculate_delta(driver1, driver2)
    
    # Export optimized for 3D pipeline
    filename = f"data/processed/{driver1}_vs_{driver2}_{session_name}.json"
    calc.export_data(delta, distances, summary_df, driver1, driver2, t1, t2, filename)
    
    # Load and return for immediate use
    with open(filename) as f:
        return json.load(f)

# Usage
if __name__ == "__main__":
    data = process_race_data(2024, 'Q', 'MONACO', 'VER', 'LEC')
    print(f"Processed data ready for 3D visualization: {len(data['telemetry']['distances'])} points")
```

## Advanced Configuration

### Environment Variables

Create a `.env` file for configuration:
```bash
# .env
F1_CACHE_DIR=./fastf1_cache
F1_DATA_QUALITY=high
PLOT_DPI=300
EXPORT_FORMAT=json
```

### Custom Configuration Class

Add to `f1_telemetry/config.py`:
```python
import os
from typing import Dict, Any

class F1Config:
    """Configuration management for F1 telemetry calculator"""
    
    def __init__(self):
        self.cache_dir = os.getenv('F1_CACHE_DIR', './fastf1_cache')
        self.data_quality = os.getenv('F1_DATA_QUALITY', 'high')
        self.plot_dpi = int(os.getenv('PLOT_DPI', '300'))
        self.export_format = os.getenv('EXPORT_FORMAT', 'json')
    
    def get_calculation_params(self) -> Dict[str, Any]:
        """Get default calculation parameters based on quality setting"""
        if self.data_quality == 'high':
            return {'num_windows': 8, 'grid_step': 2.5}
        elif self.data_quality == 'medium':
            return {'num_windows': 6, 'grid_step': 5.0}
        else:
            return {'num_windows': 4, 'grid_step': 10.0}
```

## GitHub Repository Setup

### 1. Create GitHub Actions

`.github/workflows/tests.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Test with pytest
      run: |
        pytest tests/ --cov=f1_telemetry --cov-report=xml
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

### 2. Issue Templates

`.github/ISSUE_TEMPLATE/bug_report.md`:
```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Initialize calculator with '...'
2. Calculate delta for '...' vs '...'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. Windows 10, macOS, Ubuntu]
- Python version: [e.g. 3.9.7]
- Package version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
```

### 3. Pull Request Template

`.github/pull_request_template.md`:
```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated documentation

## Integration
- [ ] Compatible with 3D visualization pipeline
- [ ] Maintains backward compatibility
- [ ] Performance implications considered
```

## Deployment and Publishing

### PyPI Publication

1. **Setup PyPI account** and get API token

2. **Build and publish**:
```bash
pip install build twine
python -m build
twine upload dist/*
```

3. **Update setup.py** with your information:
```python
# In setup.py, update these fields:
author="Your Name",
author_email="your.email@example.com",
url="https://github.com/yourusername/f1-telemetry-delta-calculator",
```

### Documentation Deployment

Setup GitHub Pages for documentation:

1. Create `docs/` directory with markdown files
2. Enable GitHub Pages in repository settings
3. Use GitHub Actions to build and deploy docs

## Final Checklist

- [ ] Repository created and initialized
- [ ] All files created in correct structure
- [ ] Dependencies installed and working
- [ ] Basic test script runs successfully
- [ ] Integration with 3D pipeline tested
- [ ] Documentation complete and accurate
- [ ] GitHub Actions configured
- [ ] Issue and PR templates created
- [ ] README includes link to 3D visualization repo
- [ ] License and contribution guidelines added

## Next Steps

1. **Test with real data**: Run the examples with actual F1 session data
2. **Create sample datasets**: Add reference calculations to `data/reference_deltas/`
3. **Performance optimization**: Profile the code and optimize bottlenecks
4. **Extended integration**: Create plugins for Blender, Unity, etc.
5. **Community engagement**: Share with F1 analysis community

## Troubleshooting

**Common Issues:**

1. **FastF1 cache issues**: Clear cache with `rm -rf ./fastf1_cache`
2. **Network timeouts**: F1 data loading requires stable internet
3. **Memory issues**: Large datasets may need chunked processing
4. **Plot display**: On headless servers, save plots instead of displaying

**Getting Help:**

1. Check the troubleshooting guide in `docs/troubleshooting.md`
2. Review example scripts in `examples/`
3. Open an issue on GitHub with detailed error information
4. Reference the [FastF1 documentation](https://docs.fastf1.dev/) for data-related issues

Your repository is now ready for professional F1 telemetry analysis and seamless integration with your 3D visualization pipeline!