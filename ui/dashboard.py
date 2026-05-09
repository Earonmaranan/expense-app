import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

# ─── PATH FIX ─────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

# ─── CONSTANTS ────────────────────────────────────────────────
BG        = "#0f0f0f"
CARD      = "#1a1a1a"
CARD2     = "#161616"
BORDER    = "#2a2a2a"
GREEN     = "#b6f36a"
RED       = "#f56a6a"
YELLOW    = "#f5d547"
BLUE      = "#6ab4f3"
TEXT      = "#e8e8e8"
MUTED     = "#555555"
FONT      = "Courier"


class Dashboard(tk.Tk):
    def __init__(self, profile_id):
        super().__init__()
        self.profile_id = profile_id
        self.profile    = db.get_profile(profile_id)
        self.currency   = self.profile["currency"]
        self.month      = datetime.now().strftime("%Y-%m")  # e.g. '2026-05'

        self.title(f"Budget Tracker — {self.profile['name']}")
        self.geometry("680x700")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._build_topbar()
        self._build_summary()
        self._build_form()
        self._build_transaction_list()
        self._build_statusbar()

        self.refresh()

    # ─── TOP BAR ──────────────────────────────────────────────
    def _build_topbar(self):
        bar = tk.Frame(self, bg=CARD, highlightthickness=1,
                       highlightbackground=BORDER)
        bar.pack(fill="x")

        inner = tk.Frame(bar, bg=CARD)
        inner.pack(fill="x", padx=20, pady=10)

        # Left — profile info
        left = tk.Frame(inner, bg=CARD)
        left.pack(side="left")

        tk.Label(left, text=self.profile["name"].upper(),
                 font=(FONT, 14, "bold"), bg=CARD, fg=GREEN).pack(anchor="w")
        tk.Label(left, text=f"{self.profile['lifestyle']}  ·  {self._month_label()}",
                 font=(FONT, 8), bg=CARD, fg=MUTED).pack(anchor="w")

        # Right — month nav
        right = tk.Frame(inner, bg=CARD)
        right.pack(side="right")

        tk.Button(right, text="◀", font=(FONT, 10),
                  bg=CARD, fg=TEXT, relief="flat", cursor="hand2",
                  activebackground=BORDER,
                  command=self._prev_month).pack(side="left", padx=(0, 6))

        self.lbl_month = tk.Label(right, text=self._month_label(),
                                   font=(FONT, 10, "bold"), bg=CARD, fg=TEXT)
        self.lbl_month.pack(side="left")

        tk.Button(right, text="▶", font=(FONT, 10),
                  bg=CARD, fg=TEXT, relief="flat", cursor="hand2",
                  activebackground=BORDER,
                  command=self._next_month).pack(side="left", padx=(6, 0))

    # ─── SUMMARY CARDS ────────────────────────────────────────
    def _build_summary(self):
        self.summary_frame = tk.Frame(self, bg=BG)
        self.summary_frame.pack(fill="x", padx=20, pady=(14, 0))

        self.lbl_income  = self._card(self.summary_frame, "INCOME",  "0.00", GREEN)
        self.lbl_expense = self._card(self.summary_frame, "SPENT",   "0.00", RED)
        self.lbl_balance = self._card(self.summary_frame, "BALANCE", "0.00", YELLOW)

    def _card(self, parent, title, value, color):
        frame = tk.Frame(parent, bg=CARD, highlightthickness=1,
                         highlightbackground=BORDER)
        frame.pack(side="left", expand=True, fill="both",
                   padx=(0, 8), pady=4, ipady=10)
        tk.Label(frame, text=title, font=(FONT, 8),
                 bg=CARD, fg=MUTED).pack()
        lbl = tk.Label(frame, text=f"{self.currency}{value}",
                       font=(FONT, 15, "bold"), bg=CARD, fg=color)
        lbl.pack()
        return lbl

    # ─── ADD TRANSACTION FORM ─────────────────────────────────
    def _build_form(self):
        form = tk.Frame(self, bg=CARD, highlightthickness=1,
                        highlightbackground=BORDER)
        form.pack(fill="x", padx=20, pady=(14, 0))

        tk.Label(form, text="  ADD TRANSACTION",
                 font=(FONT, 9, "bold"), bg=CARD, fg=MUTED).pack(
                 anchor="w", padx=10, pady=(8, 4))

        row1 = tk.Frame(form, bg=CARD)
        row1.pack(fill="x", padx=10, pady=(0, 4))

        # Description
        col1 = tk.Frame(row1, bg=CARD)
        col1.pack(side="left", expand=True, fill="x", padx=(0, 8))
        tk.Label(col1, text="Description", font=(FONT, 8),
                 bg=CARD, fg=MUTED).pack(anchor="w")
        self.entry_desc = tk.Entry(col1, font=(FONT, 11),
                                    bg="#111", fg=TEXT, relief="flat",
                                    insertbackground=GREEN,
                                    highlightthickness=1,
                                    highlightbackground=BORDER)
        self.entry_desc.pack(fill="x", ipady=5)

        # Amount
        col2 = tk.Frame(row1, bg=CARD)
        col2.pack(side="left", padx=(0, 8))
        tk.Label(col2, text=f"Amount ({self.currency})",
                 font=(FONT, 8), bg=CARD, fg=MUTED).pack(anchor="w")
        self.entry_amount = tk.Entry(col2, font=(FONT, 11), width=10,
                                      bg="#111", fg=YELLOW, relief="flat",
                                      insertbackground=GREEN,
                                      highlightthickness=1,
                                      highlightbackground=BORDER)
        self.entry_amount.pack(ipady=5)

        row2 = tk.Frame(form, bg=CARD)
        row2.pack(fill="x", padx=10, pady=(0, 4))

        # Category
        col3 = tk.Frame(row2, bg=CARD)
        col3.pack(side="left", expand=True, fill="x", padx=(0, 8))
        tk.Label(col3, text="Category", font=(FONT, 8),
                 bg=CARD, fg=MUTED).pack(anchor="w")
        self.cat_var = tk.StringVar()
        self.cat_menu = tk.OptionMenu(col3, self.cat_var, "")
        self.cat_menu.config(font=(FONT, 10), bg="#111", fg=TEXT,
                              activebackground=BORDER, relief="flat",
                              highlightthickness=1, highlightbackground=BORDER,
                              bd=0, anchor="w", width=18)
        self.cat_menu["menu"].config(bg="#111", fg=TEXT, font=(FONT, 10))
        self.cat_menu.pack(fill="x", ipady=3)

        # Type
        col4 = tk.Frame(row2, bg=CARD)
        col4.pack(side="left", padx=(0, 8))
        tk.Label(col4, text="Type", font=(FONT, 8),
                 bg=CARD, fg=MUTED).pack(anchor="w")
        self.type_var = tk.StringVar(value="expense")
        type_menu = tk.OptionMenu(col4, self.type_var, "expense", "income")
        type_menu.config(font=(FONT, 10), bg="#111", fg=TEXT,
                          activebackground=BORDER, relief="flat",
                          highlightthickness=1, highlightbackground=BORDER, bd=0)
        type_menu["menu"].config(bg="#111", fg=TEXT, font=(FONT, 10))
        type_menu.pack(ipady=3)

        # Date
        col5 = tk.Frame(row2, bg=CARD)
        col5.pack(side="left")
        tk.Label(col5, text="Date (YYYY-MM-DD)", font=(FONT, 8),
                 bg=CARD, fg=MUTED).pack(anchor="w")
        self.entry_date = tk.Entry(col5, font=(FONT, 11), width=13,
                                    bg="#111", fg=TEXT, relief="flat",
                                    insertbackground=GREEN,
                                    highlightthickness=1,
                                    highlightbackground=BORDER)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_date.pack(ipady=5)

        # Buttons row
        btn_row = tk.Frame(form, bg=CARD)
        btn_row.pack(fill="x", padx=10, pady=(4, 10))

        tk.Button(btn_row, text="+ ADD",
                  font=(FONT, 10, "bold"),
                  bg=GREEN, fg="#000", relief="flat", cursor="hand2",
                  activebackground="#9de050",
                  command=self._add_transaction,
                  padx=16, pady=6).pack(side="left", padx=(0, 8))

        tk.Button(btn_row, text="⚙ Manage Categories",
                  font=(FONT, 9),
                  bg=CARD2, fg=TEXT, relief="flat", cursor="hand2",
                  activebackground=BORDER,
                  command=self._manage_categories,
                  padx=10, pady=6).pack(side="left")

    # ─── TRANSACTION LIST ─────────────────────────────────────
    def _build_transaction_list(self):
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=20, pady=(14, 0))

        header = tk.Frame(frame, bg=BG)
        header.pack(fill="x", pady=(0, 6))

        tk.Label(header, text="TRANSACTIONS",
                 font=(FONT, 9, "bold"), bg=BG, fg=MUTED).pack(side="left")

        tk.Button(header, text="🗑 Delete Selected",
                  font=(FONT, 8), bg=BG, fg=RED, relief="flat",
                  cursor="hand2", activebackground=BORDER,
                  command=self._delete_selected).pack(side="right")

        # Treeview style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background=CARD2, foreground=TEXT,
                         fieldbackground=CARD2, font=(FONT, 10),
                         rowheight=26)
        style.configure("Treeview.Heading",
                         background=CARD, foreground=GREEN,
                         font=(FONT, 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#2a2a2a")])

        cols = ("Date", "Type", "Category", "Description", "Amount")
        self.tree = ttk.Treeview(frame, columns=cols,
                                  show="headings", height=10)

        for col in cols:
            self.tree.heading(col, text=col)

        self.tree.column("Date",        width=90,  anchor="center")
        self.tree.column("Type",        width=70,  anchor="center")
        self.tree.column("Category",    width=120, anchor="center")
        self.tree.column("Description", width=200, anchor="w")
        self.tree.column("Amount",      width=100, anchor="e")

        scroll = ttk.Scrollbar(frame, orient="vertical",
                                command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Color rows by type
        self.tree.tag_configure("income",  foreground=GREEN)
        self.tree.tag_configure("expense", foreground=RED)

    # ─── STATUS BAR ───────────────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self, bg=CARD, highlightthickness=1,
                       highlightbackground=BORDER)
        bar.pack(fill="x", side="bottom")

        self.lbl_status = tk.Label(bar,
                                    text="Ready",
                                    font=(FONT, 8), bg=CARD, fg=MUTED)
        self.lbl_status.pack(side="left", padx=16, pady=6)

        tk.Label(bar, text="Budget Tracker v1.0",
                 font=(FONT, 8), bg=CARD, fg="#333").pack(side="right", padx=16)

    # ─── REFRESH ──────────────────────────────────────────────
    def refresh(self):
        self._refresh_categories()
        self._refresh_transactions()
        self._refresh_summary()

    def _refresh_summary(self):
        summary = db.get_monthly_summary(self.profile_id, self.month)
        income  = summary["total_income"]  or 0
        expense = summary["total_expense"] or 0
        balance = income - expense

        c = self.currency
        self.lbl_income.config( text=f"{c}{income:,.2f}")
        self.lbl_expense.config(text=f"{c}{expense:,.2f}")
        self.lbl_balance.config(
            text=f"{c}{balance:,.2f}",
            fg=GREEN if balance >= 0 else RED
        )

    def _refresh_categories(self):
        cats = db.get_categories(self.profile_id)
        self._cat_map = {f"{c['icon']} {c['name']}": c["id"] for c in cats}

        menu = self.cat_menu["menu"]
        menu.delete(0, "end")

        if not cats:
            self.cat_var.set("— no categories —")
            menu.add_command(label="— no categories —",
                              command=lambda: self.cat_var.set("— no categories —"))
        else:
            for label in self._cat_map:
                menu.add_command(label=label,
                                  command=lambda l=label: self.cat_var.set(l))
            self.cat_var.set(list(self._cat_map.keys())[0])

    def _refresh_transactions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self._tx_ids = []
        txs = db.get_transactions(self.profile_id, self.month)

        for tx in txs:
            cat_label = f"{tx['category_icon']} {tx['category_name']}" \
                        if tx["category_name"] else "—"
            amount_str = f"{self.currency}{float(tx['amount']):,.2f}"
            if tx["type"] == "expense":
                amount_str = f"-{amount_str}"

            iid = self.tree.insert("", "end",
                values=(tx["date"], tx["type"].upper(),
                        cat_label, tx["description"] or "—", amount_str),
                tags=(tx["type"],))
            self._tx_ids.append((iid, tx["id"]))

        count = len(txs)
        self.lbl_status.config(
            text=f"{count} transaction{'s' if count != 1 else ''} in {self._month_label()}"
        )

    # ─── ACTIONS ──────────────────────────────────────────────
    def _add_transaction(self):
        desc   = self.entry_desc.get().strip()
        amount = self.entry_amount.get().strip()
        date   = self.entry_date.get().strip()
        type_  = self.type_var.get()
        cat_label = self.cat_var.get()

        # Validation
        if not desc:
            messagebox.showwarning("Missing", "Please enter a description.")
            return
        try:
            amount_f = float(amount)
            if amount_f <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid", "Enter a valid amount greater than 0.")
            return
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid Date", "Use format YYYY-MM-DD e.g. 2026-05-09")
            return
        if cat_label not in self._cat_map:
            messagebox.showwarning("No Category",
                "Please create at least one category first.\nClick '⚙ Manage Categories'.")
            return

        cat_id = self._cat_map[cat_label]
        db.add_transaction(self.profile_id, cat_id, type_,
                           amount_f, desc, date)

        # Clear form
        self.entry_desc.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        self.refresh()

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Nothing selected", "Click a row to select it first.")
            return
        if not messagebox.askyesno("Delete", "Delete selected transaction?"):
            return

        iid = selected[0]
        tx_id = next((tid for i, tid in self._tx_ids if i == iid), None)
        if tx_id:
            db.delete_transaction(tx_id)
            self.refresh()

    def _manage_categories(self):
        CategoryManager(self, self.profile_id, self.currency, self.refresh)

    # ─── MONTH NAV ────────────────────────────────────────────
    def _prev_month(self):
        y, m = map(int, self.month.split("-"))
        m -= 1
        if m == 0:
            m, y = 12, y - 1
        self.month = f"{y:04d}-{m:02d}"
        self.lbl_month.config(text=self._month_label())
        self.refresh()

    def _next_month(self):
        y, m = map(int, self.month.split("-"))
        m += 1
        if m == 13:
            m, y = 1, y + 1
        self.month = f"{y:04d}-{m:02d}"
        self.lbl_month.config(text=self._month_label())
        self.refresh()

    def _month_label(self):
        dt = datetime.strptime(self.month, "%Y-%m")
        return dt.strftime("%B %Y")


# ─── CATEGORY MANAGER (popup) ─────────────────────────────────
class CategoryManager(tk.Toplevel):
    def __init__(self, parent, profile_id, currency, on_close):
        super().__init__(parent)
        self.profile_id = profile_id
        self.on_close   = on_close
        self.title("Manage Categories")
        self.geometry("360x440")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()  # modal

        self._build_ui()
        self._load()

        self.protocol("WM_DELETE_WINDOW", self._close)

    def _build_ui(self):
        tk.Label(self, text="CATEGORIES",
                 font=(FONT, 14, "bold"), bg=BG, fg=GREEN).pack(
                 anchor="w", padx=20, pady=(16, 4))
        tk.Label(self, text="add your own spending categories",
                 font=(FONT, 8), bg=BG, fg=MUTED).pack(anchor="w", padx=20)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20, pady=10)

        # List
        self.list_frame = tk.Frame(self, bg=BG)
        self.list_frame.pack(fill="both", expand=True, padx=20)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20, pady=10)

        # Add form
        form = tk.Frame(self, bg=BG)
        form.pack(fill="x", padx=20, pady=(0, 16))

        tk.Label(form, text="Icon", font=(FONT, 8),
                 bg=BG, fg=MUTED).grid(row=0, column=0, sticky="w")
        tk.Label(form, text="Name", font=(FONT, 8),
                 bg=BG, fg=MUTED).grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.entry_icon = tk.Entry(form, font=(FONT, 13), width=4,
                                    bg="#111", fg=TEXT, relief="flat",
                                    insertbackground=GREEN,
                                    highlightthickness=1,
                                    highlightbackground=BORDER)
        self.entry_icon.insert(0, "📦")
        self.entry_icon.grid(row=1, column=0, ipady=5)

        self.entry_name = tk.Entry(form, font=(FONT, 11), width=20,
                                    bg="#111", fg=TEXT, relief="flat",
                                    insertbackground=GREEN,
                                    highlightthickness=1,
                                    highlightbackground=BORDER)
        self.entry_name.grid(row=1, column=1, padx=(8, 8), ipady=5)

        tk.Button(form, text="ADD", font=(FONT, 10, "bold"),
                  bg=GREEN, fg="#000", relief="flat", cursor="hand2",
                  activebackground="#9de050",
                  command=self._add).grid(row=1, column=2, ipady=5, ipadx=8)

    def _load(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        cats = db.get_categories(self.profile_id)
        if not cats:
            tk.Label(self.list_frame, text="No categories yet.",
                     font=(FONT, 10), bg=BG, fg=MUTED).pack(pady=10)
            return

        for cat in cats:
            row = tk.Frame(self.list_frame, bg=CARD,
                            highlightthickness=1, highlightbackground=BORDER)
            row.pack(fill="x", pady=(0, 6))

            tk.Label(row, text=f"  {cat['icon']}  {cat['name']}",
                     font=(FONT, 11), bg=CARD, fg=TEXT).pack(
                     side="left", padx=8, pady=8)

            cid = cat["id"]
            tk.Button(row, text="✕", font=(FONT, 9),
                      bg=CARD, fg=RED, relief="flat", cursor="hand2",
                      activebackground=BORDER,
                      command=lambda c=cid: self._delete(c)).pack(
                      side="right", padx=8)

    def _add(self):
        icon = self.entry_icon.get().strip() or "📦"
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Missing", "Please enter a category name.")
            return
        db.create_category(self.profile_id, name, icon)
        self.entry_name.delete(0, tk.END)
        self._load()

    def _delete(self, cat_id):
        if messagebox.askyesno("Delete", "Delete this category?\nTransactions using it will lose their category tag."):
            db.delete_category(cat_id)
            self._load()

    def _close(self):
        self.on_close()
        self.destroy()


# ─── STANDALONE TEST ──────────────────────────────────────────
if __name__ == "__main__":
    db.initialize_db()
    profiles = db.get_all_profiles()
    if not profiles:
        print("⚠️  No profiles found. Run db.py first to create one.")
    else:
        app = Dashboard(profile_id=profiles[0]["id"])
        app.mainloop()