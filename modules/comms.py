from pathlib import Path
from . import utils
from modules.api_client import ask_model

def run(model_name):
    print("\n=== Vendor / Stakeholder Communication Draft ===\n")

    db = utils.load_vendor_db()
    if not db:
        print("No vendors found in data/vendors.json yet.")
        return

    org_id = input("Which organisation / client? (exact name): ").strip()
    if org_id not in db:
        print(f"No records for org '{org_id}'.")
        return

    vendor_name = input("Which vendor? (exact name): ").strip()
    if vendor_name not in db[org_id]:
        print(f"Vendor '{vendor_name}' not found under org '{org_id}'.")
        return

    vendor_record = db[org_id][vendor_name]

    # safety check for isolation
    if vendor_record["org_id"] != org_id:
        print("Data isolation check failed. Aborting.")
        return

    print("\nWhat type of message do you want to draft?")
    print("1) Evidence / documentation request to vendor")
    print("2) Remediation follow-up / overdue action to vendor")
    print("3) Status update to internal stakeholder / business owner")
    print("4) Executive summary / escalation note")
    msg_type_choice = input("Choose 1-4: ").strip()

    if msg_type_choice == "1":
        msg_type = "evidence_request"
    elif msg_type_choice == "2":
        msg_type = "remediation_followup"
    elif msg_type_choice == "3":
        msg_type = "internal_update"
    elif msg_type_choice == "4":
        msg_type = "executive_escalation"
    else:
        print("Invalid choice.")
        return

    context_additional = input("Anything specific you want to mention (or leave blank): ").strip()

    audience, redaction = utils.ask_audience_and_redaction()

    # We'll surface open actions to help with the ask.
    actions_snippet = ""
    if vendor_record.get("open_actions"):
        actions_snippet = "\nOpen Actions / Outstanding Items:\n"
        for a in vendor_record["open_actions"]:
            actions_snippet += f"- [{a.get('urgency','').upper()}] {a.get('owner_type','')}: {a.get('action','')}\n"

    prompt = f"""
You are drafting a professional communication.

You must respect strict client isolation:
Only talk about this organisation ({org_id}) and this vendor ({vendor_name}).
Never mention other clients, other vendors, or portfolio context unless explicitly internal.

Message type: {msg_type}
Organisation / Client: {org_id}
Vendor: {vendor_name}
Business owner: {vendor_record['business_owner']}
Vendor service / data handled: {vendor_record['service']}
Current assessed likelihood: {vendor_record['likelihood']}
Current assessed impact: {vendor_record['impact']}
Overall control score: {vendor_record['overall_control_score']}/5
Risk bucket: {vendor_record.get('risk_bucket', utils.classify_risk_bucket(vendor_record['likelihood'], vendor_record['impact']))}

Outstanding tracked actions:
{actions_snippet}

Additional context from analyst:
{context_additional}

Tone requirements:
- Audience type: {audience}
- Redaction level: {redaction}
If audience is 'vendor', be firm but professional, request evidence or remediation, and set expectation for timeline.
If audience is 'internal_update', summarise risk and next steps in plain business language.
If audience is 'executive_escalation', be concise, impact-focused, and include urgency.
If audience is 'vendor', do NOT include internal scoring methodology ("you are critical high risk because..."). Just state what's required.
If audience is 'internal' or 'executive', you MAY reference risk in impact/likelihood terms.
Write as an email body. Do not include greeting placeholders like 'Hi NAME' unless natural.
"""

    print("\n🤖 Generating communication draft with model:", model_name, "...\n")
    message_text = ask_model(model_name, prompt)

    print("\n----- Suggested Message -----\n")
    print(message_text)
    print("\n-----------------------------\n")

    save_choice = input("Save this message to outputs as .txt? (y/n): ").strip().lower()
    if save_choice == "y":
        safe_org = org_id.replace(" ", "_")
        safe_vendor = vendor_name.replace(" ", "_")
        out_dir = Path("outputs")
        out_dir.mkdir(exist_ok=True)
        outfile = out_dir / f"{safe_org}_{safe_vendor}_message.txt"
        outfile.write_text(message_text, encoding="utf-8")
        print(f"✅ Saved draft to {outfile.resolve()}")

    print("\nDone.\n")
