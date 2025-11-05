import json
from pathlib import Path
import requests
from . import utils

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_model(model_name, prompt):
    resp = requests.post(
        OLLAMA_URL,
        json={"model": model_name, "prompt": prompt, "stream": False}
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip()

def build_org_view(db, org_id):
    """
    Returns: dict { vendor_name: vendor_record } scoped to org_id (or ALL).
    """
    if org_id == "ALL":
        merged = {}
        # merge across orgs with vendor_name keyed as "<org>::<vendor>" to avoid clash
        for org, vendors in db.items():
            for vname, vrec in vendors.items():
                merged[f"{org}::{vname}"] = vrec
        return merged
    else:
        return db.get(org_id, {})

def calculate_summary(scoped_vendors):
    total = len(scoped_vendors)
    if total == 0:
        return {
            "total": 0,
            "avg_control": 0,
            "risk_counts": {"high":0,"medium":0,"low":0},
            "weakest_domain": "n/a"
        }

    avg_control = sum(v["overall_control_score"] for v in scoped_vendors.values()) / total

    counts = {"high":0, "medium":0, "low":0}
    domain_scores = {}

    for v in scoped_vendors.values():
        bucket = utils.classify_risk_bucket(v["likelihood"], v["impact"])
        counts[bucket] = counts.get(bucket, 0) + 1

        for d,s in v["control_scores"].items():
            domain_scores.setdefault(d, []).append(s)

    # weakest avg domain
    weakest_domain = "n/a"
    if domain_scores:
        avg_domains = {d: sum(scores)/len(scores) for d, scores in domain_scores.items()}
        weakest_domain = min(avg_domains, key=avg_domains.get)

    return {
        "total": total,
        "avg_control": round(avg_control,2),
        "risk_counts": counts,
        "weakest_domain": weakest_domain
    }

def run(model_name):
    print("\n=== Portfolio / Management Report Generator ===\n")
    db = utils.load_vendor_db()

    org_id = input("Which organisation? (exact name or 'ALL' for internal rollup): ").strip()

    scoped_vendors = build_org_view(db, org_id)
    summary = calculate_summary(scoped_vendors)

    audience, redaction = utils.ask_audience_and_redaction()

    # build narrative prompt
    prompt = f"""
You are a senior risk & compliance manager.

Generate a concise management / board / client report summarizing the third-party risk posture.

Organisation scope: {org_id}
Do NOT mention any other organisation unless org_id is 'ALL'.
Assume strict confidentiality between clients.

Data points:
- Total vendors: {summary['total']}
- Average control score: {summary['avg_control']}
- High-risk vendors: {summary['risk_counts']['high']}
- Medium-risk vendors: {summary['risk_counts']['medium']}
- Low-risk vendors: {summary['risk_counts']['low']}
- Weakest control domain overall: {summary['weakest_domain']}

Write these sections:
1. Executive Overview / Current Posture
2. High-Risk Third Parties (and why they matter)
3. Thematic Weaknesses (logging, DR/BCP, evidence freshness, etc.)
4. Required Actions / Owners / Urgency
   - Vendor-facing asks
   - Internal owner obligations
   - Governance/contractual improvements
5. Recommendations for Next Quarter

Tone requirements:
- Audience type: {audience}
- Redaction level: {redaction}
If audience is 'client', never mention other clients.
If audience is 'vendor', keep focus on what that vendor needs to do, do not expose broader environment.
If audience is 'exec', keep it business-impact focused.
"""

    print("🤖 Generating executive summary with model:", model_name)
    narrative_text = ask_model(model_name, prompt)

    # ask export format
    fmt = utils.ask_output_format()

    # export all the different formats (PPT, PDF, PowerBI, etc.)
    utils.export_portfolio_artifacts(
        org_id=org_id,
        db_for_report=scoped_vendors,
        summary_dict=summary,
        narrative_text=narrative_text,
        fmt=fmt
    )

    print("\n✅ Portfolio report complete.\n")
