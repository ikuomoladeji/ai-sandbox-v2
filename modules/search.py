"""
Vendor search and filtering with production features
"""
from typing import List, Dict, Any
from . import utils
from modules.logger import get_logger, TPRMLogger
from modules.validators import InputValidator, ValidationError

logger = get_logger(__name__)

def print_vendor_block(v: Dict[str, Any]) -> None:
    """
    Print formatted vendor information block

    Args:
        v: Vendor record dictionary
    """
    try:
        risk_bucket = v.get('risk_bucket', utils.classify_risk_bucket(v['likelihood'], v['impact']))

        print("\n" + "="*70)
        print(f"📊 Organization: {v.get('org_id', 'N/A')}")
        print(f"🏢 Vendor: {v.get('vendor_name', 'N/A')}")
        print(f"📋 Service: {v.get('service', 'N/A')}")
        print(f"👤 Business Owner: {v.get('business_owner', 'N/A')}")
        print(f"⚖️  Overall Control Score: {v.get('overall_control_score', 'N/A')}/5")
        print(f"📉 Likelihood: {v.get('likelihood', 'N/A').upper()}")
        print(f"📈 Impact: {v.get('impact', 'N/A').upper()}")

        # Color-code risk bucket
        risk_display = risk_bucket.upper()
        if risk_bucket == 'high':
            risk_display = f"🔴 {risk_display} RISK"
        elif risk_bucket == 'medium':
            risk_display = f"🟡 {risk_display} RISK"
        else:
            risk_display = f"🟢 {risk_display} RISK"

        print(f"⚠️  Risk Bucket: {risk_display}")

        # Control scores with visual indicators
        control_scores = v.get("control_scores", {})
        if control_scores:
            print(f"\n📋 Control Domain Scores:")
            for domain, score in control_scores.items():
                indicator = "✅" if score >= 4 else ("⚠️" if score >= 3 else "❌")
                print(f"   {indicator} {domain}: {score}/5")

        # Open actions
        open_actions = v.get("open_actions", [])
        if open_actions:
            print(f"\n📌 Open Actions ({len(open_actions)}):")
            for idx, action in enumerate(open_actions, 1):
                urgency = action.get('urgency', '?').upper()
                urgency_icon = "🔴" if urgency == "HIGH" else ("🟡" if urgency == "MEDIUM" else "🟢")
                owner = action.get('owner_type', 'Unknown')
                action_text = action.get('action', 'No description')
                print(f"   {idx}. {urgency_icon} [{urgency}] {owner}: {action_text}")

        print("="*70 + "\n")

    except Exception as e:
        logger.error(f"Error displaying vendor block: {e}")
        print(f"❌ Error displaying vendor information: {e}")

