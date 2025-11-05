"""
Dashboard Launcher Module
Launches the Streamlit dashboard in a separate process
"""
import subprocess
import sys
from pathlib import Path
from modules.logger import get_logger

logger = get_logger(__name__)


def run():
    """
    Launch the Streamlit dashboard in a separate process
    """
    print("\n" + "="*60)
    print("  📊 LAUNCHING TPRM DASHBOARD")
    print("="*60)

    dashboard_path = Path(__file__).parent.parent / "dashboard.py"

    if not dashboard_path.exists():
        print(f"\n❌ Dashboard file not found: {dashboard_path}")
        logger.error(f"Dashboard file not found: {dashboard_path}")
        return

    print("\n🚀 Starting Streamlit dashboard...")
    print("   The dashboard will open in your default web browser")
    print("   Press Ctrl+C to stop the dashboard server\n")

    logger.info("Launching Streamlit dashboard")

    try:
        # Launch Streamlit
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(dashboard_path)],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error launching dashboard: {e}")
        logger.error(f"Failed to launch dashboard: {e}")
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped by user")
        logger.info("Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error launching dashboard: {e}", exc_info=True)


if __name__ == "__main__":
    run()
