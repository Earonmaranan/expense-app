import sys
import os

# ─── PATH SETUP ───────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import db
from ui.login import LoginScreen
from ui.dashboard import Dashboard


def launch_dashboard(profile_id):
    """Called by LoginScreen after user selects a profile."""
    app = Dashboard(profile_id=profile_id)
    app.mainloop()


def main():
    db.initialize_db()

    login = LoginScreen(on_login=launch_dashboard)
    login.mainloop()


if __name__ == "__main__":
    main()