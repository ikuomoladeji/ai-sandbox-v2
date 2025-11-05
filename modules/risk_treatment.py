import datetime
from pathlib import Path
from . import utils


def classify_treatment_action(risk_level: str):
    lvl = (risk_level or "").strip().lower()
    if lvl == "high":
        return "Mitigate", (
            "Enhance controls or remediation before engagement/renewal. "
            "Escalate to Risk / Legal for contractual clauses."
        )
    elif lvl == "medium":
        return "Transfer", (
            "Include contractual/insurance clauses, document obligations, "
            "and track remediation timelines."
        )
    else:
        return "Accept", (
            "Risk is within tolerance. Maintain monitoring and schedule periodic review."
        )


def build_vendor_rows(db_for_org):
    rows = []
    for vendor_name, record in db_for_org.items():
        risk_level = record.get("risk_level")
        if not risk_level:
            continue
        weighted_score = record.get("weighted_score")
        likelihood = record.get("likelihood", "")
        impact = record.get("impact", "")
        treatment_status, treatment_desc = classify_treatment_action(risk_level)
        rows.append({
            "vendor_name": vendor_name,
            "risk_level": risk_level,
            "likelihood": likelihood,
            "impact": impact,
            "weighted_score": weighted_score,
            "treatment_status": treatment_status,
            "treatment_desc": treatment_desc,
            "assessment_date": record.get("assessment_date", record.get("assessed_at","")),
        })
    return rows


def generate_summary(vendor_rows):
    total = len(vendor_rows)
    if total == 0:
        return None
    high_count = sum(1 for v in vendor_rows if v["risk_level"] == "High")
    med_count = sum(1 for v in vendor_rows if v["risk_level"] == "Medium")
    low_count = sum(1 for v in vendor_rows if v["risk_level"] == "Low")
    treated = sum(1 for v in vendor_rows if v["treatment_status"] in ["Mitigate","Transfer","Accept"])
    completion_pct = round((treated / total) * 100, 1) if total else 0.0
    next_review_date = (datetime.date.today() + datetime.timedelta(days=90)).strftime("%d %B %Y")
    return {
        "total": total,
        "high": high_count,
        "medium": med_count,
        "low": low_count,
        "treated": treated,
        "completion_pct": completion_pct,
        "next_review": next_review_date,
    }


def run(model_name=None):
    print("\n=== Generate Risk Treatment & Management Summary ===")
    org = input("Organisation name: ").strip()

    db = utils.load_vendor_db()
    if org not in db:
        print("❌ Organisation not found in vendor database.")
        return

    vendor_rows = build_vendor_rows(db[org])
    if not vendor_rows:
        print("❌ No assessed vendors with risk_level found for this org. Run option 1 first.")
        return

    _print_org_summary(org, vendor_rows)


def _extract_key_issues(rec):
    issues = []
    for dom in rec.get("domains", []):
        sc = dom.get("score", 0)
        if isinstance(sc, (int, float)) and sc < 4:
            issues.append(f"{dom['name']} score {sc}")
    ev = rec.get("evidence_notes", {}) or {}
    for dom_name, note in ev.items():
        if not note:
            continue
        low = note.lower()
        if "gap" in low or "missing" in low or "no " in low:
            issues.append(f"{dom_name}: {note}")
    if not issues:
        return "None identified"
    return "; ".join(issues)


def _summarize_vendor_record(vendor_name, rec):
    return {
        "vendor": vendor_name,
        "risk_level": rec.get("risk_level", "n/a"),
        "weighted_score": rec.get("weighted_score", "n/a"),
        "likelihood": rec.get("likelihood", "n/a"),
        "impact": rec.get("impact", "n/a"),
        "key_issues": _extract_key_issues(rec),
        "last_assessed": rec.get("assessment_date", rec.get("assessed_at", "")),
    }