def run(_model_name=None):
    """
    Main search function with enhanced filtering and analytics
    """
    try:
        print("\n" + "="*70)
        print("  VENDOR SEARCH & ANALYTICS")
        print("="*70)

        logger.info("Starting vendor search")
        TPRMLogger.log_user_action(logger, "vendor_search_start")

        # Load database
        try:
            db = utils.load_vendor_db()
        except Exception as e:
            logger.error(f"Failed to load vendor database: {e}")
            print(f"❌ Error loading vendor database: {e}")
            return

        if not db:
            print("\n⚠️  No vendors recorded yet.")
            print("💡 Use option 1 from main menu to assess vendors first.")
            return

        # Get organization scope with validation
        print(f"\n📂 Available Organizations ({len(db)}):")
        for idx, org_name in enumerate(sorted(db.keys()), 1):
            vendor_count = len(db[org_name])
            print(f"   {idx}. {org_name} ({vendor_count} vendors)")

        try:
            org_id = input("\n👉 Search in which org? (exact name or 'ALL'): ").strip()
            if org_id != "ALL":
                org_id = InputValidator.validate_organization_name(org_id)
        except ValidationError as e:
            print(f"❌ {e}")
            return

        # Build scoped vendors list
        scoped = []
        if org_id == "ALL":
            for o, vendors in db.items():
                for vname, vrec in vendors.items():
                    scoped.append(vrec)
            logger.info(f"Searching across all organizations: {len(scoped)} vendors")
        else:
            if org_id not in db:
                print(f"❌ Organization '{org_id}' not found in database")
                return
            for vname, vrec in db.get(org_id, {}).items():
                scoped.append(vrec)
            logger.info(f"Searching in {org_id}: {len(scoped)} vendors")

        if not scoped:
            print(f"\n⚠️  No vendors found for {org_id}")
            return

        # Display search menu
        print(f"\n🔍 SEARCH OPTIONS (Scope: {len(scoped)} vendors)")
        print("-" * 70)
        print("  1. Search by vendor name")
        print("  2. Filter by risk bucket (High/Medium/Low)")
        print("  3. Find weak control domains (score ≤ 2)")
        print("  4. Show all vendors in scope")
        print("  5. Filter by high-urgency open actions")
        print("  6. Advanced analytics and statistics")
        print("  7. Export search results to file")
        print("-" * 70)

        try:
            choice = input("\n👉 Choose option (1-7): ").strip()
            choice = InputValidator.validate_menu_choice(choice, ["1","2","3","4","5","6","7"])
        except ValidationError:
            print("❌ Invalid choice. Please choose 1-7.")
            return

        TPRMLogger.log_user_action(logger, "vendor_search", {"choice": choice, "scope": org_id})

        results = []

        if choice == "1":
            name = input("\n👉 Vendor name (partial match ok): ").strip()
            if not name:
                print("❌ Please enter a vendor name")
                return

            name_lower = name.lower()
            for v in scoped:
                if name_lower in v.get("vendor_name", "").lower():
                    results.append(v)
                    print_vendor_block(v)

            if not results:
                print(f"\n⚠️  No vendors found matching '{name}'")
            else:
                print(f"\n✅ Found {len(results)} vendor(s) matching '{name}'")

        elif choice == "2":
            try:
                level = input("\n👉 Risk level (high/medium/low): ").strip()
                level = InputValidator.validate_risk_level(level)
            except ValidationError as e:
                print(f"❌ {e}")
                return

            for v in scoped:
                bucket = v.get("risk_bucket", utils.classify_risk_bucket(v["likelihood"], v["impact"]))
                if bucket == level:
                    results.append(v)
                    print_vendor_block(v)

            if not results:
                print(f"\n⚠️  No {level.upper()} risk vendors found")
            else:
                print(f"\n✅ Found {len(results)} {level.upper()} risk vendor(s)")

        elif choice == "3":
            domain = input("\n👉 Control domain keyword (e.g., 'Data Protection', 'Compliance'): ").strip()
            if not domain:
                print("❌ Please enter a control domain keyword")
                return

            domain_lower = domain.lower()
            for v in scoped:
                control_scores = v.get("control_scores", {})
                for d, score in control_scores.items():
                    if domain_lower in d.lower() and score <= 2:
                        results.append(v)
                        print_vendor_block(v)
                        break

            if not results:
                print(f"\n⚠️  No vendors with weak '{domain}' controls found")
            else:
                print(f"\n✅ Found {len(results)} vendor(s) with weak '{domain}' controls")

        elif choice == "4":
            print(f"\n📊 Displaying all {len(scoped)} vendors...\n")
            for v in scoped:
                results.append(v)
                print_vendor_block(v)

        elif choice == "5":
            for v in scoped:
                open_actions = v.get("open_actions", [])
                for a in open_actions:
                    if a.get("urgency", "").lower() == "high":
                        results.append(v)
                        print_vendor_block(v)
                        break

            if not results:
                print("\n✅ No vendors with HIGH urgency open actions found")
            else:
                print(f"\n⚠️  Found {len(results)} vendor(s) with HIGH urgency actions")

        elif choice == "6":
            _display_analytics(scoped)

        elif choice == "7":
            _export_search_results(scoped, org_id)

        logger.info(f"Search completed: {len(results)} results found")

    except KeyboardInterrupt:
        print("\n\n⚠️  Search cancelled by user")
        logger.info("Search cancelled by user")
    except Exception as e:
        logger.error(f"Error in vendor search: {e}", exc_info=True)
        print(f"\n❌ Error during search: {e}")
        print("Check logs for details")


