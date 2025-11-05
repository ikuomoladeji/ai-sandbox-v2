# AI-Powered TPRM System

A comprehensive AI-powered Third-Party Risk Management (TPRM) system for automated vendor risk assessment, portfolio management, and compliance reporting. This system leverages local LLM inference to generate intelligent risk analyses, reports, and communications.

## Overview

An enterprise-grade CLI application for managing third-party vendor risk assessments across multiple organizations. The system provides structured DDQ scoring, weighted risk calculations, multi-format reporting, and AI-powered narrative generation.

## Features

A complete vendor risk management command center with:

- **Vendor Assessment Workflow**: Interactive DDQ (Due Diligence Questionnaire) scoring across 7 weighted control domains
- **Portfolio Management**: Generate comprehensive reports across vendors and organizations
- **Risk Register Export**: Export risk registers to Excel with detailed breakdowns
- **Risk Acceptance Memos**: Generate formal risk acceptance documentation
- **Stakeholder Communications**: Draft vendor and stakeholder communications
- **Risk Treatment Summaries**: Create board-level risk treatment reports
- **Bulk Import**: Import vendors from Excel spreadsheets
- **Search & Filter**: Query vendors and open actions
- **Interactive Dashboard**: Real-time risk analytics with Streamlit visualizations

#### Control Domains

The system evaluates vendors across 7 weighted domains:

1. **Data Protection** (25%) - Encryption, retention, certifications
2. **Compliance** (15%) - GDPR, HIPAA, PCI-DSS compliance
3. **Access Control** (15%) - MFA, access reviews, offboarding
4. **Incident Response** (15%) - IR plans, testing, escalation
5. **Business Continuity** (10%) - BCP/DR plans, RTO/RPO
6. **Subprocessor Management** (10%) - 4th party risk, exit plans
7. **Governance & Documentation** (10%) - Policies, roles, responsibilities

## Installation

### Prerequisites

- Python 3.8+
- Access to VPS running Ollama
- Required Python packages (see Requirements section)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ikuomoladeji/ai-sandbox-v2.git
cd ai-sandbox-v2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure VPS Ollama connection:
```bash
# Create your private .env file (not committed to git)
cp .env.example .env

# Edit .env with your VPS Ollama endpoint
nano .env
```

4. Update the OLLAMA_URL in `.env`:
```bash
# Replace YOUR_VPS_IP with your actual VPS address
OLLAMA_URL=http://YOUR_VPS_IP:11434/api/generate
OLLAMA_MODEL=llama3.2:3b
```

**🔒 Security Note:**
- Never commit your `.env` file - it contains your private VPS endpoint
- Ensure your VPS has proper firewall rules and authentication
- Use VPN or SSH tunneling for additional security

## Usage

### Running the TPRM System

```bash
python main.py
```

Follow the interactive menu to:
1. **Vendor Assessment** - New or update existing vendor assessments
2. **Portfolio Reports** - Generate management summaries for organizations
3. **Search & Filter** - Query vendors and open actions
4. **Risk Register Export** - Export comprehensive risk registers to Excel
5. **Risk Acceptance Memos** - Generate formal risk acceptance documentation
6. **Stakeholder Communications** - Draft vendor and stakeholder communications
7. **Risk Treatment Summaries** - Create board-level risk treatment reports
8. **Bulk Import** - Import vendors from Excel templates
9. **Interactive Dashboard** - Launch real-time analytics dashboard
10. **Continuous Monitoring** - (Coming soon) Automated watchlist tracking

### Running the Interactive Dashboard

Launch the Streamlit dashboard directly:

```bash
streamlit run dashboard.py
```

Or access it from the main menu (Option 9).

**Dashboard Features:**
- 📊 Real-time vendor risk distribution
- 🔥 Risk heat maps (Likelihood vs Impact)
- 📈 Control domain performance analysis
- 📅 Assessment timeline visualization
- 🏢 Organization-level comparisons
- 📋 Interactive vendor portfolio table with filters
- 📥 CSV export functionality
- 🔄 Auto-refresh capability

The dashboard automatically loads data from `data/vendors.json` and provides interactive visualizations powered by Plotly and Streamlit.

## Project Structure

```
ai-sandbox-v2/
├── main.py                    # Main entry point for TPRM system
├── dashboard.py               # Streamlit dashboard application
├── config.py                  # Centralized configuration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore patterns
├── modules/                  # Risk management modules
│   ├── __init__.py
│   ├── tprm_ddq.py           # Vendor assessment & DDQ scoring
│   ├── reports.py            # Portfolio & management reporting
│   ├── search.py             # Vendor search & filtering
│   ├── register.py           # Risk register export
│   ├── acceptances.py        # Risk acceptance memo generation
│   ├── comms.py              # Communication drafting
│   ├── risk_treatment.py     # Risk treatment summaries
│   ├── importer.py           # Bulk vendor import
│   ├── dashboard_launcher.py # Dashboard launcher module
│   ├── assessments.py        # Assessment utilities
│   └── utils.py              # Common utilities
├── data/                     # Vendor database (JSON)
│   └── vendors.json
├── history/                  # Historical snapshots
└── outputs/                  # Generated reports and exports
```

