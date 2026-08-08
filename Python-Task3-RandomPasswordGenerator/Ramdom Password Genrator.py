import tkinter as tk
from tkinter import ttk, messagebox
import string
import secrets
import pyperclip


class PasswordGenerator:

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Password Generator")
        self.root.geometry("650x600")
        self.root.resizable(False, False)

        self.history = []

        self.build_gui()

    def build_gui(self):

        title = tk.Label(
            self.root,
            text="Advanced Password Generator",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)

        ############################
        # Password Length
        ############################

        frame1 = tk.Frame(self.root)
        frame1.pack(pady=5)

        tk.Label(frame1, text="Password Length:", font=("Arial", 11)).pack(side=tk.LEFT)

        self.length_var = tk.IntVar(value=12)

        self.length_spin = tk.Spinbox(
            frame1,
            from_=8,
            to=64,
            width=5,
            textvariable=self.length_var
        )

        self.length_spin.pack(side=tk.LEFT, padx=10)

        ############################
        # Character Types
        ############################

        options = tk.LabelFrame(self.root, text="Character Types")
        options.pack(fill="x", padx=20, pady=10)

        self.upper = tk.BooleanVar(value=True)
        self.lower = tk.BooleanVar(value=True)
        self.number = tk.BooleanVar(value=True)
        self.symbol = tk.BooleanVar(value=True)
        self.exclude = tk.BooleanVar()

        tk.Checkbutton(
            options,
            text="Uppercase (A-Z)",
            variable=self.upper
        ).pack(anchor="w")

        tk.Checkbutton(
            options,
            text="Lowercase (a-z)",
            variable=self.lower
        ).pack(anchor="w")

        tk.Checkbutton(
            options,
            text="Numbers (0-9)",
            variable=self.number
        ).pack(anchor="w")

        tk.Checkbutton(
            options,
            text="Symbols (!@#$...)",
            variable=self.symbol
        ).pack(anchor="w")

        tk.Checkbutton(
            options,
            text="Exclude Ambiguous Characters (0 O l 1 I)",
            variable=self.exclude
        ).pack(anchor="w")

        ############################
        # Buttons
        ############################

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Generate Password",
            command=self.generate_password,
            width=20,
            bg="green",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Copy Password",
            command=self.copy_password,
            width=15
        ).pack(side=tk.LEFT)

        ############################
        # Password Display
        ############################

        self.password_var = tk.StringVar()

        entry = tk.Entry(
            self.root,
            textvariable=self.password_var,
            font=("Consolas", 14),
            width=40,
            justify="center"
        )

        entry.pack(pady=10)

        ############################
        # Strength Indicator
        ############################

        tk.Label(
            self.root,
            text="Password Strength",
            font=("Arial", 11)
        ).pack()

        self.progress = ttk.Progressbar(
            self.root,
            length=300,
            maximum=100
        )

        self.progress.pack(pady=5)

        self.strength_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 12, "bold")
        )

        self.strength_label.pack()

        ############################
        # History
        ############################

        history_frame = tk.LabelFrame(
            self.root,
            text="Last 5 Passwords"
        )

        history_frame.pack(fill="both", padx=20, pady=20)

        self.history_list = tk.Listbox(
            history_frame,
            height=5,
            font=("Consolas", 11)
        )

        self.history_list.pack(fill="both")

    ########################################################

    def get_characters(self):

        ambiguous = "0O1lI"

        upper = string.ascii_uppercase
        lower = string.ascii_lowercase
        digits = string.digits
        symbols = string.punctuation

        if self.exclude.get():

            upper = ''.join(c for c in upper if c not in ambiguous)
            lower = ''.join(c for c in lower if c not in ambiguous)
            digits = ''.join(c for c in digits if c not in ambiguous)

        selected = []

        if self.upper.get():
            selected.append(upper)

        if self.lower.get():
            selected.append(lower)

        if self.number.get():
            selected.append(digits)

        if self.symbol.get():
            selected.append(symbols)

        return selected

    ########################################################

    def generate_password(self):

        length = self.length_var.get()

        if length < 8:
            messagebox.showerror(
                "Error",
                "Password must be at least 8 characters."
            )
            return

        char_sets = self.get_characters()

        if len(char_sets) < 2:
            messagebox.showerror(
                "Error",
                "Select at least TWO character types."
            )
            return

        password = []

        # Guarantee one from each selected type
        for chars in char_sets:
            password.append(secrets.choice(chars))

        all_chars = ''.join(char_sets)

        while len(password) < length:
            password.append(secrets.choice(all_chars))

        secrets.SystemRandom().shuffle(password)

        final = ''.join(password)

        self.password_var.set(final)

        pyperclip.copy(final)

        self.update_strength(final)

        self.add_history(final)

    ########################################################

    def update_strength(self, password):

        score = 0

        if len(password) >= 8:
            score += 20

        if len(password) >= 12:
            score += 20

        if any(c.isupper() for c in password):
            score += 15

        if any(c.islower() for c in password):
            score += 15

        if any(c.isdigit() for c in password):
            score += 15

        if any(c in string.punctuation for c in password):
            score += 15

        self.progress["value"] = score

        if score < 45:
            self.strength_label.config(
                text="Weak",
                fg="red"
            )

        elif score < 75:
            self.strength_label.config(
                text="Medium",
                fg="orange"
            )

        else:
            self.strength_label.config(
                text="Strong",
                fg="green"
            )

    ########################################################

    def copy_password(self):

        pwd = self.password_var.get()

        if pwd:
            pyperclip.copy(pwd)
            messagebox.showinfo(
                "Copied",
                "Password copied to clipboard!"
            )

    ########################################################

    def add_history(self, password):

        self.history.insert(0, password)

        if len(self.history) > 5:
            self.history.pop()

        self.history_list.delete(0, tk.END)

        for pwd in self.history:
            self.history_list.insert(tk.END, pwd)


########################################################

root = tk.Tk()

PasswordGenerator(root)

root.mainloop()
