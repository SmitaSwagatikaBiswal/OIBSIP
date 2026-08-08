import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
class BMIDatabase:
    def __init__(self, db_name="bmi_tracker.db"):
        self.db_name = db_name
        self.create_database()
    def create_database(self):
        """Create BMI table if it does not exist."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS bmi_records(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL
                )
                """)
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
    def save_record(self, name, weight, height, bmi, category):
        """Save a BMI record."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO bmi_records
                (name, weight, height, bmi, category, date)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name,weight,height,bmi,category,datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
    def get_history(self, name):
        """Return all BMI records for a user."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT date, bmi
                FROM bmi_records
                WHERE name=?
                ORDER BY id
                """, (name,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            return []
    def delete_history(self, name):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM bmi_records WHERE name=?",(name,))
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

class BMITrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced BMI Calculator & Tracker")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        self.db = BMIDatabase()
        self.create_widgets()
    def create_widgets(self):
        title = tk.Label(self.root,text="Advanced BMI Calculator",font=("Arial", 20, "bold"),fg="blue")
        title.pack(pady=15)
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        # Name
        tk.Label(frame,text="Name",font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.name_entry = tk.Entry(frame, width=25)
        self.name_entry.grid(row=0, column=1)
        # Weight
        tk.Label(frame,text="Weight (kg)",font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.weight_entry = tk.Entry(frame, width=25)
        self.weight_entry.grid(row=1, column=1)
        # Height
        tk.Label(frame,text="Height (m)",font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.height_entry = tk.Entry(frame, width=25)
        self.height_entry.grid(row=2, column=1)
        self.result_label = tk.Label(self.root,text="BMI: --",font=("Arial", 18, "bold"))
        self.result_label.pack(pady=15)
        self.category_label = tk.Label(self.root,text="Category: --",font=("Arial", 16))
        self.category_label.pack()
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=25)
        calculate_btn = tk.Button(button_frame,text="Calculate BMI",width=18,command=self.calculate_bmi)
        calculate_btn.grid(row=0, column=0, padx=5)
        save_btn = tk.Button(button_frame,text="Save Record",width=18,command=self.save_record)
        save_btn.grid(row=0, column=1, padx=5)
        graph_btn = tk.Button(button_frame,text="Show Graph",width=18,command=self.show_graph)
        graph_btn.grid(row=1, column=0, pady=10)
        clear_btn = tk.Button(button_frame,text="Clear",width=18,command=self.clear_fields)
        clear_btn.grid(row=1, column=1)
        self.current_bmi = None
        self.current_category = None
    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.height_entry.delete(0, tk.END)
        self.result_label.config(text="BMI: --",fg="black")
        self.category_label.config(text="Category: --",fg="black")
        self.current_bmi = None
        self.current_category = None
    def get_bmi_category(self, bmi):
        """Return BMI category and corresponding color."""
        if bmi < 18.5:
            return "Underweight", "orange"
        elif bmi < 25:
            return "Normal", "green"
        elif bmi < 30:
            return "Overweight", "dark orange"
        else:
            return "Obese", "red"
    def calculate_bmi(self):
        name = self.name_entry.get().strip()
        if name == "":
            messagebox.showerror("Input Error","Please enter your name.")
            return
        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input","Weight and Height must be numeric values.")
            return
        if weight <= 0:
            messagebox.showerror("Invalid Weight","Weight must be greater than zero.")
            return
        if height <= 0:
            messagebox.showerror("Invalid Height","Height must be greater than zero.")
            return
        bmi = weight / (height ** 2)
        category, color = self.get_bmi_category(bmi)
        self.current_bmi = round(bmi, 2)
        self.current_category = category
        self.result_label.config(text=f"BMI : {self.current_bmi}",fg=color)
        self.category_label.config(text=f"Category : {category}",fg=color)
    def save_record(self):
        if self.current_bmi is None:
            messagebox.showwarning("Warning","Please calculate BMI first.")
            return
        name = self.name_entry.get().strip()
        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())
        except ValueError:
            messagebox.showerror("Error","Invalid weight or height.")
            return
        try:
            self.db.save_record(name,weight,height,self.current_bmi,self.current_category)
            messagebox.showinfo("Success","BMI record saved successfully.")
        except Exception as e:
            messagebox.showerror("Database Error",str(e))
    def show_graph(self):
        name = self.name_entry.get().strip()
        if name == "":
            messagebox.showwarning("Warning","Enter a user's name.")
            return
        try:
            history = self.db.get_history(name)
            if len(history) == 0:
                messagebox.showinfo("No Data","No BMI records found.")
                return
            dates = []
            bmi_values = []
            for record in history:
                dates.append(record[0])
                bmi_values.append(record[1])
            plt.figure(figsize=(9,5))
            plt.plot(dates,bmi_values,marker="o",linewidth=2)
            plt.title(f"{name}'s BMI Trend")
            plt.xlabel("Date")
            plt.ylabel("BMI")
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror( "Graph Error", str(e))
if __name__ == "__main__":
        root = tk.Tk()
        app = BMITrackerApp(root)
        root.mainloop()
