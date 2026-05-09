import tkinter as tk
from tkinter import messagebox
import sys
import os
from datetime import datetime

# ─── PATH FIX ─────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

# ─── CONSTANTS ────────────────────────────────────────────────
BG       = "#0f0f0f"
CARD     = "#1a1a1a"
BORDER   = "#2a2a2a"
GREEN    = "#b6f36a"
YELLOW   = "#f5d547"
ORANGE   = "#f59547"
RED      = "#f56a6a"
TEXT     = "#e8e8e8"
MUTED    = "#555555"
FONT     = "Courier"


def _get_bar_color(percent):
    """Returns color based on how close to the budget limit."""
    if percent >= 100:
        return RED
    elif percent >= 80:
        return ORANGE
    elif percent >= 50:
        return YELLOW
    return GREEN


class BudgetsScreen(tk.Toplevel):
    def __init__(self, parent, profile_id, currency):
        super().__init__(parent)
        self.profile_id = profile_id
        self.currency   = currency
        self.month      = datetime.now().strftime("%Y-%m")

        self.title("Budget Limits")
        self.geometry("520x620")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()  # modal

        self._build_ui()
        self.refresh()

    # ─── UI ───────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 0))

        tk.Label(header, text="BUDGET LIMITS",
                 font=(FONT, 18, "bold"), bg=BG, fg=GREEN).pack(anchor="w")
        tk.Label(header, text="set monthly spending limits per category",
                 font=(FONT, 9), bg=BG, fg=MUTED).pack(anchor="w", pady=(2, 0))

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=24, pady=12)

        # Month label
        dt = datetime.strptime(self.month, "%Y-%m")
        tk.Label(self, text=dt.strftime("%B %Y").upper(),
                 font=(FONT, 9, "bold"), bg=BG, fg=MUTED).pack(
                 anchor="w", padx=24)

        # Scrollable budget list
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=24, pady=(8, 0))

        canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical",
                                  command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=BG)

        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=24, pady=12)

        # Set budget form
        tk.Label(self, text="SET / UPDATE A BUDGET",
                 font=(FONT, 9, "bold"), bg=BG, fg=MUTED).pack(
                 anchor="w", padx=24)

        form = tk.Frame(self, bg=CARD, highlightthickness=1,
                        highlightbackground=BORDER)
        form.pack(fill="x", padx=24, pady=(6, 0))

        row = tk.Frame(form, bg=CARD)
        row.pack(fill="x", padx=12, pady=12)

        # Category picker
        col1 = tk.Frame(row, bg=CARD)
        col1.pack(side="left", expand=True, fill="x", padx=(0, 8))
        tk.Label(col1, text="Category", font=(FONT, 8),
                 bg=CARD, fg=MUTED).pack(anchor="w")
        self.cat_var = tk.StringVar()
        self.cat_menu = tk.OptionMenu(col1, self.cat_var, "")
        self.cat_menu.config(font=(FONT, 10), bg="#111", fg=TEXT,
                              activebackground=BORDER, relief="flat",
                              highlightthickness=1, highlightbackground=BORDER,
                              bd=0, anchor="w", width=16)
        self.cat_menu["menu"].config(bg="#111", fg=TEXT, font=(FONT, 10))
        self.cat_menu.pack(fill="x", ipady=3)

        # Amount
        col2 = tk.Frame(row, bg=CARD)
        col2.pack(side="left", padx=(0, 8))
        tk.Label(col2, text=f"Limit ({self.currency})",
                 font=(FONT, 8), bg=CARD, fg=MUTED).pack(anchor="w")
        self.entry_amount = tk.Entry(col2, font=(FONT, 11), width=10,
                                      bg="#111", fg=YELLOW, relief="flat",
                                      insertbackground=GREEN,
                                      highlightthickness=1,
                                      highlightbackground=BORDER)
        self.entry_amount.pack(ipady=5)

        tk.Button(form, text="💾  SAVE BUDGET",
                  font=(FONT, 10, "bold"),
                  bg=GREEN, fg="#000", relief="flat", cursor="hand2",
                  activebackground="#9de050",
                  command=self._save_budget,
                  pady=8).pack(fill="x", padx=12, pady=(0, 12))

        # Footer note
        tk.Label(self,
                 text="⚠  alerts fire at 80% and 100% of your limit",
                 font=(FONT, 8), bg=BG, fg=MUTED).pack(pady=8)

    # ─── REFRESH ──────────────────────────────────────────────
    def refresh(self):
        self._refresh_category_menu()
        self._refresh_budget_list()

    def _refresh_category_menu(self):
        cats = db.get_categories(self.profile_id)
        self._cat_map = {f"{c['icon']} {c['name']}": c["id"] for c in cats}

        menu = self.cat_menu["menu"]
        menu.delete(0, "end")

        if not cats:
            self.cat_var.set("— no categories —")
        else:
            for label in self._cat_map:
                menu.add_command(label=label,
                                  command=lambda l=label: self.cat_var.set(l))
            self.cat_var.set(list(self._cat_map.keys())[0])

    def _refresh_budget_list(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        cats    = db.get_categories(self.profile_id)
        budgets = {b["category_id"]: b for b in db.get_budgets(self.profile_id)}
        spending = {
            row["name"]: row["total"]
            for row in db.get_spending_by_category(self.profile_id, self.month)
        }

        if not cats:
            tk.Label(self.scroll_frame,
                     text="No categories yet.\nGo to Dashboard → Manage Categories.",
                     font=(FONT, 10), bg=BG, fg=MUTED,
                     justify="left").pack(pady=20)
            return

        over_budget = []

        for cat in cats:
            spent  = spending.get(cat["name"], 0)
            budget = budgets.get(cat["id"])
            limit  = budget["amount"] if budget else None

            self._budget_card(cat, spent, limit)

            if limit and spent >= limit:
                over_budget.append(cat["name"])

        # Fire alerts for over-budget categories
        if over_budget:
            names = ", ".join(over_budget)
            messagebox.showwarning(
                "Over Budget! 🚨",
                f"You've exceeded your budget for:\n\n{names}\n\nConsider adjusting your spending."
            )

    def _budget_card(self, cat, spent, limit):
        card = tk.Frame(self.scroll_frame, bg=CARD,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x", pady=(0, 10))

        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="x", padx=14, pady=10)

        # Top row — category name + spent/limit
        top = tk.Frame(inner, bg=CARD)
        top.pack(fill="x")

        tk.Label(top, text=f"{cat['icon']}  {cat['name']}",
                 font=(FONT, 11, "bold"), bg=CARD, fg=TEXT).pack(side="left")

        if limit:
            percent = min((spent / limit) * 100, 100)
            color   = _get_bar_color(percent)
            tk.Label(top,
                     text=f"{self.currency}{spent:,.2f} / {self.currency}{limit:,.2f}",
                     font=(FONT, 9), bg=CARD, fg=color).pack(side="right")
        else:
            percent = 0
            tk.Label(top, text=f"{self.currency}{spent:,.2f}  (no limit set)",
                     font=(FONT, 9), bg=CARD, fg=MUTED).pack(side="right")

        # Progress bar
        if limit:
            bar_bg = tk.Frame(inner, bg=BORDER, height=6)
            bar_bg.pack(fill="x", pady=(6, 2))
            bar_bg.pack_propagate(False)

            bar_color = _get_bar_color(percent)
            bar_fill  = tk.Frame(bar_bg, bg=bar_color, height=6)
            bar_fill.place(relwidth=min(percent / 100, 1.0), relheight=1.0)

            # Status label
            if percent >= 100:
                status = "🚨 OVER BUDGET"
                sc     = RED
            elif percent >= 80:
                status = f"⚠  {percent:.0f}% used — watch out"
                sc     = ORANGE
            elif percent >= 50:
                status = f"📊 {percent:.0f}% used"
                sc     = YELLOW
            else:
                status = f"✅ {percent:.0f}% used"
                sc     = GREEN

            tk.Label(inner, text=status, font=(FONT, 8),
                     bg=CARD, fg=sc).pack(anchor="w", pady=(2, 0))
        else:
            tk.Label(inner, text="— set a limit below to track this category",
                     font=(FONT, 8), bg=CARD, fg=MUTED).pack(
                     anchor="w", pady=(4, 0))

    # ─── ACTIONS ──────────────────────────────────────────────
    def _save_budget(self):
        cat_label = self.cat_var.get()
        amount    = self.entry_amount.get().strip()

        if cat_label not in self._cat_map:
            messagebox.showwarning("No Category",
                "Please create categories first in the Dashboard.")
            return
        try:
            amount_f = float(amount)
            if amount_f <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid", "Enter a valid limit greater than 0.")
            return

        cat_id = self._cat_map[cat_label]
        db.set_budget(self.profile_id, cat_id, amount_f)

        self.entry_amount.delete(0, tk.END)
        self.refresh()


# ─── STANDALONE TEST ──────────────────────────────────────────
if __name__ == "__main__":
    db.initialize_db()
    profiles = db.get_all_profiles()
    if not profiles:
        print("⚠️  No profiles found. Run db.py first.")
    else:
        root = tk.Tk()
        root.withdraw()  # hide root window
        p = profiles[0]
        app = BudgetsScreen(root, profile_id=p["id"], currency=p["currency"])
        root.mainloop()