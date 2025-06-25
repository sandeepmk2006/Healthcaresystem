import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

class DoctorAppointmentSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("ARK Hospital - Doctor Portal")
        self.root.geometry("1100x650")
        self.connection = mysql.connector.connect(host='localhost', user='root', password='urk24cs5059', database='healthcare_system')
        self.cursor = self.connection.cursor()
        self.create_login_frame()
        self.update_expired_appointments()
        self.root.after(60000, self.update_expired_appointments)
    
    def create_login_frame(self):
        self.login_frame = tk.Frame(self.root, padx=20, pady=20)
        self.login_frame.pack(expand=True)
        tk.Label(self.login_frame, text="ARK Hospital Doctor Login", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        tk.Label(self.login_frame, text="Select Doctor:").grid(row=1, column=0, sticky='e', pady=5)
        self.doctor_var = tk.StringVar()
        self.doctor_combo = ttk.Combobox(self.login_frame, values=["Dr. Smith (Cardiologist)", "Dr. Johnson (Neurologist)", "Dr. Williams (Pediatrician)", "Dr. Brown (Dermatologist)"], textvariable=self.doctor_var, width=30)
        self.doctor_combo.grid(row=1, column=1, pady=5)
        tk.Label(self.login_frame, text="Password:").grid(row=2, column=0, sticky='e', pady=5)
        self.password_entry = tk.Entry(self.login_frame, show="*", width=32)
        self.password_entry.grid(row=2, column=1, pady=5)
        tk.Button(self.login_frame, text="Login", command=self.doctor_login, bg='green', fg='white').grid(row=3, column=0, columnspan=2, pady=20)
    
    def doctor_login(self):
        doctor_name = self.doctor_var.get()
        password = self.password_entry.get() 
        if not doctor_name: messagebox.showerror("Error", "Please select a doctor"); return
        if not password: messagebox.showerror("Error", "Please enter your password"); return
        self.login_frame.destroy()
        self.create_main_interface(doctor_name)
    
    def create_main_interface(self, doctor_name):
        self.doctor_name = doctor_name
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        header_frame = tk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=5)
        tk.Label(header_frame, text=f"Dr. {doctor_name.split()[0]}'s Appointment Dashboard", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        self.date_label = tk.Label(header_frame, text=datetime.now().strftime("%A, %B %d, %Y"), font=("Arial", 12))
        self.date_label.pack(side=tk.RIGHT)
        filter_frame = tk.Frame(self.main_frame)
        filter_frame.pack(fill=tk.X, pady=10)
        tk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar(value="All")
        status_options = ["All", "Scheduled", "Completed", "Cancelled", "Expired"]
        for status in status_options:
            tk.Radiobutton(filter_frame, text=status, variable=self.status_var, value=status, command=self.load_appointments).pack(side=tk.LEFT, padx=2)
        date_filter_frame = tk.Frame(filter_frame)
        date_filter_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(date_filter_frame, text="Date Range:").pack(side=tk.LEFT)
        self.start_date_entry = tk.Entry(date_filter_frame, width=10)
        self.start_date_entry.pack(side=tk.LEFT, padx=5)
        self.start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        tk.Label(date_filter_frame, text="to").pack(side=tk.LEFT)
        self.end_date_entry = tk.Entry(date_filter_frame, width=10)
        self.end_date_entry.pack(side=tk.LEFT, padx=5)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        tk.Button(date_filter_frame, text="Apply", command=self.load_appointments).pack(side=tk.LEFT, padx=5)
        self.tree_frame = tk.Frame(self.main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(self.tree_frame, columns=("ID", "Patient", "Age", "Gender", "Date", "Time", "Reason", "Status"), show="headings", height=15)
        columns = [("ID", "ID", 50), ("Patient", "Patient Name", 150), ("Age", "Age", 50), ("Gender", "Gender", 70), ("Date", "Date", 100), ("Time", "Time", 80), ("Reason", "Reason", 250), ("Status", "Status", 100)]
        for col_id, heading, width in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor='center' if col_id in ["ID", "Age", "Gender", "Status"] else 'w')
        y_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        actions = [("Refresh", self.load_appointments, 'blue'), ("Mark as Completed", self.mark_completed, 'green'), ("Cancel Appointment", self.cancel_appointment, 'red'), ("Patient Details", self.view_patient_details, 'purple'), ("Logout", self.logout, 'gray')]
        for text, command, color in actions:
            tk.Button(button_frame, text=text, command=command, bg=color, fg='white').pack(side=tk.LEFT, padx=5)
        self.load_appointments()
    
    def load_appointments(self):
        try:
            for item in self.tree.get_children(): self.tree.delete(item)
            query = """SELECT id, patient_name, patient_age, patient_gender, 
                      appointment_date, appointment_time, reason, status 
                      FROM appointments WHERE doctor_name = %s"""
            params = [self.doctor_name]
            status = self.status_var.get()
            if status != "All": query += " AND status = %s"; params.append(status)
            start_date = self.start_date_entry.get()
            end_date = self.end_date_entry.get()
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
                query += " AND appointment_date BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            except ValueError:
                messagebox.showerror("Error", "Invalid date format (use YYYY-MM-DD)")
                return
            query += " ORDER BY appointment_date, appointment_time"
            self.cursor.execute(query, tuple(params))
            appointments = self.cursor.fetchall()
            for app in appointments: self.tree.insert("", tk.END, values=app)
        except Exception as e: messagebox.showerror("Error", f"Failed to load appointments: {e}")
    
    def mark_completed(self):
        selected = self.tree.selection()
        if not selected: messagebox.showwarning("Warning", "Please select an appointment"); return
        appointment_id = self.tree.item(selected[0])['values'][0]
        current_status = self.tree.item(selected[0])['values'][7]
        if current_status != "Scheduled": messagebox.showwarning("Warning", "Only scheduled appointments can be marked as completed"); return
        confirmation = messagebox.askyesno("Confirm", "Mark this appointment as completed?")
        if confirmation:
            try:
                query = "UPDATE appointments SET status = 'Completed' WHERE id = %s"
                self.cursor.execute(query, (appointment_id,))
                self.connection.commit()
                messagebox.showinfo("Success", "Appointment marked as completed")
                self.load_appointments()
            except Exception as e: messagebox.showerror("Error", f"Failed to update appointment: {e}")
    
    def cancel_appointment(self):
        selected = self.tree.selection()
        if not selected: messagebox.showwarning("Warning", "Please select an appointment"); return
        appointment_id = self.tree.item(selected[0])['values'][0]
        current_status = self.tree.item(selected[0])['values'][7]
        if current_status != "Scheduled": messagebox.showwarning("Warning", "Only scheduled appointments can be cancelled"); return
        confirmation = messagebox.askyesno("Confirm", "Cancel this appointment?")
        if confirmation:
            try:
                query = "UPDATE appointments SET status = 'Cancelled' WHERE id = %s"
                self.cursor.execute(query, (appointment_id,))
                self.connection.commit()
                messagebox.showinfo("Success", "Appointment cancelled")
                self.load_appointments()
            except Exception as e: messagebox.showerror("Error", f"Failed to cancel appointment: {e}")
    
    def view_patient_details(self):
        selected = self.tree.selection()
        if not selected: messagebox.showwarning("Warning", "Please select an appointment"); return
        appointment_data = self.tree.item(selected[0])['values']
        details_win = tk.Toplevel(self.root)
        details_win.title("Patient Details")
        details_win.geometry("500x400")
        tk.Label(details_win, text="Patient Details", font=("Arial", 14, "bold")).pack(pady=10)
        info_frame = tk.Frame(details_win)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        labels = ["Appointment ID:", "Patient Name:", "Age:", "Gender:", "Appointment Date:", "Appointment Time:", "Reason:", "Status:"]
        for i, (label, value) in enumerate(zip(labels, appointment_data)):
            tk.Label(info_frame, text=label, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky='e', padx=5, pady=2)
            tk.Label(info_frame, text=value).grid(row=i, column=1, sticky='w', padx=5, pady=2)
        tk.Label(details_win, text="Medical Notes:", font=("Arial", 12, "bold")).pack(pady=(20,5))
        notes_frame = tk.Frame(details_win)
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        notes_text = tk.Text(notes_frame, wrap=tk.WORD)
        notes_scroll = ttk.Scrollbar(notes_frame, command=notes_text.yview)
        notes_text.configure(yscrollcommand=notes_scroll.set)
        notes_text.grid(row=0, column=0, sticky="nsew")
        notes_scroll.grid(row=0, column=1, sticky="ns")
        notes_text.insert(tk.END, "Patient History:\n- No known allergies\n- Blood type: O+\n- Last physical: 1 year ago\n\nCurrent Medications:\n- None reported")
        notes_text.config(state=tk.DISABLED)
        notes_frame.grid_rowconfigure(0, weight=1)
        notes_frame.grid_columnconfigure(0, weight=1)
        tk.Button(details_win, text="Close", command=details_win.destroy).pack(pady=10)
    
    def update_expired_appointments(self):
        try:
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            query = """UPDATE appointments SET status = 'Expired' 
                      WHERE status = 'Scheduled' AND appointment_date < %s"""
            self.cursor.execute(query, (current_date,))
            updated = self.cursor.rowcount
            if updated > 0:
                self.connection.commit()
                if hasattr(self, 'main_frame'): self.load_appointments()
        except Exception as e: print(f"Error updating expired appointments: {e}")
        finally: self.root.after(60000, self.update_expired_appointments)
    
    def logout(self):
        self.main_frame.destroy()
        self.create_login_frame()
    
    def __del__(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            try: self.cursor.close(); self.connection.close()
            except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = DoctorAppointmentSystem(root)
    root.mainloop()