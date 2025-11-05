"""
AI-Powered TPRM System - Main Entry Point
Production-grade third-party risk management system
"""
import importlib
import sys
from pathlib import Path

from config import Config
from modules.logger import get_logger, TPRMLogger
from modules.api_client import get_client, ConnectionError as OllamaConnectionError
from modules.validators import InputValidator, ValidationError

logger = get_logger(__name__)

def pick_model():
    """
    Allow user to select Ollama model with validation

    Returns:
        Selected model name
    """
    default_model = Config.OLLAMA_MODEL_DEFAULT
    available = Config.AVAILABLE_MODELS

    print("\n" + "="*50)
    print("Available models:")
    for idx, model in enumerate(available, 1):
        marker = " (default)" if model == default_model else ""
        print(f"  {idx}. {model}{marker}")
    print("="*50)

    try:
        chosen = input(f"\nWhich model? [Enter for default: {default_model}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\nUsing default model: {default_model}")
        logger.info(f"User selected default model: {default_model}")
        return default_model

    if chosen == "":
        logger.info(f"User selected default model: {default_model}")
        return default_model

    # Check if user entered a number (list selection)
    try:
        idx = int(chosen)
        if 1 <= idx <= len(available):
            selected = available[idx - 1]
            logger.info(f"User selected model: {selected}")
            return selected
    except ValueError:
        pass

    # Direct model name entry
    if chosen in available:
        logger.info(f"User selected model: {chosen}")
        return chosen

    print(f"⚠️  Model '{chosen}' not in configured list, but will try to use it")
    logger.warning(f"User selected unconfigured model: {chosen}")
    return chosen


def show_menu():
    """Display main menu with production formatting"""
    print("\n" + "="*60)
    print("  AI-POWERED TPRM SYSTEM - COMMAND CENTRE")
    print("="*60)
    print("\n📋 CORE OPERATIONS:")
    print("  1. Vendor Assessment Workflow")
    print("     → New assessment | Edit existing | View portfolio")
    print("     → DDQ scoring (7 weighted domains)")
    print("     → Excel / PDF / Word / PowerPoint outputs")
    print()
    print("  2. Portfolio / Management Reports")
    print("     → Organization-level or cross-org summaries")
    print()
    print("  3. Search / Filter Vendors")
    print("     → Query vendors and open actions")
    print()
    print("  4. Export Risk Register")
    print("     → Excel export per org or ALL")
    print()
    print("\n📄 DOCUMENTATION:")
    print("  5. Risk Acceptance Memo")
    print("     → Formal risk acceptance documentation")
    print()
    print("  6. Stakeholder Communications")
    print("     → Draft vendor and stakeholder letters")
    print()
    print("  7. Risk Treatment Summary")
    print("     → Board-level risk treatment reports")
    print()
    print("\n⚙️  UTILITIES:")
    print("  8. Import Vendors from Excel")
    print("     → Bulk vendor loading")
    print()
    print("  9. Continuous Monitoring (Coming Soon)")
    print("     → Automated watchlist tracking")
    print()
    print("  10. Exit")
    print("\n" + "="*60)


