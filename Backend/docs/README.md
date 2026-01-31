# AeroGuard Backend Documentation

Welcome to the AeroGuard Backend documentation hub. All documentation is organized by category and feature for easy navigation.

## 📚 Documentation Structure

```
docs/
├── 01_getting_started/                    ← START HERE
│   ├── README.md                          - Overview
│   ├── GETTING_STARTED.md                 - Quick introduction
│   ├── DEVELOPMENT.md                     - Development setup
│   ├── SETUP_SUMMARY.md                   - Setup instructions
│   └── DELIVERY_SUMMARY.md                - Delivery overview
│
├── 02_models/                             ← Machine Learning Models
│   └── xgboost/
│       ├── XGBOOST_MODEL.md               - XGBoost implementation & usage
│       └── XGBOOST_INTEGRATION_COMPLETE.md - Integration complete report
│
├── 03_data/                               ← Data Processing
│   ├── SPATIAL_INTERPOLATION.md           - Spatial interpolation guide
│   └── SPATIAL_INTERPOLATION_QUICK_REF.md - Quick reference
│
├── 03_preprocessing/                      ← Time Series Data Preprocessing
│   ├── TIMESERIES_PREPROCESSING.md            - Comprehensive guide
│   ├── TIMESERIES_QUICK_REFERENCE.md         - Quick reference
│   └── TIMESERIES_IMPLEMENTATION_SUMMARY.md  - Implementation summary
│
├── 04_services/                           ← Business Logic Services
│   ├── explainability/                    - Model explainability
│   │   ├── EXPLAINABILITY_ENGINE.md               - Core engine documentation
│   │   ├── EXPLAINABILITY_QUICK_REF.md            - Quick reference
│   │   ├── EXPLAINABILITY_IMPLEMENTATION_COMPLETE.md
│   │   ├── GENERATIVE_EXPLAINER.md               - LLM-based explainer
│   │   └── GENERATIVE_QUICK_REF.md               - Quick reference
│   │
│   ├── health_risk/                       - Health risk classification
│   │   ├── HEALTH_RISK_ENGINE.md          - Classification engine
│   │   ├── HEALTH_RISK_QUICK_REF.md       - Quick reference
│   │   ├── HEALTH_RISK_COMPLETE.md        - Completion report
│   │   ├── HEALTH_RISK_DELIVERY.md        - Delivery documentation
│   │   └── HEALTH_RISK_SUMMARY.md         - Summary
│   │
│   └── model_comparison/                  - Model comparison & selection
│       ├── MODEL_SELECTOR.md              - Model selector logic
│       ├── MODEL_SELECTOR_QUICK_REFERENCE.md
│       ├── JUDGE_FAVORITE_SUMMARY.md      - Judge favorite summary
│       ├── JUDGE_FAVORITE_INDEX.md        - Judge favorite index
│       ├── JUDGE_FAVORITE_CHECKLIST.md    - Checklist
│       ├── JUDGE_FAVORITE_COMPLETE.md     - Completion report
│       └── JUDGE_FAVORITE_QUICK_START.md  - Quick start guide
│
├── 05_apis/                               ← REST API Documentation
│   ├── API_ENDPOINTS_COMPLETE.md          - Complete API endpoints reference
│   └── MODEL_COMPARISON_API.md            - Model comparison API guide
│
├── 05_main_app/                           ← Main Flask Application
│   ├── MAIN_FLASK_APP.md                  - Complete reference guide
│   ├── MAIN_FLASK_APP_DELIVERY.md         - Delivery documentation
│   ├── MAIN_FLASK_APP_EXAMPLES.md         - Working code examples
│   ├── MAIN_FLASK_APP_COMPLETION.md       - Completion report
│   ├── QUICK_START.md                     - Quick start (5 minutes)
│   ├── INTEGRATION_GUIDE.md                - Integration guide
│   └── INDEX.md                           - Complete index
│
└── 06_project/                            ← Project Information
    ├── PROJECT_STRUCTURE.md               - Project organization
    ├── DELIVERY_PACKAGE.md                - Delivery package contents
    ├── PHASE_2_COMPLETE.md                - Phase 2 completion
    ├── PHASE_2_COMPLETION.md              - Phase 2 completion details
    ├── REORGANIZATION_COMPLETE.md         - Reorganization complete
    ├── REORGANIZATION_SUMMARY.md          - Reorganization summary
    └── DOCS_REORGANIZATION_COMPLETE.md    - Docs reorganization report

```

