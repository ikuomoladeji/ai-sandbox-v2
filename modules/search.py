from . import utils

def print_vendor_block(v):
    print("\n---------------------------------")
    print(f"Org: {v['org_id']}")
    print(f"Vendor: {v['vendor_name']}")
    print(f"Service: {v['service']}")
    print(f"Business Owner: {v['business_owner']}")
    print(f"Overall Control Score: {v['overall_control_score']}/5")
    print(f"Likelihood: {v['likelihood']}")
    print(f"Impact: {v['impact']}")
    print(f"Risk Bucket: {v.get('risk_bucket', utils.classify_risk_bucket(v['likelihood'], v['impact']))}")
    print("Control Scores:")
    for d,s in v["control_scores"].items():
        print(f"  - {d}: {s}/5")
    if v.get("open_actions"):
        print("Open Actions:")
        for a in v["open_actions"]:
            print(f"  - [{a.get('urgency','?').upper()}] {a.get('owner_type','')}: {a.get('action','')}")
    print("---------------------------------\n")

def run(_model_name=None):
    print("\n=== Vendor Search ===")
    db = utils.load_vendor_db()
    if not db:
        print("No vendors recorded yet.")
        return

    org_id = input("Search in which org? (exact name or 'ALL'): ").strip()

    # build scoped vendors list
    scoped = []
    if org_id == "ALL":
        for o, vendors in db.items():
            for vname, vrec in vendors.items():
                scoped.append(vrec)
    else:
        for vname, vrec in db.get(org_id, {}).items():
            scoped.append(vrec)

    print("\n1) Search by vendor name")
    print("2) Search by overall risk bucket (high / medium / low)")
    print("3) Search by weak control domain (e.g. 'logging', 'bcp')")
    print("4) Show all vendors in scope")
    print("5) Show vendors that have open HIGH urgency actions")
    choice = input("Choose 1-5: ").strip()

    if choice == "1":
        name = input("Vendor name (partial ok): ").strip().lower()
        for v in scoped:
            if name in v["vendor_name"].lower():
                print_vendor_block(v)

    elif choice == "2":
        level = input("Risk level (high/medium/low): ").strip().lower()
        for v in scoped:
            bucket = v.get("risk_bucket", utils.classify_risk_bucket(v["likelihood"], v["impact"]))
            if bucket == level:
                print_vendor_block(v)

    elif choice == "3":
        domain = input("Control area substring (e.g. logging, bcp, privacy): ").strip().lower()
        for v in scoped:
            for d,score in v["control_scores"].items():
                if domain in d.lower() and score <= 2:
                    print_vendor_block(v)
                    break

    elif choice == "4":
        for v in scoped:
            print_vendor_block(v)

    elif choice == "5":
        for v in scoped:
            for a in v.get("open_actions", []):
                if a.get("urgency","").lower() == "high":
                    print_vendor_block(v)
                    break

    else:
        print("Invalid choice.")