def _display_analytics(vendors: List[Dict[str, Any]]) -> None:
    """
    Display analytics and statistics for vendor list

    Args:
        vendors: List of vendor records
    """
    print("\n" + "="*70)
    print("  VENDOR RISK ANALYTICS")
    print("="*70)

    total = len(vendors)
    if total == 0:
        print("\n⚠️  No vendors to analyze")
        return

    # Risk distribution
    high_risk = sum(1 for v in vendors if v.get("risk_bucket", utils.classify_risk_bucket(v["likelihood"], v["impact"])) == "high")
    med_risk = sum(1 for v in vendors if v.get("risk_bucket", utils.classify_risk_bucket(v["likelihood"], v["impact"])) == "medium")
    low_risk = sum(1 for v in vendors if v.get("risk_bucket", utils.classify_risk_bucket(v["likelihood"], v["impact"])) == "low")

    print(f"\n📊 RISK DISTRIBUTION:")
    print(f"   🔴 High Risk: {high_risk} ({high_risk/total*100:.1f}%)")
    print(f"   🟡 Medium Risk: {med_risk} ({med_risk/total*100:.1f}%)")
    print(f"   🟢 Low Risk: {low_risk} ({low_risk/total*100:.1f}%)")

    # Average control score
    scores = [v.get("overall_control_score", 0) for v in vendors if v.get("overall_control_score")]
    if scores:
        avg_score = sum(scores) / len(scores)
        print(f"\n⚖️  AVERAGE CONTROL SCORE: {avg_score:.2f}/5")

    # Open actions analysis
    total_actions = sum(len(v.get("open_actions", [])) for v in vendors)
    vendors_with_actions = sum(1 for v in vendors if v.get("open_actions"))
    high_urgency_actions = sum(
        sum(1 for a in v.get("open_actions", []) if a.get("urgency", "").lower() == "high")
        for v in vendors
    )

    print(f"\n📌 OPEN ACTIONS:")
    print(f"   Total Actions: {total_actions}")
    print(f"   Vendors with Actions: {vendors_with_actions} ({vendors_with_actions/total*100:.1f}%)")
    print(f"   🔴 High Urgency Actions: {high_urgency_actions}")

    # Domain analysis
    domain_scores = {}
    for v in vendors:
        for domain, score in v.get("control_scores", {}).items():
            if domain not in domain_scores:
                domain_scores[domain] = []
            domain_scores[domain].append(score)

    if domain_scores:
        print(f"\n📋 WEAKEST CONTROL DOMAINS:")
        domain_avgs = {d: sum(scores)/len(scores) for d, scores in domain_scores.items()}
        sorted_domains = sorted(domain_avgs.items(), key=lambda x: x[1])
        for domain, avg in sorted_domains[:3]:
            indicator = "❌" if avg < 3 else "⚠️"
            print(f"   {indicator} {domain}: {avg:.2f}/5")

    print("\n" + "="*70)


def _export_search_results(vendors: List[Dict[str, Any]], org_id: str) -> None:
    """
    Export search results to file

    Args:
        vendors: List of vendor records
        org_id: Organization identifier
    """
    try:
        from pathlib import Path
        import json

        safe_org = InputValidator.sanitize_filename(org_id.replace(" ", "_"))
        timestamp = utils.now_iso()

        out_dir = Path("outputs")
        out_dir.mkdir(exist_ok=True)

        filename = f"search_results_{safe_org}_{timestamp}.json"
        filepath = out_dir / filename

        # Prepare data for export
        export_data = {
            "organization": org_id,
            "timestamp": timestamp,
            "total_vendors": len(vendors),
            "vendors": vendors
        }

        filepath.write_text(json.dumps(export_data, indent=2), encoding="utf-8")
        print(f"\n✅ Search results exported to: {filepath.resolve()}")
        logger.info(f"Search results exported: {filepath}")

    except Exception as e:
        logger.error(f"Failed to export search results: {e}")
        print(f"\n❌ Error exporting results: {e}")
