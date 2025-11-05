from pathlib import Path
from openpyxl import Workbook
from . import utils

def run():
    print("\n=== Risk Register Export ===\n")
    db = utils.load_vendor_db()
    if not db:
        print("No vendors on record. Nothing to export.")
        return

    org_id = input("Which organisation? (exact name or 'ALL'): ").strip()
    ts = utils.today_short()
    safe_org = org_id.replace(" ", "_")

    # build scoped vendor list
    scoped = []
    if org_id == "ALL":
        for o, vendors in db.items():
            for vname, vrec in vendors.items():
                scoped.append(vrec)
    else:
        for vname, vrec in db.get(org_id, {}).items():
            scoped.append(vrec)

    # build workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Risk Register"

    ws.append([
        "Org",
        "Vendor",
        "Business Owner",
        "Overall Control Score (1-5)",
        "Likelihood (L/M/H)",
        "Impact (L/M/H)",
        "Risk Bucket",
        "Regulatory Scope",
        "Notes / Follow-up"
    ])

    for v in scoped:
        bucket = v.get("risk_bucket", utils.classify_risk_bucket(v["likelihood"], v["impact"]))
        ws.append([
            v["org_id"],
            v["vendor_name"],
            v["business_owner"],
            v["overall_control_score"],
            v["likelihood"],
            v["impact"],
            bucket,
            v["regulator"],
            "See 'Open Actions' tab"
        ])

    # add open actions sheet
    ws2 = wb.create_sheet("Open Actions")
    ws2.append(["Org","Vendor","OwnerType","Urgency","Action","Status"])
    for v in scoped:
        for a in v.get("open_actions", []):
            ws2.append([
                v["org_id"],
                v["vendor_name"],
                a.get("owner_type",""),
                a.get("urgency",""),
                a.get("action",""),
                a.get("status","open")
            ])

    out_path = Path(f"outputs/risk_register_{safe_org}_{ts}.xlsx")
    wb.save(out_path)
    print(f"✅ Risk register Excel created: {out_path.resolve()}")

    txt_path = Path(f"outputs/risk_register_{safe_org}_{ts}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        for v in scoped:
            bucket = v.get("risk_bucket", utils.classify_risk_bucket(v["likelihood"], v["impact"]))
            f.write(
                f"{v['org_id']} | {v['vendor_name']} | Owner={v['business_owner']} | "
                f"Score={v['overall_control_score']} | Likelihood={v['likelihood']} | "
                f"Impact={v['impact']} | Risk={bucket}\n"
            )
    print(f"✅ Risk register text created: {txt_path.resolve()}\n")
