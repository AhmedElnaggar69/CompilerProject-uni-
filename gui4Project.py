import tkinter as tk
from tkinter import scrolledtext, ttk
from lexer import lexer
from semanticAnal import analyze

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Compiler Project - Spring 2026")
        self.root.geometry("800x700")

        # ── shared input area ─────────────────────────────────────────────
        tk.Label(root, text="Source Code:", font=("Arial", 12, "bold")).pack(pady=5)

        self.input_area = scrolledtext.ScrolledText(root, height=10, font=("Consolas", 11))
        self.input_area.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

        # ── buttons ───────────────────────────────────────────────────────
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.lexer_btn = tk.Button(btn_frame, text="Run Lexer",
                                   command=self.run_lexer,
                                   bg="#4CAF50", fg="white",
                                   font=("Arial", 10, "bold"), width=15)
        self.lexer_btn.pack(side=tk.LEFT, padx=10)

        self.semantic_btn = tk.Button(btn_frame, text="Run Semantic",
                                      command=self.run_semantic,
                                      bg="#2196F3", fg="white",
                                      font=("Arial", 10, "bold"), width=15)
        self.semantic_btn.pack(side=tk.LEFT, padx=10)

        self.clear_btn = tk.Button(btn_frame, text="Clear",
                                   command=self.clear_all,
                                   bg="#f44336", fg="white",
                                   font=("Arial", 10, "bold"), width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=10)

        # ── notebook (tabs) ───────────────────────────────────────────────
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Tab 1 — Lexer output
        lexer_tab = tk.Frame(self.notebook)
        self.notebook.add(lexer_tab, text="  Lexer Output  ")

        self.lexer_output = scrolledtext.ScrolledText(lexer_tab, font=("Consolas", 10), bg="#f4f4f4")
        self.lexer_output.pack(fill=tk.BOTH, expand=True)
        self.lexer_output.config(state=tk.DISABLED)

        # Tab 2 — Symbol table
        table_tab = tk.Frame(self.notebook)
        self.notebook.add(table_tab, text="  Symbol Table  ")

        # use a Treeview for a proper table look
        columns = ("Name", "Type", "Line")
        self.tree = ttk.Treeview(table_tab, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 3 — Semantic errors
        errors_tab = tk.Frame(self.notebook)
        self.notebook.add(errors_tab, text="  Semantic Errors  ")

        self.errors_output = scrolledtext.ScrolledText(errors_tab, font=("Consolas", 10), bg="#fff8f8")
        self.errors_output.pack(fill=tk.BOTH, expand=True)
        self.errors_output.config(state=tk.DISABLED)

    # ── LEXER ─────────────────────────────────────────────────────────────
    def run_lexer(self):
        source_code = self.input_area.get("1.0", tk.END)

        self.lexer_output.config(state=tk.NORMAL)
        self.lexer_output.delete("1.0", tk.END)

        try:
            tokens = lexer(source_code).tokenize()

            if not tokens:
                self.lexer_output.insert(tk.END, "No tokens found.")
            else:
                for tok in tokens:
                    self.lexer_output.insert(tk.END, f"{tok}\n")

            # switch to lexer tab
            self.notebook.select(0)

        except Exception as e:
            self.lexer_output.insert(tk.END, f"Lexer Error: {str(e)}")

        self.lexer_output.config(state=tk.DISABLED)

    # ── SEMANTIC ──────────────────────────────────────────────────────────
    def run_semantic(self):
        source_code = self.input_area.get("1.0", tk.END)

        # clear previous results
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.errors_output.config(state=tk.NORMAL)
        self.errors_output.delete("1.0", tk.END)

        try:
            tokens = lexer(source_code).tokenize()
            table, errs = analyze(tokens)

            # fill symbol table tab
            for name, info in table.allEntries():
                self.tree.insert("", tk.END, values=(name, info['type'], info['line']))

            # fill errors tab
            if errs:
                for e in errs:
                    self.errors_output.insert(tk.END, f"❌  {e}\n")
            else:
                self.errors_output.insert(tk.END, "✅  No semantic errors found.")

            # switch to errors tab if there are errors, else symbol table
            if errs:
                self.notebook.select(2)
            else:
                self.notebook.select(1)

        except Exception as e:
            self.errors_output.insert(tk.END, f"Error: {str(e)}")
            self.notebook.select(2)

        self.errors_output.config(state=tk.DISABLED)

    # ── CLEAR ─────────────────────────────────────────────────────────────
    def clear_all(self):
        self.input_area.delete("1.0", tk.END)

        self.lexer_output.config(state=tk.NORMAL)
        self.lexer_output.delete("1.0", tk.END)
        self.lexer_output.config(state=tk.DISABLED)

        for row in self.tree.get_children():
            self.tree.delete(row)

        self.errors_output.config(state=tk.NORMAL)
        self.errors_output.delete("1.0", tk.END)
        self.errors_output.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()