import tkinter as tk
from tkinter import messagebox
import sys
import os

# ─── PATH FIX ─────────────────────────────────────────────────
# Allows ui/login.py to import from the root db.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

# ─── CONSTANTS ────────────────────────────────────────────────
BG         = "#0f0f0f"
CARD       = "#1a1a1a"
BORDER     = "#2a2a2a"
GREEN      = "#b6f36a"
RED        = "#f56a6a"
YELLOW     = "#f5d547"
TEXT       = "#e8e8e8"
MUTED      = "#555555"
FONT_MONO  = "Courier"

LIFESTYLES = ["Student", "Professional", "Small Business", "Freelancer", "Other"]


class LoginScreen(tk.Tk):
    def __init__(self, on_login):
        super().__init__()
        self.on_login = on_login  # callback — passes profile_id to main app
        self.title("Budget Tracker — Select Profile")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(bg=BG)

        db.initialize_db()
        self._build_ui()
        self._load_profiles()

    # ─── UI ───────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(24, 0))

        tk.Label(header, text="BUDGET TRACKER",
                 font=(FONT_MONO, 22, "bold"), bg=BG, fg=GREEN).pack(anchor="w")
        tk.Label(header, text="select or create a profile to continue",
                 font=(FONT_MONO, 9), bg=BG, fg=MUTED).pack(anchor="w", pady=(2, 0))

        self._divider()

        # Profile list label
        tk.Label(self, text="  YOUR PROFILES",
                 font=(FONT_MONO, 9, "bold"), bg=BG, fg=MUTED).pack(anchor="w", padx=24)

        # Scrollable profile list
        list_frame = tk.Frame(self, bg=BG)
        list_frame.pack(fill="both", expand=True, padx=24, pady=(6, 0))

        self.canvas = tk.Canvas(list_frame, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical",
                                  command=self.canvas.yview)
        self.scrollable = tk.Frame(self.canvas, bg=BG)

        self.scrollable.bind("<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._divider()

        # New profile form
        tk.Label(self, text="  CREATE NEW PROFILE",
                 font=(FONT_MONO, 9, "bold"), bg=BG, fg=MUTED).pack(anchor="w", padx=24)

        form = tk.Frame(self, bg=CARD, highlightthickness=1,
                        highlightbackground=BORDER)
        form.pack(fill="x", padx=24, pady=(6, 0))

        row = tk.Frame(form, bg=CARD)
        row.pack(fill="x", padx=12, pady=10)

        # Name field
        name_col = tk.Frame(row, bg=CARD)
        name_col.pack(side="left", expand=True, fill="x", padx=(0, 8))
        tk.Label(name_col, text="Name", font=(FONT_MONO, 8),
                 bg=CARD, fg=MUTED).pack(anchor="w")
        self.entry_name = tk.Entry(name_col, font=(FONT_MONO, 11),
                                    bg="#111", fg=TEXT, relief="flat",
                                    insertbackground=GREEN,
                                    highlightthickness=1,
                                    highlightbackground=BORDER)
        self.entry_name.pack(fill="x", ipady=5)

        # Lifestyle dropdown
        life_col = tk.Frame(row, bg=CARD)
        life_col.pack(side="left")
        tk.Label(life_col, text="Lifestyle", font=(FONT_MONO, 8),
                 bg=CARD, fg=MUTED).pack(anchor="w")

        self.lifestyle_var = tk.StringVar(value="Student")
        life_menu = tk.OptionMenu(life_col, self.lifestyle_var, *LIFESTYLES)
        life_menu.config(font=(FONT_MONO, 10), bg="#111", fg=TEXT,
                         activebackground=BORDER, activeforeground=TEXT,
                         relief="flat", highlightthickness=1,
                         highlightbackground=BORDER, bd=0)
        life_menu["menu"].config(bg="#111", fg=TEXT, font=(FONT_MONO, 10))
        life_menu.pack(ipady=3)

        # Create button
        tk.Button(form, text="+ CREATE PROFILE",
                  font=(FONT_MONO, 10, "bold"),
                  bg=GREEN, fg="#000", relief="flat", cursor="hand2",
                  activebackground="#9de050", activeforeground="#000",
                  command=self._create_profile, pady=8).pack(
                  fill="x", padx=12, pady=(0, 12))

        # Footer
        tk.Label(self, text="data stored locally on your device",
                 font=(FONT_MONO, 8), bg=BG, fg="#333").pack(pady=10)

    def _divider(self):
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=24, pady=10)

    # ─── PROFILE CARDS ────────────────────────────────────────
    def _load_profiles(self):
        # Clear existing cards
        for widget in self.scrollable.winfo_children():
            widget.destroy()

        profiles = db.get_all_profiles()

        if not profiles:
            tk.Label(self.scrollable,
                     text="No profiles yet. Create one below.",
                     font=(FONT_MONO, 10), bg=BG, fg=MUTED).pack(pady=20)
            return

        for profile in profiles:
            self._profile_card(profile)

    def _profile_card(self, profile):
        card = tk.Frame(self.scrollable, bg=CARD,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x", pady=(0, 8))

        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="x", padx=14, pady=10)

        # Left — info
        info = tk.Frame(inner, bg=CARD)
        info.pack(side="left", expand=True, fill="x")

        tk.Label(info, text=profile["name"],
                 font=(FONT_MONO, 13, "bold"), bg=CARD, fg=TEXT).pack(anchor="w")
        tk.Label(info, text=f"{profile['lifestyle']}  ·  {profile['currency']}  ·  created {profile['created_at'][:10]}",
                 font=(FONT_MONO, 8), bg=CARD, fg=MUTED).pack(anchor="w", pady=(2, 0))

        # Right — buttons
        btn_frame = tk.Frame(inner, bg=CARD)
        btn_frame.pack(side="right")

        pid = profile["id"]

        tk.Button(btn_frame, text="LOGIN →",
                  font=(FONT_MONO, 9, "bold"),
                  bg=GREEN, fg="#000", relief="flat", cursor="hand2",
                  activebackground="#9de050",
                  command=lambda p=pid: self._login(p),
                  padx=10, pady=4).pack(side="left", padx=(0, 6))

        tk.Button(btn_frame, text="🗑",
                  font=(FONT_MONO, 10),
                  bg=CARD, fg=RED, relief="flat", cursor="hand2",
                  activebackground=BORDER,
                  command=lambda p=pid, n=profile["name"]: self._delete_profile(p, n),
                  padx=6, pady=4).pack(side="left")

    # ─── ACTIONS ──────────────────────────────────────────────
    def _login(self, profile_id):
        self.destroy()
        self.on_login(profile_id)

    def _create_profile(self):
        name = self.entry_name.get().strip()
        lifestyle = self.lifestyle_var.get()

        if not name:
            messagebox.showwarning("Missing", "Please enter a profile name.")
            return
        if len(name) > 30:
            messagebox.showwarning("Too long", "Name must be 30 characters or less.")
            return

        db.create_profile(name, lifestyle=lifestyle)
        self.entry_name.delete(0, tk.END)
        self._load_profiles()

    def _delete_profile(self, profile_id, name):
        confirm = messagebox.askyesno(
            "Delete Profile",
            f"Delete '{name}'?\n\nThis will erase ALL transactions and budgets for this profile. This cannot be undone."
        )
        if confirm:
            db.delete_profile(profile_id)
            self._load_profiles()


# ─── STANDALONE TEST ──────────────────────────────────────────
if __name__ == "__main__":
    def on_login(profile_id):
        print(f"✅ Logged in as profile ID: {profile_id}")

    app = LoginScreen(on_login=on_login)
    app.mainloop()