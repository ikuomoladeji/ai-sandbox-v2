import importlib
from pathlib import Path

AVAILABLE_MODELS = [
    "llama3:latest",
    "mistral:latest",
    "qwen3-coder:30b (heavy)",
]

def pick_model():
    default_model = "llama3:latest"
    print("Available models:", ", ".join(AVAILABLE_MODELS))
    try:
        chosen = input(f"Which model do you want to use? [{default_model}]: ").strip()
    except EOFError:
        print("\nEOF received, using default model:", default_model)
        return default_model
    except KeyboardInterrupt:
        print("\nInterrupted, using default model:", default_model)
        return default_model
    if chosen == "":
        return default_model
    return chosen


def show_menu():
    print("\nAI Risk Assistant – Command Centre")
    print("----------------------------------")
    print("1. Vendor assessment workflow")
    print("   – New vendor OR edit existing vendor OR view org vendors")
    print("   – DDQ scoring (1–5 weighted)")
    print("   – Save/update vendor record")
    print("   – Optional: generate Excel / narrative / board packs")
    print()
    print("2. Generate portfolio / management report (per org or ALL)")
    print("3. Search / filter vendors / open actions")
    print("4. Export Risk Register (Excel, per org or ALL)")
    print("5. Generate Risk Acceptance memo (link to vendor)")
    print("6. Draft Vendor / Stakeholder Communication")
    print("7. Generate Risk Treatment & Management Summary (board pack)")
    print("8. Import vendors from Excel (bulk load)")
    print("9. (Future) Continuous monitoring / watchlist")
    print("10. Exit\n")


def main():
    # ensure dirs so modules don't explode
    Path("outputs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    Path("history").mkdir(exist_ok=True)

    model_name = pick_model()

    while True:
        show_menu()
        try:
            choice = input("Select an option (1–10): ").strip()
        except EOFError:
            print("\nEOF received. Exiting cleanly.")
            break
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting cleanly.")
            break

        if choice == "1":
            try:
                mod = importlib.import_module("modules.tprm_ddq")
                mod.run(model_name)
            except Exception as e:
                print(f"[!] Error in assessment workflow: {e}")

        elif choice == "2":
            try:
                mod = importlib.import_module("modules.reports")
                mod.run(model_name)
            except Exception as e:
                print(f"[!] Error in portfolio/management report: {e}")

        elif choice == "3":
            try:
                mod = importlib.import_module("modules.search")
                mod.run(model_name)
            except Exception as e:
                print(f"[!] Error in vendor search/filter: {e}")

        elif choice == "4":
            try:
                mod = importlib.import_module("modules.register")
                mod.run()
            except Exception as e:
                print(f"[!] Error exporting risk register: {e}")

        elif choice == "5":
            try:
                mod = importlib.import_module("modules.acceptances")
                mod.run(model_name)
            except Exception as e:
                print(f"[!] Error generating risk acceptance memo: {e}")

        elif choice == "6":
            try:
                mod = importlib.import_module("modules.comms")
                mod.run(model_name)
            except Exception as e:
                print(f"[!] Error drafting communication: {e}")

        elif choice == "7":
            try:
                mod = importlib.import_module("modules.risk_treatment")
                mod.run(model_name)
            except Exception as e:
                print(f"[!] Error generating risk treatment summary: {e}")

        elif choice == "8":
            try:
                mod = importlib.import_module("modules.importer")
                mod.run()
            except Exception as e:
                print(f"[!] Error importing vendors from Excel: {e}")

        elif choice == "9":
            print("⚙️ Continuous monitoring / watchlist module coming soon.")

        elif choice == "10":
            print("Goodbye.")
            break

        else:
            print("Invalid selection. Choose 1–10.")


if __name__ == "__main__":
    main()
