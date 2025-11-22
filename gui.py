"""
gui.py

Simple Tkinter-based GUI for the AI Personal Finance Copilot.

This GUI demonstrates:
- Calling the FinanceAI class to predict a transaction category
- Displaying an overall efficiency score

It satisfies the basic GUI requirement with interactive widgets:
- Text entry for transaction description
- Button to predict category
- Button to show efficiency score
- Labels to display results
"""

import tkinter as tk
from tkinter import ttk, messagebox

from finance_ai import FinanceAI


class FinanceAIGUI:
    """
    Tkinter-based graphical interface for the FinanceAI engine.
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("AI Personal Finance Copilot")

        # Initialize the backend engine
        try:
            self.engine = FinanceAI()
        except Exception as e:
            messagebox.showerror("Initialization Error", str(e))
            self.root.destroy()
            return

        self._build_layout()

    def _build_layout(self) -> None:
        """
        Create and arrange all the GUI widgets.
        """

        # Main frame with some padding
        main_frame = ttk.Frame(self.root, padding="16 16 16 16")
        main_frame.grid(row=0, column=0, sticky="NSEW")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # ---- Section 1: Transaction category prediction ----
        section_label = ttk.Label(
            main_frame,
            text="Transaction Category Prediction",
            font=("Helvetica", 14, "bold"),
        )
        section_label.grid(row=0, column=0, columnspan=2, sticky="W", pady=(0, 8))

        desc_label = ttk.Label(main_frame, text="Transaction description:")
        desc_label.grid(row=1, column=0, sticky="W")

        self.desc_entry = ttk.Entry(main_frame, width=50)
        self.desc_entry.grid(row=1, column=1, sticky="WE", pady=4)

        predict_button = ttk.Button(
            main_frame,
            text="Predict Category",
            command=self.on_predict_clicked,
        )
        predict_button.grid(row=2, column=0, columnspan=2, pady=(4, 8))

        self.prediction_label = ttk.Label(
            main_frame,
            text="Predicted category: —",
            font=("Helvetica", 11),
        )
        self.prediction_label.grid(row=3, column=0, columnspan=2, sticky="W")

        # ---- Section 2: Overall efficiency score ----
        sep = ttk.Separator(main_frame, orient="horizontal")
        sep.grid(row=4, column=0, columnspan=2, sticky="EW", pady=12)

        eff_section_label = ttk.Label(
            main_frame,
            text="Overall Spending Efficiency",
            font=("Helvetica", 14, "bold"),
        )
        eff_section_label.grid(row=5, column=0, columnspan=2, sticky="W", pady=(0, 8))

        eff_button = ttk.Button(
            main_frame,
            text="Compute Efficiency Score",
            command=self.on_efficiency_clicked,
        )
        eff_button.grid(row=6, column=0, columnspan=2, pady=(4, 4))

        self.efficiency_label = ttk.Label(
            main_frame,
            text="Efficiency score: — / 100",
            font=("Helvetica", 11),
        )
        self.efficiency_label.grid(row=7, column=0, columnspan=2, sticky="W")

        # Make columns expand
        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(1, weight=1)

    def on_predict_clicked(self) -> None:
        """
        Callback for the 'Predict Category' button.
        Reads the description from the entry box, calls FinanceAI,
        and updates the prediction label.
        """
        desc = self.desc_entry.get()

        if not desc.strip():
            messagebox.showwarning(
                "Missing Input",
                "Please enter a transaction description first."
            )
            return

        try:
            category = self.engine.predict_category(desc)
            self.prediction_label.config(
                text=f"Predicted category: {category}"
            )
        except Exception as e:
            messagebox.showerror("Prediction Error", str(e))

    def on_efficiency_clicked(self) -> None:
        """
        Callback for the 'Compute Efficiency Score' button.
        Uses FinanceAI to compute an overall score and updates the label.
        """
        try:
            score = self.engine.get_efficiency_score()
            self.efficiency_label.config(
                text=f"Efficiency score: {score} / 100"
            )
        except Exception as e:
            messagebox.showerror("Efficiency Error", str(e))


def main() -> None:
    """
    Entry point for launching the Tkinter GUI.
    """
    root = tk.Tk()
    app = FinanceAIGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
