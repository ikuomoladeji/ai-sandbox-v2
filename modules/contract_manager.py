"""
Contract Lifecycle Management Module
Manages vendor contracts, renewals, SLAs, and spend tracking
"""
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from modules.logger import get_logger, TPRMLogger
from modules.validators import InputValidator, ValidationError
from modules import utils

logger = get_logger(__name__)


def add_contract_to_vendor(vendor_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interactive function to add contract details to a vendor record

    Args:
        vendor_record: Existing vendor record

    Returns:
        Updated vendor record with contract information
    """
    print("\n" + "="*70)
    print("  CONTRACT LIFECYCLE MANAGEMENT")
    print("="*70)

    contract = {}

    # Contract dates
    print("\n📅 CONTRACT DATES:")
    start_date = input("Contract start date (YYYY-MM-DD) [Enter to skip]: ").strip()
    if start_date:
        try:
            datetime.datetime.strptime(start_date, "%Y-%m-%d")
            contract["start_date"] = start_date
        except ValueError:
            print("⚠️  Invalid date format, skipping")

    end_date = input("Contract end date (YYYY-MM-DD) [Enter to skip]: ").strip()
    if end_date:
        try:
            datetime.datetime.strptime(end_date, "%Y-%m-%d")
            contract["end_date"] = end_date
        except ValueError:
            print("⚠️  Invalid date format, skipping")

    # Calculate renewal date (typically 60-90 days before end)
    if end_date:
        try:
            end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            notice_days = input("Notice period in days (default 90): ").strip()
            notice_days = int(notice_days) if notice_days else 90
            contract["notice_period_days"] = notice_days

            renewal_dt = end_dt - datetime.timedelta(days=notice_days)
            contract["renewal_date"] = renewal_dt.strftime("%Y-%m-%d")

            # Calculate days until renewal
            today = datetime.datetime.now()
            days_until_renewal = (renewal_dt - today).days
            contract["days_until_renewal"] = days_until_renewal

            if days_until_renewal < 0:
                print(f"⚠️  WARNING: Renewal date passed {abs(days_until_renewal)} days ago!")
            elif days_until_renewal < 30:
                print(f"🔴 URGENT: Renewal due in {days_until_renewal} days")
            elif days_until_renewal < 90:
                print(f"🟡 Renewal due in {days_until_renewal} days")

        except Exception as e:
            logger.warning(f"Error calculating renewal date: {e}")

    # Auto-renewal
    auto_renewal = input("Auto-renewal? (y/n) [default: n]: ").strip().lower()
    contract["auto_renewal"] = auto_renewal == "y"

    # Financial details
    print("\n💰 FINANCIAL DETAILS:")
    contract_value = input("Annual contract value [Enter to skip]: ").strip()
    if contract_value:
        try:
            contract["contract_value_annual"] = float(contract_value)
            currency = input("Currency (default USD): ").strip() or "USD"
            contract["currency"] = currency.upper()
        except ValueError:
            print("⚠️  Invalid value, skipping")

    payment_terms = input("Payment terms (e.g., Net 30, Net 60): ").strip()
    if payment_terms:
        contract["payment_terms"] = payment_terms

    # SLA details
    print("\n📊 SLA DETAILS:")
    sla_response = input("SLA response time (e.g., 4 hours, 1 business day): ").strip()
    if sla_response:
        contract["sla_response_time"] = sla_response

    sla_uptime = input("SLA uptime guarantee (e.g., 99.9%, 99.99%): ").strip()
    if sla_uptime:
        contract["sla_uptime"] = sla_uptime

    sla_resolution = input("SLA resolution time (e.g., 24 hours, 3 business days): ").strip()
    if sla_resolution:
        contract["sla_resolution_time"] = sla_resolution

    # Contract ownership
    print("\n👤 OWNERSHIP:")
    contract_owner = input("Contract owner/manager (name or department): ").strip()
    if contract_owner:
        contract["contract_owner"] = contract_owner

    procurement_contact = input("Procurement contact: ").strip()
    if procurement_contact:
        contract["procurement_contact"] = procurement_contact

    # Document reference
    print("\n📄 DOCUMENTATION:")
    doc_path = input("Contract document path/reference [Enter to skip]: ").strip()
    if doc_path:
        contract["contract_document_path"] = doc_path

    # Additional terms
    termination_clause = input("Termination for convenience? (y/n) [Enter to skip]: ").strip().lower()
    if termination_clause:
        contract["termination_for_convenience"] = termination_clause == "y"

    # Add metadata
    contract["created_at"] = datetime.datetime.now().isoformat()
    contract["last_updated"] = datetime.datetime.now().isoformat()

    # Update vendor record
    vendor_record["contract"] = contract

    logger.info(f"Added contract details to vendor: {vendor_record.get('vendor_name')}")

    return vendor_record


def get_expiring_contracts(db: Dict[str, Any], days_threshold: int = 90) -> List[Dict[str, Any]]:
    """
    Get list of contracts expiring within the threshold

    Args:
        db: Vendor database
        days_threshold: Number of days to look ahead

    Returns:
        List of vendor records with expiring contracts
    """
    expiring = []
    today = datetime.datetime.now()

    for org_id, vendors in db.items():
        for vendor_name, vendor_record in vendors.items():
            contract = vendor_record.get("contract", {})

            if not contract or "end_date" not in contract:
                continue

            try:
                end_date = datetime.datetime.strptime(contract["end_date"], "%Y-%m-%d")
                days_until_expiry = (end_date - today).days

                if 0 <= days_until_expiry <= days_threshold:
                    expiring.append({
                        "org_id": org_id,
                        "vendor_name": vendor_name,
                        "end_date": contract["end_date"],
                        "days_until_expiry": days_until_expiry,
                        "contract_value": contract.get("contract_value_annual", "N/A"),
                        "auto_renewal": contract.get("auto_renewal", False)
                    })
            except Exception as e:
                logger.warning(f"Error processing contract for {vendor_name}: {e}")

    return sorted(expiring, key=lambda x: x["days_until_expiry"])


def check_sla_compliance(vendor_record: Dict[str, Any], incident_data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Check if vendor is meeting SLA commitments

    Args:
        vendor_record: Vendor record with contract SLAs
        incident_data: Optional incident data to check against SLAs

    Returns:
        SLA compliance report
    """
    contract = vendor_record.get("contract", {})

    if not contract:
        return {"status": "no_sla_defined", "message": "No SLA defined in contract"}

    # This is a placeholder - in production, integrate with incident/ticket system
    return {
        "status": "compliant",  # compliant, at_risk, breach
        "sla_uptime": contract.get("sla_uptime"),
        "sla_response_time": contract.get("sla_response_time"),
        "sla_resolution_time": contract.get("sla_resolution_time"),
        "last_checked": datetime.datetime.now().isoformat(),
        "message": "Manual SLA tracking - integrate with monitoring system"
    }


def run():
    """
    Main contract management workflow
    """
    try:
        print("\n" + "="*70)
        print("  CONTRACT LIFECYCLE MANAGEMENT")
        print("="*70)

        logger.info("Starting contract management module")
        TPRMLogger.log_user_action(logger, "contract_management_start")

        # Load database
        db = utils.load_vendor_db()

        if not db:
            print("\n⚠️  No vendors found. Please assess vendors first.")
            return

        # Show menu
        print("\n📋 CONTRACT MANAGEMENT OPTIONS:")
        print("-" * 70)
        print("  1. Add/update contract for a vendor")
        print("  2. View expiring contracts (next 90 days)")
        print("  3. View all contracts")
        print("  4. Check SLA compliance")
        print("  5. Export contract register")
        print("-" * 70)

        try:
            choice = input("\n👉 Choose option (1-5): ").strip()
            choice = InputValidator.validate_menu_choice(choice, ["1","2","3","4","5"])
        except ValidationError:
            print("❌ Invalid choice")
            return

        if choice == "1":
            # Add/update contract
            org_id = input("\n👉 Organization name: ").strip()
            if org_id not in db:
                print(f"❌ Organization '{org_id}' not found")
                return

            vendor_name = input("👉 Vendor name: ").strip()
            if vendor_name not in db[org_id]:
                print(f"❌ Vendor '{vendor_name}' not found")
                return

            vendor_record = db[org_id][vendor_name]
            updated_record = add_contract_to_vendor(vendor_record)

            # Save
            db[org_id][vendor_name] = updated_record
            utils.save_vendor_db(db)
            utils.snapshot_history(org_id, vendor_name, updated_record)

            print("\n✅ Contract details saved successfully")
            logger.info(f"Contract updated for {org_id}/{vendor_name}")

        elif choice == "2":
            # View expiring contracts
            days = input("\n👉 Show contracts expiring in next X days (default 90): ").strip()
            days_threshold = int(days) if days else 90

            expiring = get_expiring_contracts(db, days_threshold)

            if not expiring:
                print(f"\n✅ No contracts expiring in the next {days_threshold} days")
            else:
                print(f"\n⚠️  {len(expiring)} CONTRACT(S) EXPIRING IN NEXT {days_threshold} DAYS:")
                print("="*70)

                for contract in expiring:
                    urgency = "🔴" if contract["days_until_expiry"] < 30 else "🟡"
                    auto = " (AUTO-RENEW)" if contract["auto_renewal"] else ""

                    print(f"\n{urgency} {contract['vendor_name']} ({contract['org_id']}){auto}")
                    print(f"   End Date: {contract['end_date']}")
                    print(f"   Days Until Expiry: {contract['days_until_expiry']}")
                    print(f"   Contract Value: {contract['contract_value']}")

        elif choice == "3":
            # View all contracts
            total_contracts = 0
            total_value = 0

            print("\n📊 ALL VENDOR CONTRACTS:")
            print("="*70)

            for org_id, vendors in db.items():
                org_contracts = 0

                for vendor_name, vendor_record in vendors.items():
                    contract = vendor_record.get("contract")

                    if contract:
                        org_contracts += 1
                        total_contracts += 1

                        value = contract.get("contract_value_annual", 0)
                        if value:
                            total_value += value

                        print(f"\n🏢 {vendor_name} ({org_id})")
                        print(f"   Start: {contract.get('start_date', 'N/A')}")
                        print(f"   End: {contract.get('end_date', 'N/A')}")
                        print(f"   Value: {contract.get('contract_value_annual', 'N/A')} {contract.get('currency', '')}")
                        print(f"   Owner: {contract.get('contract_owner', 'N/A')}")

            print("\n" + "="*70)
            print(f"📊 SUMMARY:")
            print(f"   Total Contracts: {total_contracts}")
            print(f"   Total Annual Value: ${total_value:,.2f}" if total_value else "   Total Annual Value: N/A")

        elif choice == "4":
            # Check SLA compliance
            org_id = input("\n👉 Organization name: ").strip()
            vendor_name = input("👉 Vendor name: ").strip()

            if org_id not in db or vendor_name not in db[org_id]:
                print("❌ Vendor not found")
                return

            vendor_record = db[org_id][vendor_name]
            sla_report = check_sla_compliance(vendor_record)

            print(f"\n📊 SLA COMPLIANCE REPORT: {vendor_name}")
            print("="*70)
            print(f"Status: {sla_report['status']}")
            print(f"Uptime SLA: {sla_report.get('sla_uptime', 'Not defined')}")
            print(f"Response Time SLA: {sla_report.get('sla_response_time', 'Not defined')}")
            print(f"Resolution Time SLA: {sla_report.get('sla_resolution_time', 'Not defined')}")
            print(f"\n{sla_report['message']}")

        elif choice == "5":
            # Export contract register
            from openpyxl import Workbook

            wb = Workbook()
            ws = wb.active
            ws.title = "Contract Register"

            # Headers
            ws.append([
                "Organization",
                "Vendor",
                "Start Date",
                "End Date",
                "Renewal Date",
                "Days Until Renewal",
                "Auto-Renewal",
                "Annual Value",
                "Currency",
                "Notice Period (Days)",
                "SLA Uptime",
                "SLA Response Time",
                "Contract Owner",
                "Payment Terms"
            ])

            # Data
            for org_id, vendors in db.items():
                for vendor_name, vendor_record in vendors.items():
                    contract = vendor_record.get("contract", {})

                    if contract:
                        ws.append([
                            org_id,
                            vendor_name,
                            contract.get("start_date", ""),
                            contract.get("end_date", ""),
                            contract.get("renewal_date", ""),
                            contract.get("days_until_renewal", ""),
                            "Yes" if contract.get("auto_renewal") else "No",
                            contract.get("contract_value_annual", ""),
                            contract.get("currency", ""),
                            contract.get("notice_period_days", ""),
                            contract.get("sla_uptime", ""),
                            contract.get("sla_response_time", ""),
                            contract.get("contract_owner", ""),
                            contract.get("payment_terms", "")
                        ])

            # Save
            out_dir = Path("outputs")
            out_dir.mkdir(exist_ok=True)

            ts = utils.today_short()
            filename = f"contract_register_{ts}.xlsx"
            filepath = out_dir / filename

            wb.save(filepath)
            print(f"\n✅ Contract register exported to: {filepath.resolve()}")
            logger.info(f"Contract register exported: {filepath}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled")
    except Exception as e:
        logger.error(f"Error in contract management: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Check logs for details")


if __name__ == "__main__":
    run()