def run_for_single_vendor(org, vendor, model_name):
    db = utils.load_vendor_db()
    if org not in db or vendor not in db[org]:
        print(f"[!] Vendor {vendor} not found under {org}")
        return

    rec = db[org][vendor]
    summary = _summarize_vendor_record(vendor, rec)

    print("\n=== Vendor Risk Treatment Summary ===")
    print(f"Organisation: {org}")
    print(f"Vendor: {summary['vendor']}")
    print(f"Risk Rating: {summary['risk_level']}")
    print(f"Weighted Score: {summary['weighted_score']}")
    print(f"Likelihood / Impact: {summary['likelihood']} / {summary['impact']}")
    print(f"Key Issue(s): {summary['key_issues']}")
    print(f"Last Assessed: {summary['last_assessed']}")
    print("Recommended Treatment: Mitigate / Transfer / Avoid / Accept")
    print("-------------------------------------")

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    safe_org = org.replace(" ", "_")
    safe_vendor = vendor.replace(" ", "_")
    nowstamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"{safe_org}_{safe_vendor}_Treatment_Summary_{nowstamp}.txt"

    lines = [
        f"Organisation: {org}",
        f"Vendor: {summary['vendor']}",
        f"Risk Rating: {summary['risk_level']}",
        f"Weighted Score: {summary['weighted_score']}",
        f"Likelihood / Impact: {summary['likelihood']} / {summary['impact']}",
        f"Last Assessed: {summary['last_assessed']}",
        f"Key Issues: {summary['key_issues']}",
        "Recommended Treatment: [Mitigate / Transfer / Avoid / Accept]",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n📝 Vendor treatment summary saved: {out_path.resolve()}\n")


def run_for_org(org, model_name):
    db = utils.load_vendor_db()
    if org not in db or not db[org]:
        print(f"[!] No vendors found for {org}")
        return

    summaries = []
    for v_name, rec in db[org].items():
        summaries.append(_summarize_vendor_record(v_name, rec))

    total = len(summaries)
    high = sum(1 for s in summaries if str(s["risk_level"]).lower().startswith("high"))
    med  = sum(1 for s in summaries if str(s["risk_level"]).lower().startswith("med"))
    low  = sum(1 for s in summaries if str(s["risk_level"]).lower().startswith("low"))

    # future calc: treatment completion % / next review date escalation
    treated_pct = "N/A"
    next_review = "TBD"

    print("\n========== Management Summary ==========")
    print(f"Organisation: {org}")
    print(f"Total Vendors Reviewed: {total}")
    print(f"High-Risk Vendors: {high}")
    print(f"Medium-Risk Vendors: {med}")
    print(f"Low-Risk Vendors: {low}")
    print(f"Treatment Completion: {treated_pct}")
    print(f"Next Review Date: {next_review}")
    print("\nObservations / Recommendations:")
    print("- Review high-risk vendors first.")
    print("- Ensure contractual clauses (BCP, breach notification, audit rights) are embedded.")
    print("- Formalise quarterly vendor risk review for critical suppliers.")
    print("---------------------------------------")

    print("\nVendor Risk Register")
    print("(Vendor | Risk Rating | Key Issues | Last Assessed)")
    for s in summaries:
        print(f"- {s['vendor']} | {s['risk_level']} | {s['key_issues']} | {s['last_assessed']}")
    print("---------------------------------------\n")

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    safe_org = org.replace(" ", "_")
    nowstamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"{safe_org}_Org_Management_Summary_{nowstamp}.txt"

    lines = []
    lines.append(f"Organisation: {org}")
    lines.append(f"Total Vendors Reviewed: {total}")
    lines.append(f"High-Risk Vendors: {high}")
    lines.append(f"Medium-Risk Vendors: {med}")
    lines.append(f"Low-Risk Vendors: {low}")
    lines.append(f"Treatment Completion: {treated_pct}")
    lines.append(f"Next Review Date: {next_review}")
    lines.append("")
    lines.append("Vendor Risk Register (Vendor | Risk | Key Issues | Last Assessed)")
    for s in summaries:
        lines.append(
            f"{s['vendor']} | {s['risk_level']} | {s['key_issues']} | {s['last_assessed']}"
        )
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"📊 Org management summary saved: {out_path.resolve()}\n")


def _print_org_summary(org, vendor_rows):
    # vendor_rows is from build_vendor_rows (org-level classification)
    summary = generate_summary(vendor_rows)
    if not summary:
        print("No summary could be generated.")
        return

    print("\n========== Management Summary ==========")
    print(f"Organisation: {org}")
    print(f"Total Vendors Reviewed: {summary['total']}")
    print(f"High-Risk Vendors: {summary['high']}")
    print(f"Medium-Risk Vendors: {summary['medium']}")
    print(f"Low-Risk Vendors: {summary['low']}")
    print(f"Treatment Completion: {summary['completion_pct']}%")
    print(f"Next Review Date: {summary['next_review']}")
    print("\nRecommendations:")
    print("- Continue quarterly vendor risk reviews for critical suppliers.")
    print("- Enforce contractual risk clauses upon renewal.")
    print("- Track remediation for high-risk vendors before renewal.")
    print("---------------------------------------")

    print("\nVendor Risk Register:")
    print("(Vendor | Risk Rating | Likelihood/Impact | Treatment Status | Last Assessed)")
    for idx, row in enumerate(vendor_rows, start=1):
        print(
            f"{idx}. {row['vendor_name']} | {row['risk_level']} | "
            f"{row['likelihood']}/{row['impact']} | {row['treatment_status']} | {row['assessment_date']}"
        )
    print("---------------------------------------\n")
