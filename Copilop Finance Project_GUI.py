# GUI by: Ratan Shanmugam

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("AI Personal Finance Dashboard")
        self.geometry("1100x700")
        self.minsize(950, 600)

        # main data holders
        self.df = None
        self.filtered_df = None

        self.current_month = tk.StringVar()
        self.chart_option = tk.StringVar(value="Daily Spending")
        self.manual_path = tk.StringVar()

        self._setup_style()
        self._build_ui()

# Style
    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

# Base color used
        bg_main = "#f1f5f9"   #this is page background
        bg_card = "#ffffff"   #this is for cards
        blue = "#2563eb"      #primary color used-blue
        blue_dark = "#1d4ed8"

        self.configure(bg=bg_main)

        style.configure("TFrame", background=bg_main)
        style.configure("TLabel", background=bg_main)
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background=bg_main)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 10, "bold"), background=bg_main, foreground="#334155")

        style.configure(
            "Card.TLabelframe",
            background=bg_card,
            bordercolor="#e2e8f0",
            relief="solid",
            borderwidth=1,
        )
        style.configure("Card.TLabelframe.Label", background=bg_card, foreground="#0f172a")

        style.configure("Blue.TButton",
                        background=blue,
                        foreground="white",
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor=bg_main,
                        padding=5)
        style.map("Blue.TButton",
                  background=[("active", blue_dark)])

        style.configure("Link.TLabel", foreground=blue, cursor="hand2")

#tostore colors for buttons
        self.color_blue = blue
        self.color_blue_dark = blue_dark
        self.color_card = bg_card
        self.color_main = bg_main

    def style_button_hover(self, btn):
        # add simple hover effect for buttons
        def on_enter(e):
            btn.configure(style="Blue.TButton")

        def on_leave(e):
            btn.configure(style="Blue.TButton")

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

# UI Build
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

 # Header
        header = ttk.Frame(self, padding=15)
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="💰 AI Finance Copilot — Analytics Dashboard",
                  style="Header.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header,
                  text="Visualize your spending by month, category, and merchant.",
                  style="TLabel").grid(row=1, column=0, sticky="w", pady=(2, 0))

#Top Controls
        top = ttk.Frame(self, padding=(15, 5, 15, 10))
        top.grid(row=1, column=0, sticky="ew")
        top.columnconfigure(9, weight=1)

 # Load controls
        ttk.Label(top, text="Load data:", style="SubHeader.TLabel").grid(row=0, column=0, sticky="w")

        btn_default = ttk.Button(top, text="Default CSV", style="Blue.TButton",
                                 command=self.load_default_csv)
        btn_default.grid(row=0, column=1, padx=4, pady=2, sticky="w")

        btn_browse = ttk.Button(top, text="Browse…", style="Blue.TButton",
                                command=self.open_file_dialog)
        btn_browse.grid(row=0, column=2, padx=4, pady=2, sticky="w")

        self.style_button_hover(btn_default)
        self.style_button_hover(btn_browse)

        ttk.Entry(top, textvariable=self.manual_path, width=36).grid(
            row=0, column=3, padx=(20, 4), pady=2, sticky="w"
        )
        btn_path = ttk.Button(top, text="Load Path", style="Blue.TButton",
                              command=self.load_path_file)
        btn_path.grid(row=0, column=4, padx=4, pady=2, sticky="w")
        self.style_button_hover(btn_path)

#Filters row
        ttk.Label(top, text="Month:", style="SubHeader.TLabel").grid(
            row=1, column=0, pady=(10, 0), sticky="w"
        )
        self.month_box = ttk.Combobox(top, textvariable=self.current_month,
                                      state="readonly", width=15)
        self.month_box.grid(row=1, column=1, pady=(10, 0), sticky="w")
        self.month_box.bind("<<ComboboxSelected>>", lambda e: self.filter_data())

        btn_all_months = ttk.Button(top, text="All Months", style="Blue.TButton",
                                    command=self.reset_month)
        btn_all_months.grid(row=1, column=2, pady=(10, 0), padx=4, sticky="w")
        self.style_button_hover(btn_all_months)

        ttk.Label(top, text="Chart:", style="SubHeader.TLabel").grid(
            row=1, column=3, padx=(20, 4), pady=(10, 0), sticky="e"
        )
        self.chart_box = ttk.Combobox(
            top,
            textvariable=self.chart_option,
            values=["Daily Spending", "Top Categories", "Top Merchants"],
            state="readonly",
            width=20,
        )
        self.chart_box.grid(row=1, column=4, pady=(10, 0), sticky="w")
        self.chart_box.bind("<<ComboboxSelected>>", lambda e: self.draw_chart())

        btn_refresh = ttk.Button(top, text="Refresh", style="Blue.TButton",
                                 command=self.filter_data)
        btn_refresh.grid(row=1, column=5, padx=4, pady=(10, 0), sticky="w")
        self.style_button_hover(btn_refresh)

