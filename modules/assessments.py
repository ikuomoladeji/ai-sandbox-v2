import json
import datetime
from pathlib import Path
from . import utils
from modules.api_client import ask_model

def run(model_name):   # 👈 this is the entry point main.py is calling
    print("\n=== Vendor Assessment Wizard ===\n")

    db = utils.load_vendor_db()
    org_id = input("Organisation / Client name: ").strip()
    vendor_name = input("Vendor name: ").strip()

    # Ensure structure for multi-org setup
    if org_id not in db:
        db[org_id] = {}

    # If vendor already exists, update; else new entry
    existing = db[org_id].get(vendor_name)
    if existing:
        print(f"Updating existing record for {vendor_name}.")
        vendor = existing
    else:
        vendor = {
            "vendor_name": vendor_name,
            "org_id": org_id,
            "created": datetime.datetime.now().isoformat()
        }

    # Basic info
    vendor["service"] = input("Describe service or data handled: ").strip()
    vendor["business_owner"] = input("Business owner or department: ").strip()
    vendor["assessment_date"] = str(datetime.date.today())

    print("\nScoring controls 1–5 (1=Unacceptable, 5=Strong Control)")
    domains = ["Governance", "Cybersecurity", "Data Protection", "Resilience", "Compliance"]
    scores = {}
    for d in domains:
        while True:
            try:
                val = int(input(f"{d} score (1–5): "))
                if val < 1 or val > 5:
                    raise ValueError
                scores[d] = val
                break
            except ValueError:
                print("Please enter a number between 1 and 5.")
    vendor["control_scores"] = scores
    vendor["overall_control_score"] = round(sum(scores.values()) / len(scores), 2)

    # Likelihood / Impact
    vendor["likelihood"] = input("Likelihood (low/medium/high): ").lower()
    vendor["impact"] = input("Impact (low/medium/high): ").lower()
    vendor["risk_bucket"] = utils.classify_risk_bucket(vendor["likelihood"], vendor["impact"])

    # Ask AI for recommendations
    prompt = f"""
You are a third-party risk analyst. Based on the following control scores, provide:
1. A brief risk summary (2–3 paragraphs)
2. Key strengths
3. Areas of concern
4. 3 recommended improvements the vendor should implement

Vendor: {vendor_name}
Organisation: {org_id}
Service: {vendor['service']}
Scores: {json.dumps(scores, indent=2)}
Likelihood: {vendor['likelihood']}
Impact: {vendor['impact']}
Overall Score: {vendor['overall_control_score']}/5
Risk Bucket: {vendor['risk_bucket']}
"""

    print("\n🤖 Generating analysis and recommendations...")
    ai_text = ask_model(model_name, prompt)
    vendor["ai_analysis"] = ai_text

    # Save to DB
    db[org_id][vendor_name] = vendor
    utils.save_vendor_db(db)
    utils.snapshot_history(org_id, vendor_name, vendor)

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    file_path = out_dir / f"{org_id.replace(' ', '_')}_{vendor_name.replace(' ', '_')}_assessment.txt"
    file_path.write_text(ai_text, encoding="utf-8")

    print(f"\n✅ Vendor assessment complete. Saved to {file_path}\n")