## Data Storage

- **Vendor Database**: `data/vendors.json` - Multi-organization vendor records
- **History**: `history/` - Point-in-time snapshots of assessments
- **Outputs**: `outputs/` - Generated reports (Excel, PDF, Word, PowerPoint, etc.)

## Output Formats

The system supports multiple output formats:

- **Excel** (.xlsx) - Structured data with multiple sheets
- **Word** (.docx) - Narrative reports with formatting
- **PDF** - Print-ready assessment documents
- **PowerPoint** (.pptx) - Executive presentations and board packs
- **Power BI** (CSV) - Dashboard-ready datasets
- **Python** (.py) - Data exports as Python modules
- **Text** (.txt) - Plain text audit trails

## Configuration

### Available Models on VPS

Available models:
- `llama3.2:3b` (default, lightweight & fast)
- `llama3.2:1b` (ultra-lightweight)
- `llama3.2:latest`
- `llama3:latest`
- `mistral:latest`

Select model in `.env` or use environment variables:
```bash
export OLLAMA_MODEL=llama3.2:3b
```

### VPS Ollama Configuration

**Required:** System requires VPS Ollama endpoint configured in `.env`

To configure your VPS Ollama instance:

1. Create private `.env` file:
```bash
cp .env.example .env
```

2. Edit configuration in `.env`:
```bash
# Configure your VPS Ollama endpoint
OLLAMA_URL=http://YOUR_VPS_IP:11434/api/generate
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TIMEOUT=120
```

3. Your `.env` file is automatically ignored by git and stays private.

**🔒 Security Best Practices:**
- Never commit `.env` files to git
- Ensure VPS has proper firewall rules (restrict port 11434 to your IP)
- Use strong authentication on VPS
- Consider using VPN or SSH tunneling for additional security
- Regularly update VPS security patches

## Risk Scoring Methodology

### Domain-Level Scoring
Each question is scored 1-5:
- **5** = Strong control (evidence verified)
- **4** = Acceptable control (minor gaps)
- **3** = Moderate control (some gaps)
- **2** = Weak control (no formal process)
- **1** = Unacceptable (missing control)

### Weighted Calculation
- Each domain has questions weighted equally within the domain
- Domain scores are averaged and weighted by domain importance (%)
- Total weighted score determines overall risk level

### Risk Classification
- **Low Risk**: Total weighted score ≥ 4.0
- **Medium Risk**: Total weighted score ≥ 3.0 and < 4.0
- **High Risk**: Total weighted score < 3.0

### Risk Bucketing
Risk bucket = Likelihood × Impact:
- **High**: Product ≥ 7
- **Medium**: Product ≥ 4 and < 7
- **Low**: Product < 4

Where: low=1, medium=2, high=3

## Development

### Adding New Modules

1. Create module in `modules/` directory
2. Implement a `run()` function (with optional `model_name` parameter)
3. Add menu option in `main.py`
4. Import and call module in the main menu handler

Example:
```python
# In main.py
elif choice == "11":
    try:
        mod = importlib.import_module("modules.new_module")
        mod.run(model_name)
    except Exception as e:
        print(f"[!] Error: {e}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is available for educational and commercial use.

## Authors

- Adedeji Ikuomola

## Acknowledgments

- Built with [Ollama](https://ollama.ai/) for local LLM inference
- Uses OpenPyXL, ReportLab, python-pptx, and python-docx for document generation


## MaryMia Ltd Engagement

This repository includes completed Third-Party Risk Management work for **MaryMia Ltd**,
delivered in July 2024. The engagement deliverables are organized in `outputs/marymia_ltd/`
and include:

- Vendor inventory and weighted DDQ assessments
- Risk treatment and mitigation plans
- Contract security clause reviews
- Continuous monitoring registers
- Incident response documentation
- Audit readiness evidence (ISO 27001 mapping)

**View Details**: See `outputs/marymia_ltd/README.md` for complete documentation.

**Engagement Outcome**: MaryMia Ltd achieved a **Substantially Compliant** vendor risk
posture with measurable reduction in residual risk.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Roadmap

- [ ] Continuous monitoring / watchlist module
- [ ] Database integration (PostgreSQL/SQLite)
- [ ] Web UI interface
- [ ] API endpoints for integrations
- [ ] Enhanced visualizations and dashboards
- [ ] Automated vendor outreach workflows
- [ ] Contract lifecycle management
- [ ] Risk appetite configuration
- [ ] Multi-language support
