import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from datetime import datetime
import numpy as np
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, 'archery_data.csv')
VALID_SCORES = {"10", "9", "8", "7", "6", "5", "0"}

class ArcheryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Archery Tracker")
        self.root.state('zoomed')  # Fullscreen windowed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Proper exit

        self.data = self.load_data()
        self.current_user = tb.StringVar()
        self.date_entry_var = tb.StringVar(value="now")

        self.sort_column = None
        self.sort_reverse = False

        self.build_layout()

    def on_closing(self):
        self.root.destroy()
        sys.exit()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                return pd.read_csv(DATA_FILE)
            except Exception:
                return pd.DataFrame(columns=['Name', 'Date & Time', 'Average Score', 'Precision'])
        else:
            return pd.DataFrame(columns=['Name', 'Date & Time', 'Average Score', 'Precision'])

    def save_data(self):
        self.data.to_csv(DATA_FILE, index=False, encoding='utf-8-sig', float_format='%.2f')

    def build_layout(self):
        main_frame = tb.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=True)

        left_frame = tb.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="n")

        right_frame = tb.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="n", padx=(20, 0))

        bottom_frame = tb.Frame(main_frame)
        bottom_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.build_score_entry(left_frame)
        self.build_leaderboard(right_frame)
        self.build_graphs(bottom_frame)

        import_button = tb.Button(right_frame, text="Import CSV", command=self.import_csv)
        import_button.pack(pady=(10, 0))

    def build_score_entry(self, frame):
        tb.Label(frame, text="User Name:").pack()
        self.username_entry = tb.Entry(frame, textvariable=self.current_user)
        self.username_entry.pack()

        tb.Label(frame, text="Date (DD-MM-YYYY or 'now'):").pack()
        self.date_entry = tb.Entry(frame, textvariable=self.date_entry_var)
        self.date_entry.pack()

        self.score_boxes = []
        for set_idx in range(2):
            group = tb.LabelFrame(frame, text=f"Set {set_idx + 1}")
            group.pack(pady=(5, 15) if set_idx == 0 else (0, 5))
            for row in range(6):
                row_entries = []
                for col in range(6):
                    e = tb.Entry(group, width=3, justify='center')
                    e.grid(row=row, column=col, padx=2, pady=2)
                    e.bind("<Return>", self.focus_next_widget)
                    e.bind("<FocusOut>", self.validate_input)
                    row_entries.append(e)
                self.score_boxes.append(row_entries)

        self.submit_button = tb.Button(frame, text="Submit Scores", command=self.submit_scores)
        self.submit_button.pack(pady=5)

    def focus_next_widget(self, event):
        try:
            event.widget.tk_focusNext().focus()
        except:
            pass
        return "break"

    def validate_input(self, event):
        value = event.widget.get()
        if value == "":
            return
        if value not in VALID_SCORES:
            event.widget.delete(0, tb.END)
            Messagebox.show_error("Invalid Input", "Please enter a valid score (10, 9, 8, 7, 6, 5, or 0)")

    def clear_score_boxes(self):
        for row_entries in self.score_boxes:
            for e in row_entries:
                e.delete(0, tb.END)

    def submit_scores(self):
        name = self.current_user.get().strip()
        if not name:
            Messagebox.show_error("Missing Name", "Please enter a user name.")
            return

        scores = []
        for row_entries in self.score_boxes:
            for e in row_entries:
                v = e.get()
                if v not in VALID_SCORES:
                    Messagebox.show_error("Invalid Entry", "All scores must be one of 10, 9, 8, 7, 6, 5, or 0")
                    return
                scores.append(int(v))

        avg = np.mean(scores)
        stddev = np.std(scores)

        date_input = self.date_entry_var.get().strip()
        if date_input.lower() == "now":
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            try:
                parsed_date = datetime.strptime(date_input, '%d-%m-%Y')
                timestamp = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                Messagebox.show_error("Invalid Date Format", "Please enter the date as DD-MM-YYYY or type 'now'.")
                return

        self.data = pd.concat([self.data, pd.DataFrame.from_records([{
            'Name': name,
            'Date & Time': timestamp,
            'Average Score': avg,
            'Precision': stddev
        }])], ignore_index=True)
        self.save_data()
        self.update_leaderboard()
        self.update_graphs()
        Messagebox.show_info("Success", "Scores submitted.")

        self.clear_score_boxes()
        self.score_boxes[0][0].focus_set()

    def import_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filepath:
            try:
                new_data = pd.read_csv(filepath)
                self.data = pd.concat([self.data, new_data], ignore_index=True).drop_duplicates()
                self.save_data()
                self.update_leaderboard()
                self.update_graphs()
                Messagebox.show_info("Imported", "CSV data successfully imported.")
            except Exception as e:
                Messagebox.show_error("Import Failed", f"Could not read file: {e}")

    def build_leaderboard(self, frame):
        tb.Label(frame, text="Leaderboard", font=("Arial", 12, "bold")).pack()
        self.tree = tb.Treeview(frame, columns=("user", "avg", "stddev"), show="headings")
        self.tree.heading("user", text="Name", command=lambda: self.sort_leaderboard("Name"))
        self.tree.heading("avg", text="Avg Score", command=lambda: self.sort_leaderboard("Average Score", reverse=True))
        self.tree.heading("stddev", text="Precision", command=lambda: self.sort_leaderboard("Precision"))
        self.tree.pack()
        self.update_leaderboard()

    def sort_leaderboard(self, column, reverse=False):
        self.sort_column = column
        self.sort_reverse = not self.sort_reverse if self.sort_column == column else reverse
        self.update_leaderboard()

    def update_leaderboard(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        if self.data.empty:
            return

        leaderboard = self.data.groupby('Name').agg({'Average Score': 'mean', 'Precision': 'mean'}).reset_index()

        if self.sort_column:
            leaderboard = leaderboard.sort_values(by=self.sort_column, ascending=not self.sort_reverse)

        for _, row in leaderboard.iterrows():
            self.tree.insert('', 'end', values=(row['Name'], f"{row['Average Score']:.2f}", f"{row['Precision']:.2f}"))

    def build_graphs(self, frame):
        self.fig1, self.ax1 = plt.subplots(figsize=(4, 3))
        self.fig2, self.ax2 = plt.subplots(figsize=(4, 3))

        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=frame)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=frame)

        self.canvas1.get_tk_widget().grid(row=0, column=0, padx=10)
        self.canvas2.get_tk_widget().grid(row=0, column=1, padx=10)

        self.update_graphs()

    def update_graphs(self):
        self.ax1.clear()
        self.ax2.clear()

        if self.data.empty:
            self.canvas1.draw()
            self.canvas2.draw()
            return

        selected_user = self.current_user.get().strip()
        if not selected_user or selected_user not in self.data['Name'].values:
            selected_user = self.data['Name'].iloc[0]

        df_user = self.data[self.data['Name'] == selected_user].sort_values('Date & Time')
        timestamps = pd.to_datetime(df_user['Date & Time'])

        self.ax1.plot(timestamps, df_user['Average Score'], marker='o')
        self.ax1.set_title('Average Over Time')
        self.ax1.set_xlabel('')
        self.ax1.set_ylabel('')

        self.ax2.plot(timestamps, -df_user['Precision'], marker='o', color='orange')
        self.ax2.set_title('')
        self.ax2.set_xlabel('')
        self.ax2.set_ylabel('- Standard Deviation')

        self.canvas1.draw()
        self.canvas2.draw()

if __name__ == '__main__':
    root = tb.Window(themename="flatly")
    app = ArcheryApp(root)
    root.mainloop()