# Summary text
        self.summary_var = tk.StringVar(value="Load a CSV to begin.")
        ttk.Label(top, textvariable=self.summary_var,
                  style="SubHeader.TLabel").grid(
            row=2, column=0, columnspan=6, pady=(10, 0), sticky="w"
        )

 #main content
        main = ttk.Frame(self, padding=(15, 0, 15, 15))
        main.grid(row=2, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

# LEFT side table
        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.rowconfigure(1, weight=1)
        left.rowconfigure(3, weight=1)
        left.columnconfigure(0, weight=1)

# Categories card
        cat_group = ttk.Labelframe(left, text="Top Categories", style="Card.TLabelframe", padding=10)
        cat_group.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        cat_group.columnconfigure(0, weight=1)
        cat_group.rowconfigure(0, weight=1)

        self.cat_table = ttk.Treeview(
            cat_group,
            columns=("cat", "amt"),
            show="headings",
            height=6
        )
        self.cat_table.heading("cat", text="Category")
        self.cat_table.heading("amt", text="Total ($)")
        self.cat_table.column("cat", width=150, anchor="w")
        self.cat_table.column("amt", width=80, anchor="e")
        self.cat_table.grid(row=0, column=0, sticky="nsew")

        cat_scroll = ttk.Scrollbar(cat_group, orient="vertical",
                                   command=self.cat_table.yview)
        self.cat_table.configure(yscrollcommand=cat_scroll.set)
        cat_scroll.grid(row=0, column=1, sticky="ns")

#Merchants card
        merch_group = ttk.Labelframe(left, text="Recurring Merchants",
                                     style="Card.TLabelframe", padding=10)
        merch_group.grid(row=2, column=0, sticky="nsew")
        merch_group.columnconfigure(0, weight=1)
        merch_group.rowconfigure(0, weight=1)

        self.merch_table = ttk.Treeview(
            merch_group,
            columns=("m", "count", "amt"),
            show="headings",
            height=8,
        )
        self.merch_table.heading("m", text="Merchant")
        self.merch_table.heading("count", text="# Tx")
        self.merch_table.heading("amt", text="Total ($)")
        self.merch_table.column("m", width=160, anchor="w")
        self.merch_table.column("count", width=60, anchor="center")
        self.merch_table.column("amt", width=90, anchor="e")
        self.merch_table.grid(row=0, column=0, sticky="nsew")

        merch_scroll = ttk.Scrollbar(merch_group, orient="vertical",
                                     command=self.merch_table.yview)
        self.merch_table.configure(yscrollcommand=merch_scroll.set)
        merch_scroll.grid(row=0, column=1, sticky="ns")

# right side chart
        chart_group = ttk.Labelframe(main, text="Spending Chart",
                                     style="Card.TLabelframe", padding=10)
        chart_group.grid(row=0, column=1, sticky="nsew")
        chart_group.rowconfigure(0, weight=1)
        chart_group.columnconfigure(0, weight=1)

        self.fig = Figure(figsize=(6, 5))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_group)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

