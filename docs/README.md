# AeroGuard Documentation

Welcome to the AeroGuard documentation hub. All documentation is organized by category and feature for easy navigation.

## 📚 Documentation Structure

```
docs/
├── 01_getting_started/          ← Start here!
│   ├── GETTING_STARTED.md       - Quick introduction
│   ├── DEVELOPMENT.md           - Development setup
│   └── SETUP_SUMMARY.md         - Setup instructions
│
├── 02_models/                   ← Machine learning models
│   ├── sarima/
│   │   └── (SARIMA model documentation)
│   │
│   └── xgboost/
│       ├── XGBOOST_MODEL.md     - XGBoost implementation
│       └── XGBOOST_INTEGRATION_COMPLETE.md
│
├── 03_preprocessing/            ← Data preprocessing
│   ├── TIMESERIES_PREPROCESSING.md    - Data preprocessing guide
│   ├── TIMESERIES_QUICK_REFERENCE.md  - Quick reference
│   └── TIMESERIES_IMPLEMENTATION_SUMMARY.md
│
├── 04_services/                 ← Business logic services
│   ├── model_comparison/        - Model comparison service
│   │   ├── JUDGE_FAVORITE_SUMMARY.md
│   │   ├── MODEL_SELECTOR.md
│   │   └── MODEL_SELECTOR_QUICK_REFERENCE.md
│   │
│   └── health_risk/             - Health risk classification
│       ├── HEALTH_RISK_ENGINE.md
│       └── HEALTH_RISK_QUICK_REF.md
│
├── 05_apis/                     ← REST API documentation
│   └── MODEL_COMPARISON_API.md  - Model comparison API reference
│
└── 06_project/                  ← Project information
    ├── PROJECT_STRUCTURE.md     - Project organization
    └── PROJECT_SUMMARY.py       - Project summary

```

## 🚀 Quick Navigation

### For New Users
1. Start with [01_getting_started/GETTING_STARTED.md](01_getting_started/GETTING_STARTED.md)
2. Review [01_getting_started/DEVELOPMENT.md](01_getting_started/DEVELOPMENT.md) for setup
3. Check [06_project/PROJECT_STRUCTURE.md](06_project/PROJECT_STRUCTURE.md) for overview

### For Model Development
1. [02_models/xgboost/XGBOOST_MODEL.md](02_models/xgboost/XGBOOST_MODEL.md) - XGBoost models
2. [03_preprocessing/TIMESERIES_PREPROCESSING.md](03_preprocessing/TIMESERIES_PREPROCESSING.md) - Data prep
3. [03_preprocessing/TIMESERIES_QUICK_REFERENCE.md](03_preprocessing/TIMESERIES_QUICK_REFERENCE.md) - Quick ref

### For Service Integration
1. [04_services/model_comparison/JUDGE_FAVORITE_SUMMARY.md](04_services/model_comparison/JUDGE_FAVORITE_SUMMARY.md) - Model comparison
2. [04_services/health_risk/HEALTH_RISK_ENGINE.md](04_services/health_risk/HEALTH_RISK_ENGINE.md) - Health risk assessment
3. [05_apis/MODEL_COMPARISON_API.md](05_apis/MODEL_COMPARISON_API.md) - REST API endpoints

### For Specific Features
- **Time Series Preprocessing**: [03_preprocessing/](03_preprocessing/)
- **Model Comparison**: [04_services/model_comparison/](04_services/model_comparison/)
- **Health Risk Classification**: [04_services/health_risk/](04_services/health_risk/)
- **REST APIs**: [05_apis/](05_apis/)

## 📖 Category Descriptions

### 01 - Getting Started
Entry point documentation covering:
- Project introduction
- Installation and setup
- Development environment configuration
- Initial setup steps

### 02 - Models
Machine learning model implementations:
- **SARIMA**: Time series forecasting model
- **XGBoost**: Gradient boosting model
- Model specifications and usage

### 03 - Preprocessing
Data preparation and transformation:
- Time series preprocessing pipeline
- Feature engineering
- Data validation

