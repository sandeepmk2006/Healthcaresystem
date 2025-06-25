import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime, timedelta

class HealthcareAppointmentSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("ARK Hospital")                                                                                      # Window title
        self.root.geometry("900x600")                                                                                        # Window size
        self.available_time_slots = ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM"]
        self.connection = mysql.connector.connect(host='localhost', user='root', password='urk24cs5059', database='healthcare_system')
        self.cursor = self.connection.cursor()
        self.tab_control = ttk.Notebook(root)                                                                               # Create tabs container
        self.tab1 = ttk.Frame(self.tab_control)                                                                              # Schedule tab
        self.tab2 = ttk.Frame(self.tab_control)                                                                              # Status tab
        self.tab3 = ttk.Frame(self.tab_control)                                                                              # View tab
        self.tab_control.add(self.tab1, text='Schedule Appointment')
        self.tab_control.add(self.tab2, text='Check Status')
        self.tab_control.add(self.tab3, text='View Appointments')
        self.tab_control.pack(expand=1, fill='both')
        self.create_schedule_tab()                                                                                       # Initialize schedule tab
        self.create_status_tab()                                                                                         # Initialize status tab
        self.create_view_tab()                                                                                           # Initialize view tab
        self.clock_label = tk.Label(root, text="", font=('Helvetica', 12))                                               # Clock display
        self.clock_label.pack(side=tk.BOTTOM, pady=5)
        self.update_clock()                                                                                              # Start clock updates
    
    def update_clock(self):
        self.clock_label.config(text=f"Current Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.root.after(1000, self.update_clock)                                                                           # Update every second
    
    def create_schedule_tab(self):
        tk.Label(self.tab1, text="Today's Date:", font=('Helvetica', 10)).grid(row=0, column=0, padx=10, pady=5, sticky='e')
        tk.Label(self.tab1, text=datetime.now().strftime("%Y-%m-%d"), font=('Helvetica', 10)).grid(row=0, column=1, padx=10, pady=5, sticky='w')
        
                                                                            
        self.patient_name = tk.Entry(self.tab1, width=30)
        self.patient_age = tk.Entry(self.tab1, width=30)                                                                    # Create all fields first
        self.patient_gender = ttk.Combobox(self.tab1, values=["Male", "Female", "Other"], width=27)
        self.appointment_date = tk.Entry(self.tab1, width=30)
        self.appointment_time = ttk.Combobox(self.tab1, values=self.available_time_slots, width=27)
        self.doctor = ttk.Combobox(self.tab1, values=["Dr. Smith (Cardiologist)", "Dr. Johnson (Neurologist)", "Dr. Williams (Pediatrician)", "Dr. Brown (Dermatologist)"], width=27)
        
        fields = [
            ("Patient Name:", self.patient_name),
            ("Age:", self.patient_age),
            ("Gender:", self.patient_gender),
            ("Appointment Date (YYYY-MM-DD):", self.appointment_date),
            ("Appointment Time:", self.appointment_time),
            ("Doctor:", self.doctor),
        ]
        
        for row, (label, widget) in enumerate(fields, start=1):
            tk.Label(self.tab1, text=label).grid(row=row, column=0, padx=10, pady=5, sticky='e')
            widget.grid(row=row, column=1, padx=10, pady=5, sticky='w')
        
        # Now set default values after all fields are created
        self.appointment_date.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        self.appointment_time.current(0)
        self.doctor.current(0)
        
        tk.Label(self.tab1, text="Reason:").grid(row=7, column=0, padx=10, pady=5, sticky='e')
        self.reason = tk.Text(self.tab1, width=30, height=4)
        self.reason.grid(row=7, column=1, padx=10, pady=5)
        tk.Button(self.tab1, text="Schedule Appointment", command=self.schedule_appointment, bg='green', fg='white').grid(row=8, column=0, columnspan=2, pady=10)
    
    def create_status_tab(self):
        tk.Label(self.tab2, text="Appointment ID:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.appointment_id = tk.Entry(self.tab2, width=30)
        self.appointment_id.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.tab2, text="Check Status", command=self.check_status, bg='blue', fg='white').grid(row=1, column=0, columnspan=2, pady=5)
        self.status_frame = tk.LabelFrame(self.tab2, text="Appointment Status", padx=10, pady=10)
        self.status_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
        self.status_labels = []
        for i, (label, _) in enumerate([("Patient Name:", "patient_name"), ("Appointment Date:", "appointment_date"), ("Appointment Time:", "appointment_time"), ("Doctor:", "doctor_name"), ("Status:", "status")]):
            tk.Label(self.status_frame, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=2)
            value_label = tk.Label(self.status_frame, text="", width=30, anchor='w')
            value_label.grid(row=i, column=1, sticky='w', padx=5, pady=2)
            self.status_labels.append(value_label)
        self.cancel_button = tk.Button(self.tab2, text="Cancel Appointment", command=self.cancel_appointment, bg='red', fg='white', state='disabled')
        self.cancel_button.grid(row=3, column=0, columnspan=2, pady=10)
    
    def create_view_tab(self):
        self.tree = ttk.Treeview(self.tab3, columns=("ID", "Name", "Age", "Gender", "Date", "Time", "Doctor", "Reason", "Status"), show="headings", height=20)
        for col, width in [("ID", 40), ("Name", 100), ("Age", 40), ("Gender", 60), ("Date", 80), ("Time", 80), ("Doctor", 120), ("Reason", 150), ("Status", 80)]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center' if col in ["ID", "Age", "Gender", "Status"] else 'w')
        scrollbar = ttk.Scrollbar(self.tab3, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        tk.Button(self.tab3, text="Refresh", command=self.refresh_appointments, bg='blue', fg='white').grid(row=1, column=0, pady=5)
        self.refresh_appointments()
    
    def schedule_appointment(self):
        data = {
            'name': self.patient_name.get(),
            'age': self.patient_age.get(),
            'gender': self.patient_gender.get(),
            'date': self.appointment_date.get(),
            'time': self.appointment_time.get(),
            'doctor': self.doctor.get(),
            'reason': self.reason.get("1.0", tk.END).strip()
        }
        if not all(data.values()): messagebox.showerror("Error", "All fields are required!"); return
        try:
            appt_date = datetime.strptime(data['date'], "%Y-%m-%d").date()
            age = int(data['age'])
            if not (1 <= age <= 120): raise ValueError("Age must be 1-120")
            if appt_date < datetime.now().date(): messagebox.showerror("Error", "Date cannot be in past!"); return
            if appt_date == datetime.now().date() and datetime.strptime(data['time'], "%I:%M %p").time() < datetime.now().time():
                messagebox.showerror("Error", "Time cannot be in past for today!"); return
            self.cursor.execute("SELECT COUNT(*) FROM appointments WHERE appointment_date=%s AND appointment_time=%s AND doctor_name=%s AND status='Scheduled'", 
                              (data['date'], data['time'], data['doctor']))
            if self.cursor.fetchone()[0] > 0: messagebox.showerror("Error", "Time slot already booked!"); return
            self.cursor.execute("INSERT INTO appointments (patient_name,patient_age,patient_gender,appointment_date,appointment_time,doctor_name,reason,status) VALUES (%s,%s,%s,%s,%s,%s,%s,'Scheduled')", 
                              (data['name'], age, data['gender'], data['date'], data['time'], data['doctor'], data['reason']))
            self.connection.commit()
            self.cursor.execute("SELECT LAST_INSERT_ID()")
            messagebox.showinfo("Success", f"Appointment scheduled!\nID: {self.cursor.fetchone()[0]}")
            for field in [self.patient_name, self.patient_age, self.appointment_date, self.reason]: field.delete(0, tk.END) if field != self.reason else field.delete("1.0", tk.END)
            self.patient_gender.set(''); self.appointment_time.current(0); self.doctor.current(0)
            self.appointment_date.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        except ValueError as e: messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e: messagebox.showerror("Error", f"Failed to schedule: {e}")
    
    def check_status(self):
        appt_id = self.appointment_id.get()
        if not appt_id: messagebox.showerror("Error", "Please enter ID"); return
        try: appt_id = int(appt_id)
        except: messagebox.showerror("Error", "ID must be number"); return
        try:
            self.cursor.execute("SELECT patient_name,appointment_date,appointment_time,doctor_name,status FROM appointments WHERE id=%s", (appt_id,))
            if result := self.cursor.fetchone():
                for i, val in enumerate(result): self.status_labels[i].config(text=val)
                self.cancel_button.config(state='normal' if result[4] == "Scheduled" else 'disabled')
            else: 
                messagebox.showerror("Error", "ID not found")
                for label in self.status_labels: label.config(text="")
                self.cancel_button.config(state='disabled')
        except Exception as e: messagebox.showerror("Error", f"Failed to check status: {e}")
    
    def cancel_appointment(self):
        appt_id = self.appointment_id.get()
        if not appt_id: messagebox.showerror("Error", "No appointment selected"); return
        try: appt_id = int(appt_id)
        except: messagebox.showerror("Error", "ID must be number"); return
        if not messagebox.askyesno("Confirm", "Cancel this appointment?"): return
        try:
            self.cursor.execute("SELECT appointment_date,appointment_time,status FROM appointments WHERE id=%s", (appt_id,))
            if not (result := self.cursor.fetchone()): messagebox.showerror("Error", "Appointment not found"); return
            appt_datetime = datetime.strptime(f"{result[0]} {result[1]}", "%Y-%m-%d %I:%M %p")
            if appt_datetime < datetime.now() and result[2] == "Scheduled":
                self.cursor.execute("UPDATE appointments SET status='Completed' WHERE id=%s", (appt_id,))
                messagebox.showinfo("Info", "Past appointment marked 'Completed'")
            else:
                self.cursor.execute("UPDATE appointments SET status='Cancelled' WHERE id=%s", (appt_id,))
                messagebox.showinfo("Success", "Appointment cancelled")
            self.connection.commit()
            self.check_status()
        except Exception as e: messagebox.showerror("Error", f"Failed to cancel: {e}")
    
    def refresh_appointments(self):
        try:
            for item in self.tree.get_children(): self.tree.delete(item)
            self.cursor.execute("SELECT id,patient_name,patient_age,patient_gender,appointment_date,appointment_time,doctor_name,reason,status FROM appointments ORDER BY appointment_date,appointment_time")
            for app in self.cursor.fetchall(): self.tree.insert("", tk.END, values=app)
            self.update_past_appointments()
        except Exception as e: messagebox.showerror("Error", f"Failed to load: {e}")
    
    def update_past_appointments(self):
        try:
            self.cursor.execute("SELECT id FROM appointments WHERE status='Scheduled' AND CONCAT(appointment_date,' ',appointment_time) < %s", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
            if past := self.cursor.fetchall():
                self.cursor.executemany("UPDATE appointments SET status='Completed' WHERE id=%s", [(x[0],) for x in past])
                self.connection.commit()
        except Exception as e: print(f"Error updating past: {e}")
    
    def __del__(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            try: self.cursor.close(); self.connection.close()
            except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = HealthcareAppointmentSystem(root)
    root.mainloop()