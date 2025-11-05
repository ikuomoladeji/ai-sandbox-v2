#!/usr/bin/env python3
"""
Import MaryMia Ltd Third-Party Risk Management Work
===================================================
This script imports completed TPRM deliverables from the thirdpartyrisk/ folder
into the AI-powered TPRM system for MaryMia Ltd.

Deliverables to import:
- Vendor inventory and classification
- DDQ weighted scoring results
- Risk treatment plans
- Contract clause reviews
- Continuous monitoring registers
- Incident response documentation
- Audit readiness evidence

Author: Adedeji Ikuomola
Date: 2025-11-05
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

# Paths
SOURCE_DIR = Path("thirdpartyrisk")
OUTPUTS_DIR = Path("outputs/marymia_ltd")
DATA_DIR = Path("data")
HISTORY_DIR = Path("history")

# MaryMia Ltd deliverable files mapping
DELIVERABLES = {
    "vendor_inventory": "Vendor inventory draft compiled.xlsx",
    "ddq_scoring": "MarymiaLtd_Robust_DDQ_Weighted_Scoring.xlsx",
    "risk_treatment": "MarymiaLtd_Vendor_Risk_Treatment_Plan.xlsx",
    "risk_treatment_pdf": "MarymiaLtd_Vendor_Risk_Treatment_Plan.pdf",
    "contract_review": "MarymiaLtd_Contract_Clause_Review.xlsx",
    "continuous_monitoring": "MarymiaLtd ContinuousMonitoring.xlsx",
    "incident_pack": "MarymiaLtd Incident_Pack.xlsx",
    "audit_readiness": "MarymiaLtd AuditReadiness.xlsx",
    "executive_summary": "MarymiaLtd_Executive_Summary.pdf",
    "vendor_comms": "Vendor Communication.docx",
    "risk_classification": "Vendor Risk Classification Rules.docx",
}


def create_directory_structure():
    """Create necessary directories for imported work."""
    print("\n[*] Creating directory structure...")

    directories = [
        OUTPUTS_DIR,
        OUTPUTS_DIR / "assessments",
        OUTPUTS_DIR / "reports",
        OUTPUTS_DIR / "communications",
        OUTPUTS_DIR / "compliance",
        DATA_DIR,
        HISTORY_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"    ✓ {directory}")


def copy_deliverables():
    """Copy all MaryMia Ltd deliverables to the outputs directory."""
    print("\n[*] Copying MaryMia Ltd deliverables...")

    # Mapping deliverables to subdirectories
    file_mappings = {
        "vendor_inventory": "assessments",
        "ddq_scoring": "assessments",
        "risk_treatment": "reports",
        "risk_treatment_pdf": "reports",
        "contract_review": "compliance",
        "continuous_monitoring": "reports",
        "incident_pack": "compliance",
        "audit_readiness": "compliance",
        "executive_summary": "reports",
        "vendor_comms": "communications",
        "risk_classification": "compliance",
    }

    copied_files = []

    for key, filename in DELIVERABLES.items():
        source_path = SOURCE_DIR / filename
        subdirectory = file_mappings.get(key, "reports")
        dest_path = OUTPUTS_DIR / subdirectory / filename

        if source_path.exists():
            shutil.copy2(source_path, dest_path)
            print(f"    ✓ {filename} → {subdirectory}/")
            copied_files.append({
                "name": filename,
                "category": subdirectory,
                "path": str(dest_path),
                "imported_at": datetime.now().isoformat()
            })
        else:
            print(f"    ✗ {filename} (not found)")

    return copied_files


def create_import_metadata(copied_files):
    """Create metadata file documenting the import."""
    print("\n[*] Creating import metadata...")

    metadata = {
        "organization": "Marymia Ltd",
        "import_date": datetime.now().isoformat(),
        "import_source": "thirdpartyrisk/",
        "deliverables_count": len(copied_files),
        "deliverables": copied_files,
        "methodology": {
            "framework": "ISO 27001 (Annex A.15 & A.16)",
            "regulations": ["GDPR"],
            "lifecycle_phases": [
                "Vendor identification & tiering",
                "Due diligence & evidence review",
                "Risk scoring & treatment",
                "Continuous monitoring",
                "Incident management",
                "Audit readiness reporting"
            ]
        },
        "engagement_details": {
            "analyst": "Ikuomola Adedeji",
            "engagement_date": "July 2024",
            "outcome": "Substantially Compliant vendor risk posture",
            "status": "Completed"
        },
        "system_integration": {
            "integrated_into": "AI-Powered TPRM System",
            "data_location": "data/vendors.json",
            "outputs_location": "outputs/marymia_ltd/",
            "notes": "Deliverables organized by category for easy reference"
        }
    }

    metadata_path = OUTPUTS_DIR / "import_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"    ✓ Metadata saved to {metadata_path}")
    return metadata


def create_marymia_readme():
    """Create a README for the MaryMia Ltd imported work."""
    print("\n[*] Creating MaryMia Ltd documentation...")

    readme_content = """# MaryMia Ltd - Third-Party Risk Management Work

## Overview

This directory contains completed Third-Party Risk Management (TPRM) deliverables for **MaryMia Ltd**,
imported from the original engagement conducted in July 2024.

## Engagement Summary

- **Client**: MaryMia Ltd
- **Analyst**: Ikuomola Adedeji
- **Engagement Date**: July 2024
- **Framework**: ISO 27001 (Annex A.15 & A.16)
- **Compliance**: GDPR
- **Outcome**: Substantially Compliant vendor risk posture

## Directory Structure