## 🚀 Quick Navigation

### For New Users
1. Start with [01_getting_started/GETTING_STARTED.md](01_getting_started/GETTING_STARTED.md)
2. Review [01_getting_started/DEVELOPMENT.md](01_getting_started/DEVELOPMENT.md) for setup
3. Check [01_getting_started/SETUP_SUMMARY.md](01_getting_started/SETUP_SUMMARY.md) for instructions
4. See [06_project/PROJECT_STRUCTURE.md](06_project/PROJECT_STRUCTURE.md) for overview

### For Model Development
1. [02_models/xgboost/XGBOOST_MODEL.md](02_models/xgboost/XGBOOST_MODEL.md) - XGBoost models
2. [03_preprocessing/TIMESERIES_PREPROCESSING.md](03_preprocessing/TIMESERIES_PREPROCESSING.md) - Data prep
3. [03_preprocessing/TIMESERIES_QUICK_REFERENCE.md](03_preprocessing/TIMESERIES_QUICK_REFERENCE.md) - Quick ref

### For Service Integration
1. [04_services/model_comparison/MODEL_SELECTOR.md](04_services/model_comparison/MODEL_SELECTOR.md) - Model comparison
2. [04_services/health_risk/HEALTH_RISK_ENGINE.md](04_services/health_risk/HEALTH_RISK_ENGINE.md) - Health risk
3. [04_services/explainability/EXPLAINABILITY_ENGINE.md](04_services/explainability/EXPLAINABILITY_ENGINE.md) - Explainability
4. [05_apis/API_ENDPOINTS_COMPLETE.md](05_apis/API_ENDPOINTS_COMPLETE.md) - REST API endpoints

### For Flask Application
1. [05_main_app/QUICK_START.md](05_main_app/QUICK_START.md) - Get running in 5 minutes
2. [05_main_app/MAIN_FLASK_APP.md](05_main_app/MAIN_FLASK_APP.md) - Complete reference
3. [05_main_app/INTEGRATION_GUIDE.md](05_main_app/INTEGRATION_GUIDE.md) - Integration guide

## 📖 Category Descriptions

### 01 - Getting Started
Entry point documentation covering:
- Project introduction
- Installation and setup
- Development environment configuration
- Initial setup steps

### 02 - Models
Machine learning model implementations:
- **XGBoost**: Gradient boosting model with documentation and integration guide
- Model specifications, usage, and performance

### 03 - Data (Spatial Interpolation)
Data processing for hyper-local air quality:
- Spatial interpolation techniques
- Implementation guide and quick reference

### 03_preprocessing - Time Series Data
Data preparation and transformation:
- Time series preprocessing pipeline
- Feature engineering
- Implementation summary and quick reference

### 04 - Services
Business logic services organized by feature:
- **Model Comparison**: Compare and select best model (Judge Favorite)
- **Health Risk**: Classify health risks from AQI values (6-persona assessment)
- **Explainability**: Rule-based and generative model explanations
- Service architecture and usage

### 05_apis - REST API
REST API endpoint documentation:
- Complete API endpoint reference
- Model comparison API guide
- Request/response formats
- Error handling

### 05_main_app - Flask Application
Main Flask application documentation:
- Application factory and configuration
- Blueprint registration
- CORS setup
- Error handling
- Deployment guide
- Integration with services

### 06 - Project
High-level project information:
- Project structure and organization
- Delivery packages and completion reports
- Phase summaries
- Reorganization notes

## 🔍 Finding What You Need

