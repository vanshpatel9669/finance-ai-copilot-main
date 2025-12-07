"""
gui.py

Tkinter GUI for the AI Personal Finance Copilot.

Tabs:
- Predict: type a transaction description, get category + probabilities,
  view overall and category-specific efficiency score, and clear the screen.
- Analytics: explore monthly spending, category breakdown, recurring merchants,
  top 5 categories, and suspected subscriptions.
- Help: short instructions for running and using the app.

Run with:
    python gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

from finance_ai import FinanceAI


class FinanceApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        # ---------------- To create more better button for gui ---------------- #
        style = ttk.Style()
        # Use a theme that lets us override colors
        try:
            style.theme_use("clam")
        except tk.TclError:
            # Fallback if clam is not available
            pass

        # Global button style
        style.configure(
            "TButton",
            foreground="white",
            background="#4a4a4a",
            padding=6,
            relief="raised",
            font=("Helvetica", 11, "bold"),
        )
        style.map(
            "TButton",
            background=[("active", "#5c5c5c")],
            foreground=[("active", "white")],
        )

        # ---------------- Window setup ---------------- #
        self.title("AI Personal Finance Copilot")
        self.geometry("1000x650")

        # Single engine shared by all tabs
        self.engine = FinanceAI()
        self.last_pred_label: str | None = None

        # Notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.tab_predict = ttk.Frame(self.notebook)
        self.tab_analytics = ttk.Frame(self.notebook)
        self.tab_help = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_predict, text="Predict")
        self.notebook.add(self.tab_analytics, text="Analytics")
        self.notebook.add(self.tab_help, text="Help")

        # Build each tab
        self._build_predict_tab()
        self._build_analytics_tab()
        self._build_help_tab()

    # ------------------------------------------------------------------
    # Predict tab
    # ------------------------------------------------------------------

    def _build_predict_tab(self) -> None:
        frame = self.tab_predict

        instructions = (
            "Enter a transaction description (e.g., 'Uber ride', "
            "'Netflix subscription', 'Shell gas', 'McDonalds burger') "
            "and click 'Predict Category'.\n\n"
            "The model was trained on merchant names, so giving "
            "merchant-like text works best."
        )
        ttk.Label(
            frame,
            text=instructions,
            wraplength=900,
            justify="left",
        ).grid(row=0, column=0, columnspan=4, sticky="W", pady=(0, 10))

        # Input row
        ttk.Label(frame, text="Transaction description:").grid(
            row=1, column=0, sticky="W"
        )
        self.desc_entry = ttk.Entry(frame, width=50)
        self.desc_entry.grid(row=1, column=1, sticky="WE", padx=(5, 0))
        frame.columnconfigure(1, weight=1)

        predict_btn = ttk.Button(
            frame, text="Predict Category", command=self.on_predict_clicked
        )
        predict_btn.grid(row=1, column=2, padx=5, sticky="WE")

        eff_btn = ttk.Button(
            frame, text="Show Efficiency Score", command=self.on_efficiency_clicked
        )
        eff_btn.grid(row=1, column=3, padx=5, sticky="WE")

        clear_btn = ttk.Button(
            frame, text="Clear", command=self.on_clear_clicked
        )
        clear_btn.grid(row=2, column=3, padx=5, sticky="WE", pady=(4, 8))

        # Prediction + efficiency labels
        self.predicted_label = ttk.Label(
            frame, text="Predicted category: —", font=("Helvetica", 12, "bold")
        )
        self.predicted_label.grid(row=2, column=0, columnspan=3, sticky="W", pady=8)

        self.efficiency_label = ttk.Label(
            frame, text="Efficiency score: — / 100", font=("Helvetica", 11)
        )
        self.efficiency_label.grid(row=3, column=0, columnspan=4, sticky="W", pady=4)

        # Top-k probabilities text box
        ttk.Label(frame, text="Top 3 categories (with probabilities):").grid(
            row=4, column=0, columnspan=4, sticky="W"
        )
        self.topk_box = tk.Text(frame, height=7, width=80)
        self.topk_box.grid(row=5, column=0, columnspan=4, sticky="NSEW", pady=5)
        self.topk_box.config(state="disabled")

        frame.rowconfigure(5, weight=1)

    def on_predict_clicked(self) -> None:
        desc = self.desc_entry.get().strip()
        if not desc:
            messagebox.showwarning(
                "Missing input",
                "Please type a transaction description first "
                "(e.g., 'Uber ride', 'Netflix subscription').",
            )
            return

        try:
            info = self.engine.predict_with_proba(desc)
        except Exception as e:
            messagebox.showerror("Prediction error", str(e))
            return

        main_raw = info["prediction"]
        main_pretty = self.engine.pretty_category(main_raw)
        source = info.get("source", "model")

        # remember for per-category efficiency
        self.last_pred_label = main_raw

        self.predicted_label.config(
            text=f"Predicted category: {main_raw}  "
                 f"({main_pretty})   [Source: {source}]"
        )

        # Show top-k with friendly names
        self.topk_box.config(state="normal")
        self.topk_box.delete("1.0", "end")
        self.topk_box.insert(
            "end",
            "Category (raw)       Category (friendly)          Prob\n",
        )
        self.topk_box.insert(
            "end",
            "-----------------------------------------------------------\n",
        )

        for label, prob in info["top_k"]:
            friendly = self.engine.pretty_category(label)
            self.topk_box.insert(
                "end",
                f"{label:18s}  {friendly:26s}  {prob*100:5.1f}%\n",
            )

        self.topk_box.config(state="disabled")

    def on_efficiency_clicked(self) -> None:
        """Show overall and category-specific efficiency scores."""
        try:
            overall = self.engine.get_efficiency_score()
        except Exception as e:
            messagebox.showerror("Efficiency error", str(e))
            return

        text = f"Overall efficiency: {overall:.1f} / 100"

        # If we have a current prediction, also show its impact score
        if self.last_pred_label is not None:
            try:
                cat_score = self.engine.get_category_efficiency(self.last_pred_label)
                pretty = self.engine.pretty_category(self.last_pred_label)
                text += f"   |   {pretty} impact: {cat_score:.1f} / 100"
            except Exception:
                pass

        text += "  (higher = more essential spending, less misc/shopping)"
        self.efficiency_label.config(text=text)

    def on_clear_clicked(self) -> None:
        """Clear input and output fields."""
        self.desc_entry.delete(0, "end")
        self.last_pred_label = None
        self.predicted_label.config(text="Predicted category: —")
        self.efficiency_label.config(text="Efficiency score: — / 100")
        self.topk_box.config(state="normal")
        self.topk_box.delete("1.0", "end")
        self.topk_box.config(state="disabled")

    # ------------------------------------------------------------------
    # Analytics tab
    # ------------------------------------------------------------------

    def _build_analytics_tab(self) -> None:
        frame = self.tab_analytics

        ttk.Label(
            frame,
            text="Explore your spending analytics. Use the dropdown or buttons below.",
            wraplength=900,
            justify="left",
        ).grid(row=0, column=0, columnspan=3, sticky="W", pady=(0, 8))

        ttk.Label(frame, text="View:").grid(row=1, column=0, sticky="W")

        self.analytics_option = tk.StringVar(
            value="Monthly Spend (Last 6 Months)"
        )
        options = [
            "Monthly Spend (Last 6 Months)",
            "Category Breakdown",
            "Recurring Merchants (>= 3 txns)",
        ]
        dropdown = ttk.Combobox(
            frame,
            textvariable=self.analytics_option,
            values=options,
            state="readonly",
            width=35,
        )
        dropdown.grid(row=1, column=1, sticky="W")
        dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_analytics_view())

        # Extra analytics buttons
        top_btn = ttk.Button(
            frame, text="Top 5 Categories", command=self.on_show_top_categories
        )
        top_btn.grid(row=1, column=2, padx=5, sticky="WE")

        subs_btn = ttk.Button(
            frame, text="Suspected Subscriptions",
            command=self.on_show_subscriptions,
        )
        subs_btn.grid(row=2, column=2, padx=5, sticky="WE", pady=(4, 8))

        # Text widget with scrollbars
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=2, column=0, columnspan=2, sticky="NSEW", pady=8)

        self.analytics_text = tk.Text(text_frame, wrap="none")
        self.analytics_text.grid(row=0, column=0, sticky="NSEW")

        y_scroll = ttk.Scrollbar(
            text_frame, orient="vertical", command=self.analytics_text.yview
        )
        y_scroll.grid(row=0, column=1, sticky="NS")
        x_scroll = ttk.Scrollbar(
            text_frame, orient="horizontal", command=self.analytics_text.xview
        )
        x_scroll.grid(row=1, column=0, sticky="EW")

        self.analytics_text.config(
            yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set
        )

        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)

        # Initial view
        self.update_analytics_view()

    def _set_analytics_text(self, content: str) -> None:
        """Helper to update analytics_text widget."""
        self.analytics_text.config(state="normal")
        self.analytics_text.delete("1.0", "end")
        self.analytics_text.insert("end", content)
        self.analytics_text.config(state="disabled")

    def update_analytics_view(self) -> None:
        """Update analytics view based on dropdown selection."""
        choice = self.analytics_option.get()
        try:
            if choice == "Monthly Spend (Last 6 Months)":
                df = self.engine.get_monthly_summary(last_n_months=6)
            elif choice == "Category Breakdown":
                df = self.engine.get_category_breakdown()
            else:
                df = self.engine.get_recurring_merchants(min_transactions=3)
        except Exception as e:
            messagebox.showerror("Analytics error", str(e))
            return

        self._set_analytics_text(df.head(100).to_string(index=True))

    def on_show_top_categories(self) -> None:
        """Display top 5 spending categories."""
        try:
            df = self.engine.get_top_categories(n=5)
        except Exception as e:
            messagebox.showerror("Analytics error", str(e))
            return

        text = "Top 5 categories by total spend:\n\n"
        text += df.to_string(index=False)
        self._set_analytics_text(text)

    def on_show_subscriptions(self) -> None:
        """Display suspected subscription merchants."""
        try:
            df = self.engine.get_suspected_subscriptions()
        except Exception as e:
            messagebox.showerror("Analytics error", str(e))
            return

        if df.empty:
            text = (
                "No suspected subscriptions found.\n\n"
                "(Heuristic: recurring entertainment / online merchants.)"
            )
        else:
            text = (
                "Suspected subscriptions "
                "(recurring entertainment/online merchants):\n\n"
            )
            text += df.to_string(index=False)

        self._set_analytics_text(text)

    # ------------------------------------------------------------------
    # Help tab
    # ------------------------------------------------------------------

    def _build_help_tab(self) -> None:
        frame = self.tab_help

        help_text = (
            "AI Personal Finance Copilot – Help\n\n"
            "1. Predict tab\n"
            "   • Type a transaction description such as 'Uber ride', "
            "'Netflix subscription', 'Shell gas', or 'McDonalds burger'.\n"
            "   • Click 'Predict Category' to see which spending category "
            "the system assigns.\n"
            "   • Click 'Show Efficiency Score' to view your overall "
            "spending efficiency from 0–100, plus an impact score for the\n"
            "     current predicted category.\n"
            "   • Use 'Clear' to reset the fields.\n\n"
            "2. Analytics tab\n"
            "   • Use the dropdown to switch between monthly spending, "
            "category breakdown, and recurring merchants.\n"
            "   • 'Top 5 Categories' shows where you spend the most overall.\n"
            "   • 'Suspected Subscriptions' lists recurring online/entertainment "
            "merchants (a simple heuristic for subscriptions).\n\n"
            "This project combines a trained text classification model with a "
            "small rule-based layer for common merchants to provide a more "
            "intuitive user experience, and then exposes analytics and scores "
            "through this interactive GUI."
        )

        txt = tk.Text(frame, wrap="word")
        txt.insert("1.0", help_text)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, padx=10, pady=10)


def main() -> None:
    app = FinanceApp()
    app.mainloop()


if __name__ == "__main__":
    main()