#Data Loading
    def load_default_csv(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "data", "gold", "transactions_gold.csv")
        self._load_file(path)

    def open_file_dialog(self):
        p = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if p:
            self.manual_path.set(p)
            self._load_file(p)

    def load_path_file(self):
        p = self.manual_path.get().strip()
        if not p:
            messagebox.showwarning("Missing Path", "Please type a CSV file path.")
            return
        self._load_file(p)

    def _load_file(self, path):
        try:
            df = pd.read_csv(path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file:\n{e}")
            return

        if "date" not in df.columns or "amount" not in df.columns:
            messagebox.showerror("Invalid CSV", "CSV must have 'date' and 'amount' columns.")
            return

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

        if "category" not in df.columns:
            df["category"] = "Other"
        if "merchant" not in df.columns:
            df["merchant"] = "Misc"
        if "is_recurring" not in df.columns:
            df["is_recurring"] = False

        df["month"] = df["date"].dt.strftime("%Y-%m")

        self.df = df
        self._fill_months()
        self.filter_data()

    def _fill_months(self):
        if self.df is None:
            return
        months = ["All"] + sorted(self.df["month"].dropna().unique())
        self.month_box["values"] = months
        self.current_month.set("All")

# Filtering & summary
    def reset_month(self):
        if self.df is not None:
            self.current_month.set("All")
            self.filter_data()

    def filter_data(self):
        if self.df is None:
            return

        month = self.current_month.get()
        if month and month != "All":
            temp_df = self.df[self.df["month"] == month].copy()
        else:
            temp_df = self.df.copy()

        self.filtered_df = temp_df

        total = temp_df["amount"].sum()
        count = len(temp_df)
        label = month if month and month != "All" else "all months"

        self.summary_var.set(
            f"Showing {count} transactions for {label} • Total spending: ${total:,.2f}"
        )

        self._load_category_table()
        self._load_merchant_table()
        self.draw_chart()

# Tables
    def _load_category_table(self):
        for i in self.cat_table.get_children():
            self.cat_table.delete(i)

        if self.filtered_df is None or self.filtered_df.empty:
            return

        cat_sum = (
            self.filtered_df.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        for cat, amt in cat_sum.items():
            self.cat_table.insert("", tk.END, values=(cat, f"{amt:,.2f}"))

    def _load_merchant_table(self):
        for i in self.merch_table.get_children():
            self.merch_table.delete(i)

        if self.filtered_df is None or self.filtered_df.empty:
            return

        recurring_df = (
            self.filtered_df[self.filtered_df["is_recurring"] == True]
            if "is_recurring" in self.filtered_df.columns
            else self.filtered_df
        )

        if recurring_df.empty:
            return

        grouped = recurring_df.groupby("merchant").agg(
            count=("merchant", "size"),
            amt=("amount", "sum"),
        )
        grouped = grouped[grouped["count"] >= 3]
        grouped = grouped.sort_values(["count", "amt"], ascending=False).head(15)

        for m, row in grouped.iterrows():
            self.merch_table.insert(
                "", tk.END,
                values=(m, int(row["count"]), f"{row['amt']:,.2f}")
            )

#chart
    def draw_chart(self):
        self.ax.clear()

        if self.filtered_df is None or self.filtered_df.empty:
            self.ax.set_title("No data to display")
            self.canvas.draw()
            return

        option = self.chart_option.get()

        if option == "Top Categories":
            data = (
                self.filtered_df.groupby("category")["amount"]
                .sum()
                .sort_values(ascending=False)
                .head(8)
            )
            if not data.empty:
# category color mapping
                color_map = {
                    "Food": "#facc15",
                    "Groceries": "#22c55e",
                    "Transport": "#06b6d4",
                    "Travel": "#0ea5e9",
                    "Shopping": "#a855f7",
                    "Entertainment": "#fb923c",
                    "Subscriptions": "#f97316",
                }
                colors = [color_map.get(cat, "#2563eb") for cat in data.index]

                self.ax.bar(data.index, data.values, color=colors)
                self.ax.set_title("Top Categories by Spending")
                self.ax.set_ylabel("Total ($)")
                self.ax.set_xticklabels(data.index, rotation=45, ha="right")

        elif option == "Top Merchants":
            data = (
                self.filtered_df.groupby("merchant")["amount"]
                .sum()
                .sort_values(ascending=False)
                .head(8)
            )
            if not data.empty:
                self.ax.bar(data.index, data.values, color="#2563eb")
                self.ax.set_title("Top Merchants by Spending")
                self.ax.set_ylabel("Total ($)")
                self.ax.set_xticklabels(data.index, rotation=45, ha="right")
# Daily Spending
        else:
            daily = (
                self.filtered_df.groupby(self.filtered_df["date"].dt.date)["amount"]
                .sum()
            )
            if not daily.empty:
                x_vals = list(daily.index)
                y_vals = list(daily.values)
                self.ax.plot(range(len(x_vals)), y_vals, marker="o", color="#2563eb")
                self.ax.set_title("Daily Spending")
                self.ax.set_ylabel("Total ($)")
                self.ax.set_xticks(range(len(x_vals)))
                step = max(1, len(x_vals) // 8)
                labels = [str(d) if i % step == 0 else "" for i, d in enumerate(x_vals)]
                self.ax.set_xticklabels(labels, rotation=45, ha="right")

        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()