| Looking for... | Go to... |
|---|---|
| Project setup & installation | [01_getting_started/SETUP_SUMMARY.md](01_getting_started/SETUP_SUMMARY.md) |
| XGBoost model details | [02_models/xgboost/XGBOOST_MODEL.md](02_models/xgboost/XGBOOST_MODEL.md) |
| Spatial interpolation | [03_data/SPATIAL_INTERPOLATION.md](03_data/SPATIAL_INTERPOLATION.md) |
| Data preprocessing guide | [03_preprocessing/TIMESERIES_PREPROCESSING.md](03_preprocessing/TIMESERIES_PREPROCESSING.md) |
| Model comparison service | [04_services/model_comparison/MODEL_SELECTOR.md](04_services/model_comparison/MODEL_SELECTOR.md) |
| Health risk assessment | [04_services/health_risk/HEALTH_RISK_ENGINE.md](04_services/health_risk/HEALTH_RISK_ENGINE.md) |
| Model explainability | [04_services/explainability/EXPLAINABILITY_ENGINE.md](04_services/explainability/EXPLAINABILITY_ENGINE.md) |
| LLM-based explanations | [04_services/explainability/GENERATIVE_EXPLAINER.md](04_services/explainability/GENERATIVE_EXPLAINER.md) |
| Flask application | [05_main_app/QUICK_START.md](05_main_app/QUICK_START.md) |
| API endpoints | [05_apis/API_ENDPOINTS_COMPLETE.md](05_apis/API_ENDPOINTS_COMPLETE.md) |
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
- [MAIN_FLASK_APP.md](05_main_app/MAIN_FLASK_APP.md)

### Quick References
Condensed guides for quick lookup:
- Common use cases
- Code snippets
- Performance info
- Best practices

**Examples**:
- [HEALTH_RISK_QUICK_REF.md](04_services/health_risk/HEALTH_RISK_QUICK_REF.md)
- [TIMESERIES_QUICK_REFERENCE.md](03_preprocessing/TIMESERIES_QUICK_REFERENCE.md)
- [QUICK_START.md](05_main_app/QUICK_START.md)

### Summaries & Completion Reports
Overview documents highlighting:
- Key features
- Implementation status
- Metrics and statistics
- Integration info

**Examples**:
- [JUDGE_FAVORITE_SUMMARY.md](04_services/model_comparison/JUDGE_FAVORITE_SUMMARY.md)
- [MAIN_FLASK_APP_DELIVERY.md](05_main_app/MAIN_FLASK_APP_DELIVERY.md)
- [DELIVERY_PACKAGE.md](06_project/DELIVERY_PACKAGE.md)

## 🎯 By Use Case

### I'm a New Developer
1. Read [01_getting_started/GETTING_STARTED.md](01_getting_started/GETTING_STARTED.md)
2. Follow [01_getting_started/DEVELOPMENT.md](01_getting_started/DEVELOPMENT.md) to setup
3. Review [06_project/PROJECT_STRUCTURE.md](06_project/PROJECT_STRUCTURE.md)
4. Explore the service layer in [04_services/](04_services/)

### I'm Working on Models
1. Check [02_models/xgboost/XGBOOST_MODEL.md](02_models/xgboost/XGBOOST_MODEL.md)
2. Review data prep: [03_preprocessing/](03_preprocessing/)
3. See model selection: [04_services/model_comparison/MODEL_SELECTOR.md](04_services/model_comparison/MODEL_SELECTOR.md)

### I'm Integrating Services
1. Start with [05_main_app/INTEGRATION_GUIDE.md](05_main_app/INTEGRATION_GUIDE.md)
2. Check service docs in [04_services/](04_services/)
3. Review API endpoints: [05_apis/API_ENDPOINTS_COMPLETE.md](05_apis/API_ENDPOINTS_COMPLETE.md)

### I'm Deploying to Production
1. Follow [05_main_app/MAIN_FLASK_APP.md](05_main_app/MAIN_FLASK_APP.md) deployment section
2. Configure in [05_main_app/QUICK_START.md](05_main_app/QUICK_START.md)
3. Verify APIs in [05_apis/](05_apis/)

## 📊 Documentation Statistics

- **Total Categories**: 6
- **Total Sections**: 15+
- **Total Documents**: 47+
- **Code Examples**: Included in all service documentation
- **Quick References**: Available for complex topics
- **Completion Reports**: Available for all major features

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