def main():
    """
    Main application entry point with production error handling
    """
    try:
        # Display startup banner
        print("\n" + "="*60)
        print(f"  {Config.APP_NAME}")
        print(f"  Version {Config.VERSION}")
        print("="*60)

        logger.info("="*60)
        logger.info(f"Starting {Config.APP_NAME} v{Config.VERSION}")
        logger.info("="*60)

        # Ensure directories exist
        Config.ensure_directories()
        logger.info("Initialized directory structure")

        # Verify configuration
        try:
            Config.validate_config()
            logger.info("Configuration validated successfully")
        except ValueError as e:
            logger.critical(f"Configuration error: {e}")
            print(f"\n❌ Configuration Error: {e}")
            print("Please check your .env file or config.py")
            sys.exit(1)

        # Verify Ollama connection
        print("\n🔌 Verifying connection to Ollama...")
        try:
            client = get_client()
            client.verify_connection()
            print("✅ Connected to Ollama successfully")
        except OllamaConnectionError as e:
            logger.error(f"Ollama connection failed: {e}")
            print(f"\n❌ Cannot connect to Ollama:")
            print(f"   {e}")
            print("\n💡 Troubleshooting:")
            print("   1. Ensure Ollama is running: ollama serve")
            print(f"   2. Check URL in .env: {Config.OLLAMA_URL}")
            print("   3. Test connection: curl http://localhost:11434/api/tags")
            sys.exit(1)

        # Model selection
        model_name = pick_model()

        # Main application loop
        while True:
            show_menu()

            try:
                choice = input("\n👉 Select option (1-10): ").strip()
            except EOFError:
                print("\n\nEOF received. Exiting cleanly.")
                logger.info("Application exit (EOF)")
                break
            except KeyboardInterrupt:
                print("\n\nInterrupted. Exiting cleanly.")
                logger.info("Application exit (Keyboard Interrupt)")
                break

            # Validate menu choice
            try:
                choice = InputValidator.validate_menu_choice(
                    choice,
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
                )
            except ValidationError:
                print("❌ Invalid selection. Please choose 1-10.")
                continue

            # Log user action
            TPRMLogger.log_user_action(logger, f"menu_selection", {"choice": choice})

            # Execute menu option
            if choice == "1":
                try:
                    mod = importlib.import_module("modules.tprm_ddq")
                    mod.run(model_name)
                except Exception as e:
                    logger.error(f"Error in assessment workflow: {e}", exc_info=True)
                    print(f"\n❌ Error in assessment workflow: {e}")
                    print("Check logs/tprm_system.log for details")

            elif choice == "2":
                try:
                    mod = importlib.import_module("modules.reports")
                    mod.run(model_name)
                except Exception as e:
                    logger.error(f"Error in portfolio report: {e}", exc_info=True)
                    print(f"\n❌ Error in portfolio/management report: {e}")
                    print("Check logs/tprm_system.log for details")

            elif choice == "3":
                try:
                    mod = importlib.import_module("modules.search")
                    mod.run(model_name)
                except Exception as e:
                    logger.error(f"Error in vendor search: {e}", exc_info=True)
                    print(f"\n❌ Error in vendor search/filter: {e}")
                    print("Check logs/tprm_system.log for details")

            elif choice == "4":
                try:
                    mod = importlib.import_module("modules.register")
                    mod.run()
                except Exception as e:
                    logger.error(f"Error exporting risk register: {e}", exc_info=True)
                    print(f"\n❌ Error exporting risk register: {e}")
                    print("Check logs/tprm_system.log for details")

            elif choice == "5":
                try:
                    mod = importlib.import_module("modules.acceptances")
                    mod.run(model_name)
                except Exception as e:
                    logger.error(f"Error generating risk acceptance: {e}", exc_info=True)
                    print(f"\n❌ Error generating risk acceptance memo: {e}")
                    print("Check logs/tprm_system.log for details")

            elif choice == "6":
                try:
                    mod = importlib.import_module("modules.comms")
                    mod.run(model_name)
                except Exception as e:
                    logger.error(f"Error drafting communication: {e}", exc_info=True)
                    print(f"\n❌ Error drafting communication: {e}")
                    print("Check logs/tprm_system.log for details")

            elif choice == "7":
                try:
                    mod = importlib.import_module("modules.risk_treatment")
                    mod.run(model_name)
                except Exception as e:
                    logger.error(f"Error generating risk treatment: {e}", exc_info=True)
                    print(f"\n❌ Error generating risk treatment summary: {e}")
                    print("Check logs/tprm_system.log for details")

            elif choice == "8":
                try:
                    mod = importlib.import_module("modules.importer")
                    mod.run()
                except Exception as e:
                    logger.error(f"Error importing vendors: {e}", exc_info=True)
                    print(f"\n❌ Error importing vendors from Excel: {e}")
                    print("Check logs/tprm_system.log for details")

            elif choice == "9":
                print("\n⚙️  Continuous monitoring / watchlist module coming soon.")
                logger.info("User accessed unimplemented feature: continuous monitoring")

            elif choice == "10":
                print("\n👋 Thank you for using the TPRM System. Goodbye!")
                logger.info("Application exit (user request)")
                break

    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted. Goodbye!")
        logger.info("Application interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.critical(f"Unexpected error in main: {e}", exc_info=True)
        print(f"\n❌ CRITICAL ERROR: {e}")
        print("Check logs/tprm_system.log for full details")
        sys.exit(1)


if __name__ == "__main__":
    main()
