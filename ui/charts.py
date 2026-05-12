import tkinter as tk
from tkinter import ttk
import sys
import os
from datetime import datetime, timedelta
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# ─── PATH FIX ─────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

# ─── CONSTANTS ────────────────────────────────────────────────
BG      = "#0f0f0f"
CARD    = "#1a1a1a"
BORDER  = "#2a2a2a"
GREEN   = "#b6f36a"
RED     = "#f56a6a"
YELLOW  = "#f5d547"
BLUE    = "#6ab4f3"
ORANGE  = "#f59547"
PURPLE  = "#c084fc"
TEXT    = "#e8e8e8"
MUTED   = "#555555"
FONT    = "Courier"

# Chart color palette
PALETTE = [GREEN, YELLOW, BLUE, ORANGE, PURPLE, RED,
           "#f084c0", "#84f0c0", "#c0f084", "#f0c084"]


class ChartsScreen(tk.Toplevel):
    def __init__(self, parent, profile_id, currency):
        super().__init__(parent)
        self.profile_id = profile_id
        self.currency   = currency
        self.month      = datetime.now().strftime("%Y-%m")

        self.title("Spending Charts")
        self.geometry("720x680")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()

        self._build_ui()
        self.refresh()

    # ─── UI ───────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 0))

        left = tk.Frame(header, bg=BG)
        left.pack(side="left")
        tk.Label(left, text="SPENDING CHARTS",
                 font=(FONT, 18, "bold"), bg=BG, fg=GREEN).pack(anchor="w")
        tk.Label(left, text="visualize where your money goes",
                 font=(FONT, 9), bg=BG, fg=MUTED).pack(anchor="w", pady=(2, 0))

        # Month nav
        right = tk.Frame(header, bg=BG)
        right.pack(side="right")
        tk.Button(right, text="◀", font=(FONT, 10),
                  bg=BG, fg=TEXT, relief="flat", cursor="hand2",
                  activebackground=BORDER,
                  command=self._prev_month).pack(side="left", padx=(0, 6))
        self.lbl_month = tk.Label(right, text=self._month_label(),
                                   font=(FONT, 10, "bold"), bg=BG, fg=TEXT)
        self.lbl_month.pack(side="left")
        tk.Button(right, text="▶", font=(FONT, 10),
                  bg=BG, fg=TEXT, relief="flat", cursor="hand2",
                  activebackground=BORDER,
                  command=self._next_month).pack(side="left", padx=(6, 0))

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=24, pady=12)

        # Tab switcher
        tab_row = tk.Frame(self, bg=BG)
        tab_row.pack(fill="x", padx=24, pady=(0, 12))

        self.active_tab = tk.StringVar(value="pie")

        for label, value in [("🥧  By Category", "pie"),
                               ("📈  Daily Trend", "line"),
                               ("📊  Summary", "summary")]:
            tk.Radiobutton(tab_row, text=label, value=value,
                           variable=self.active_tab,
                           font=(FONT, 9), bg=BG, fg=TEXT,
                           selectcolor=CARD,
                           activebackground=BG, activeforeground=GREEN,
                           indicatoron=False, relief="flat",
                           padx=12, pady=6, cursor="hand2",
                           command=self.refresh).pack(side="left", padx=(0, 8))

        # Chart container
        self.chart_frame = tk.Frame(self, bg=BG)
        self.chart_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))

    # ─── REFRESH ──────────────────────────────────────────────
    def refresh(self):
        for w in self.chart_frame.winfo_children():
            w.destroy()
        plt.close("all")

        tab = self.active_tab.get()
        if tab == "pie":
            self._draw_pie()
        elif tab == "line":
            self._draw_line()
        elif tab == "summary":
            self._draw_summary()

    # ─── PIE CHART ────────────────────────────────────────────
    def _draw_pie(self):
        rows = db.get_spending_by_category(self.profile_id, self.month)

        if not rows:
            self._empty_state("No expense data for this month.")
            return

        labels = [f"{r['icon']} {r['name']}" for r in rows]
        values = [r["total"] for r in rows]
        colors = PALETTE[:len(labels)]

        fig = Figure(figsize=(7, 5), facecolor=BG)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(BG)

        wedges, texts, autotexts = ax.pie(
            values,
            labels=None,
            colors=colors,
            autopct="%1.1f%%",
            startangle=140,
            pctdistance=0.75,
            wedgeprops=dict(width=0.6, edgecolor=BG, linewidth=2)
        )

        for at in autotexts:
            at.set_color(BG)
            at.set_fontsize(9)
            at.set_fontfamily(FONT)
            at.set_fontweight("bold")

        # Legend
        legend = ax.legend(
            wedges, [f"{l}  {self.currency}{v:,.2f}" for l, v in zip(labels, values)],
            loc="lower center",
            bbox_to_anchor=(0.5, -0.18),
            ncol=2,
            frameon=False,
            fontsize=9
        )
        for text in legend.get_texts():
            text.set_color(TEXT)
            text.set_fontfamily(FONT)

        total = sum(values)
        ax.text(0, 0, f"{self.currency}{total:,.0f}\ntotal",
                ha="center", va="center",
                fontsize=10, fontfamily=FONT,
                fontweight="bold", color=TEXT)

        ax.set_title(f"Spending by Category — {self._month_label()}",
                     color=TEXT, fontfamily=FONT, fontsize=11, pad=16)

        fig.tight_layout()
        self._embed_chart(fig)

    # ─── LINE CHART ───────────────────────────────────────────
    def _draw_line(self):
        txs = db.get_transactions(self.profile_id, self.month)
        expenses = [t for t in txs if t["type"] == "expense"]

        if not expenses:
            self._empty_state("No expense data for this month.")
            return

        # Build daily totals
        daily = {}
        for tx in expenses:
            day = tx["date"]
            daily[day] = daily.get(day, 0) + float(tx["amount"])

        # Fill all days in month
        y, m   = map(int, self.month.split("-"))
        start  = datetime(y, m, 1)
        if m == 12:
            end = datetime(y + 1, 1, 1)
        else:
            end = datetime(y, m + 1, 1)

        all_days   = []
        all_values = []
        d = start
        while d < end:
            key = d.strftime("%Y-%m-%d")
            all_days.append(d.strftime("%d"))
            all_values.append(daily.get(key, 0))
            d += timedelta(days=1)

        # Cumulative line
        cumulative = []
        total = 0
        for v in all_values:
            total += v
            cumulative.append(total)

        fig = Figure(figsize=(7, 4.5), facecolor=BG)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(BG)

        # Bar chart for daily
        bar_colors = [RED if v > 0 else BORDER for v in all_values]
        ax.bar(all_days, all_values, color=bar_colors, alpha=0.5, zorder=2)

        # Cumulative line
        ax2 = ax.twinx()
        ax2.plot(all_days, cumulative, color=YELLOW,
                 linewidth=2, marker="o", markersize=3, zorder=3)
        ax2.set_facecolor(BG)
        ax2.tick_params(colors=MUTED, labelsize=8)
        ax2.yaxis.label.set_color(YELLOW)
        for spine in ax2.spines.values():
            spine.set_edgecolor(BORDER)

        # Styling
        ax.set_title(f"Daily Spending — {self._month_label()}",
                     color=TEXT, fontfamily=FONT, fontsize=11, pad=12)
        ax.set_xlabel("Day", color=MUTED, fontfamily=FONT, fontsize=8)
        ax.set_ylabel(f"Daily ({self.currency})", color=RED,
                      fontfamily=FONT, fontsize=8)
        ax2.set_ylabel(f"Cumulative ({self.currency})", color=YELLOW,
                       fontfamily=FONT, fontsize=8)
        ax.tick_params(colors=MUTED, labelsize=7)
        ax.set_xticks(all_days[::2])  # show every other day label

        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)
        ax.grid(axis="y", color=BORDER, linewidth=0.5, zorder=1)

        fig.tight_layout()
        self._embed_chart(fig)

    # ─── SUMMARY TABLE ────────────────────────────────────────
    def _draw_summary(self):
        summary  = db.get_monthly_summary(self.profile_id, self.month)
        by_cat   = db.get_spending_by_category(self.profile_id, self.month)
        budgets  = {b["category_id"]: b["amount"]
                    for b in db.get_budgets(self.profile_id)}
        cats     = {c["name"]: c["id"] for c in db.get_categories(self.profile_id)}

        income  = summary["total_income"]  or 0
        expense = summary["total_expense"] or 0
        balance = income - expense

        # Top summary cards
        cards = tk.Frame(self.chart_frame, bg=BG)
        cards.pack(fill="x", pady=(0, 16))

        for title, value, color in [
            ("INCOME",  f"{self.currency}{income:,.2f}",  GREEN),
            ("SPENT",   f"{self.currency}{expense:,.2f}", RED),
            ("BALANCE", f"{self.currency}{balance:,.2f}", YELLOW if balance >= 0 else RED),
        ]:
            c = tk.Frame(cards, bg=CARD, highlightthickness=1,
                         highlightbackground=BORDER)
            c.pack(side="left", expand=True, fill="both",
                   padx=(0, 8), ipady=10)
            tk.Label(c, text=title, font=(FONT, 8),
                     bg=CARD, fg=MUTED).pack()
            tk.Label(c, text=value, font=(FONT, 14, "bold"),
                     bg=CARD, fg=color).pack()

        # Category breakdown table
        tk.Label(self.chart_frame, text="CATEGORY BREAKDOWN",
                 font=(FONT, 9, "bold"), bg=BG, fg=MUTED).pack(
                 anchor="w", pady=(0, 6))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Charts.Treeview",
                         background=CARD, foreground=TEXT,
                         fieldbackground=CARD, font=(FONT, 10),
                         rowheight=26)
        style.configure("Charts.Treeview.Heading",
                         background=CARD, foreground=GREEN,
                         font=(FONT, 9, "bold"), relief="flat")
        style.map("Charts.Treeview",
                  background=[("selected", BORDER)])

        cols = ("Category", "Spent", "Budget", "Remaining", "Status")
        tree = ttk.Treeview(self.chart_frame, columns=cols,
                             show="headings", height=8,
                             style="Charts.Treeview")

        for col in cols:
            tree.heading(col, text=col)

        tree.column("Category",  width=150, anchor="w")
        tree.column("Spent",     width=110, anchor="e")
        tree.column("Budget",    width=110, anchor="e")
        tree.column("Remaining", width=110, anchor="e")
        tree.column("Status",    width=110, anchor="center")

        tree.tag_configure("ok",   foreground=GREEN)
        tree.tag_configure("warn", foreground=YELLOW)
        tree.tag_configure("over", foreground=RED)

        for row in by_cat:
            cat_id  = cats.get(row["name"])
            limit   = budgets.get(cat_id)
            spent   = row["total"]

            if limit:
                remaining = limit - spent
                pct       = (spent / limit) * 100
                status    = "✅ OK" if pct < 80 else ("⚠ WARNING" if pct < 100 else "🚨 OVER")
                tag       = "ok" if pct < 80 else ("warn" if pct < 100 else "over")
                rem_str   = f"{self.currency}{remaining:,.2f}"
                lim_str   = f"{self.currency}{limit:,.2f}"
            else:
                rem_str = "—"
                lim_str = "—"
                status  = "— no limit"
                tag     = "ok"

            tree.insert("", "end",
                        values=(f"{row['icon']} {row['name']}",
                                f"{self.currency}{spent:,.2f}",
                                lim_str, rem_str, status),
                        tags=(tag,))

        tree.pack(fill="both", expand=True)

    # ─── HELPERS ──────────────────────────────────────────────
    def _embed_chart(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _empty_state(self, message):
        tk.Label(self.chart_frame, text=message,
                 font=(FONT, 12), bg=BG, fg=MUTED).pack(
                 expand=True, pady=80)

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
        return datetime.strptime(self.month, "%Y-%m").strftime("%B %Y")


# ─── STANDALONE TEST ──────────────────────────────────────────
if __name__ == "__main__":
    db.initialize_db()
    profiles = db.get_all_profiles()
    if not profiles:
        print("⚠️  No profiles found. Run db.py first.")
    else:
        root = tk.Tk()
        root.withdraw()
        p = profiles[0]
        app = ChartsScreen(root, profile_id=p["id"], currency=p["currency"])
        root.mainloop()