```
outputs/marymia_ltd/
├── assessments/           # Vendor assessments and DDQ scoring
├── reports/              # Risk reports and treatment plans
├── communications/       # Vendor and stakeholder communications
├── compliance/           # Compliance documentation and audit evidence
└── import_metadata.json  # Import tracking metadata
```

## Deliverables Included

### Assessments
- Vendor inventory and classification register
- Weighted Due-Diligence Questionnaire (DDQ) with scoring

### Risk Reports
- Risk treatment and mitigation plans
- Continuous monitoring register
- Executive summary report

### Compliance
- Contract security clauses review
- Incident simulation pack
- Audit readiness evidence
- Risk classification rules

### Communications
- Vendor communication templates

## Methodology

The engagement followed a comprehensive third-party risk lifecycle:

1. **Vendor Identification & Tiering** - Classification and prioritization
2. **Due Diligence & Evidence Review** - Detailed assessment and validation
3. **Risk Scoring & Treatment** - Quantitative risk analysis and remediation planning
4. **Continuous Monitoring** - Ongoing risk tracking via KRIs
5. **Incident Management** - Preparedness simulation and response protocols
6. **Audit Readiness Reporting** - ISO 27001 mapping and evidence compilation

## Integration with TPRM System

This work has been integrated into the AI-Powered TPRM System:

- **Vendor Data**: Available in `data/vendors.json` under "Marymia ltd" organization
- **Deliverables**: Organized in this directory by category
- **Accessibility**: Can be referenced in system reports and communications

## Using This Work

### View Existing Assessments
```bash
python main.py
# Select option: Search & Filter
# Query: org:Marymia ltd
```

### Generate New Reports
```bash
python main.py
# Select option: Portfolio Reports
# Organization: Marymia ltd
```

### Launch Dashboard
```bash
streamlit run dashboard.py
# Filter by: Marymia ltd
```

## Next Steps

To continue building on this work:

1. **Add New Vendors** - Use the bulk import or individual assessment features
2. **Update Existing Assessments** - Re-score vendors as they evolve
3. **Generate Periodic Reports** - Create quarterly/annual portfolio reviews
4. **Track Remediation** - Monitor risk treatment plan progress
5. **Maintain Continuous Monitoring** - Update KRIs and watchlists

## Contact

For questions about this engagement or deliverables:
- **Analyst**: Ikuomola Adedeji
- **Role**: Third-Party Risk Analyst | Cybersecurity Consultant

---

*Imported on: {import_date}*
*Source: thirdpartyrisk/ repository*
"""

    readme_path = OUTPUTS_DIR / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content.format(import_date=datetime.now().strftime("%Y-%m-%d")))

    print(f"    ✓ README saved to {readme_path}")


def update_main_readme():
    """Update the main README to reference the imported work."""
    print("\n[*] Updating main README...")

    main_readme_path = Path("README.md")

    if not main_readme_path.exists():
        print("    ✗ Main README not found")
        return

    with open(main_readme_path, 'r') as f:
        content = f.read()

    # Check if already updated
    if "## MaryMia Ltd Engagement" in content:
        print("    ℹ Main README already references MaryMia Ltd work")
        return

    # Add section before "## Support" or at the end
    new_section = """
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

"""

    # Insert before "## Support" section
    if "## Support" in content:
        content = content.replace("## Support", new_section + "## Support")
    else:
        # Append at the end if no Support section
        content += "\n" + new_section

    with open(main_readme_path, 'w') as f:
        f.write(content)

    print("    ✓ Main README updated with MaryMia Ltd section")


def print_summary(metadata):
    """Print import summary."""
    print("\n" + "="*70)
    print("IMPORT COMPLETE - MARYMIA LTD TPRM WORK")
    print("="*70)
    print(f"\n📁 Deliverables Imported: {metadata['deliverables_count']}")
    print(f"📍 Location: {OUTPUTS_DIR}")
    print(f"📅 Import Date: {metadata['import_date']}")
    print(f"\n🎯 Engagement Details:")
    print(f"   Organization: MaryMia Ltd")
    print(f"   Analyst: {metadata['engagement_details']['analyst']}")
    print(f"   Date: {metadata['engagement_details']['engagement_date']}")
    print(f"   Outcome: {metadata['engagement_details']['outcome']}")
    print(f"\n✓ Files organized by category:")

    categories = {}
    for file_info in metadata['deliverables']:
        category = file_info['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(file_info['name'])

    for category, files in sorted(categories.items()):
        print(f"\n   {category.upper()}:")
        for filename in files:
            print(f"      • {filename}")

    print(f"\n📖 Documentation: {OUTPUTS_DIR}/README.md")
    print(f"📊 Metadata: {OUTPUTS_DIR}/import_metadata.json")
    print("\n" + "="*70)
    print("\nNext Steps:")
    print("1. Review imported deliverables in outputs/marymia_ltd/")
    print("2. Run 'python main.py' to access the TPRM system")
    print("3. Use 'Search & Filter' to view MaryMia Ltd vendor data")
    print("4. Launch dashboard with 'streamlit run dashboard.py'")
    print("\n" + "="*70 + "\n")


def main():
    """Main import workflow."""
    print("\n" + "="*70)
    print("MARYMIA LTD TPRM WORK IMPORT TOOL")
    print("="*70)
    print("\nImporting completed Third-Party Risk Management deliverables")
    print("from thirdpartyrisk/ into the AI-Powered TPRM System...")

    try:
        # Execute import steps
        create_directory_structure()
        copied_files = copy_deliverables()
        metadata = create_import_metadata(copied_files)
        create_marymia_readme()
        update_main_readme()
        print_summary(metadata)

        print("✅ Import completed successfully!\n")
        return 0

    except Exception as e:
        print(f"\n❌ Import failed: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