### 04 - Services
Business logic services:
- **Model Comparison**: Compare and select best model
- **Health Risk**: Classify health risks from AQI values
- Service architecture and usage

### 05 - APIs
REST API endpoint documentation:
- Model comparison endpoints
- Request/response formats
- Error handling
- Integration examples

### 06 - Project
High-level project information:
- Project structure
- Component overview
- File organization
- Project summary

## 🔍 Finding What You Need

| Looking for... | Go to... |
|---|---|
| How to set up the project | [01_getting_started/SETUP_SUMMARY.md](01_getting_started/SETUP_SUMMARY.md) |
| XGBoost model details | [02_models/xgboost/](02_models/xgboost/) |
| Data preprocessing guide | [03_preprocessing/TIMESERIES_PREPROCESSING.md](03_preprocessing/TIMESERIES_PREPROCESSING.md) |
| Model comparison service | [04_services/model_comparison/](04_services/model_comparison/) |
| Health risk assessment | [04_services/health_risk/](04_services/health_risk/) |
| API endpoints | [05_apis/MODEL_COMPARISON_API.md](05_apis/MODEL_COMPARISON_API.md) |
| Project overview | [06_project/PROJECT_STRUCTURE.md](06_project/PROJECT_STRUCTURE.md) |

## 📝 Document Types

### Full References
Complete documentation covering:
- Architecture
- Usage patterns
- Code examples
- Error handling
- Best practices

**Examples**: 
- [HEALTH_RISK_ENGINE.md](04_services/health_risk/HEALTH_RISK_ENGINE.md)
- [XGBOOST_MODEL.md](02_models/xgboost/XGBOOST_MODEL.md)

### Quick References
Condensed guides for quick lookup:
- Common use cases
- Code snippets
- Performance info
- Best practices

**Examples**:
- [HEALTH_RISK_QUICK_REF.md](04_services/health_risk/HEALTH_RISK_QUICK_REF.md)
- [TIMESERIES_QUICK_REFERENCE.md](03_preprocessing/TIMESERIES_QUICK_REFERENCE.md)

### Summaries
Overview documents highlighting:
- Key features
- Implementation status
- Metrics and statistics
- Integration info

**Examples**:
- [JUDGE_FAVORITE_SUMMARY.md](04_services/model_comparison/JUDGE_FAVORITE_SUMMARY.md)
- [XGBOOST_INTEGRATION_COMPLETE.md](02_models/xgboost/XGBOOST_INTEGRATION_COMPLETE.md)

## 🎯 By Use Case

### I'm a Developer
1. Read [01_getting_started/DEVELOPMENT.md](01_getting_started/DEVELOPMENT.md)
2. Review [06_project/PROJECT_STRUCTURE.md](06_project/PROJECT_STRUCTURE.md)
3. Explore relevant service docs in [04_services/](04_services/)

### I'm Integrating the System
1. Check [04_services/model_comparison/JUDGE_FAVORITE_SUMMARY.md](04_services/model_comparison/JUDGE_FAVORITE_SUMMARY.md)
2. Review [05_apis/MODEL_COMPARISON_API.md](05_apis/MODEL_COMPARISON_API.md)
3. See [04_services/health_risk/HEALTH_RISK_ENGINE.md](04_services/health_risk/HEALTH_RISK_ENGINE.md)

### I'm Using the Models
1. Check [03_preprocessing/TIMESERIES_QUICK_REFERENCE.md](03_preprocessing/TIMESERIES_QUICK_REFERENCE.md)
2. Review relevant model docs in [02_models/](02_models/)
3. See [04_services/model_comparison/](04_services/model_comparison/) for selection logic

### I Need a Quick Answer
1. Check the Quick Reference sections in each folder
2. Look at code examples in the docs
3. Review relevant API documentation

## 📞 Still Need Help?

- Check the README in each folder for category-specific guidance
- Look for code examples in the documentation
- Review the quick reference guides for common patterns
- Check project structure for file locations

---

**Last Updated**: January 31, 2026  
**Documentation Version**: Complete  
**Status**: Organized and Ready for Use ✅
