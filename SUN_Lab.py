import tkinter as tk
import os
from tkinter import ttk
import datetime
import mysql.connector
from tkinter import messagebox

db_password = os.environ.get("DB_PASSWORD")

# Create a MySQL connection
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=db_password,
    database="LabAccess"
)

# Declare global filter variables
date_entry = None
time_range_entry = None
tree = None  # Define tree as a global variable
user_id_entry = None


def log_access(entry_type):
    swipe_data = user_id_entry.get()
    user_id = parse_swipe_data(swipe_data)
    cursor = connection.cursor()

    cursor.execute("SELECT user_status FROM Users WHERE userID = %s", (user_id,))
    user_status = cursor.fetchone()

    print(f"User Status for ID {user_id} is: {user_status}")  # Debugging line

    if user_status and user_status[0] == 1:
        timestamp = datetime.datetime.now()
        query = "INSERT INTO AccessRecords (userID, timestamp, entryType) VALUES (%s, %s, %s)"
        values = (user_id, timestamp, entry_type)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
    else:
        messagebox.showerror("Access Denied", "Your access is suspended")

    cursor.close()

def parse_swipe_data(swipe_data):
    if swipe_data.startswith("%A"):
        return swipe_data[2:11]
    else:
        return None

def on_entry():
    #user_id = user_id_entry.get()
    swipe_data = user_id_entry.get()
    user_id = parse_swipe_data(swipe_data)
    if user_id and is_user_id_valid(user_id):
        log_access("in")
    else:
        messagebox.showerror("Invalid ID", "ID not found")


def on_exit():
    #user_id = user_id_entry.get()
    swipe_data = user_id_entry.get()
    user_id = parse_swipe_data(swipe_data)
    if user_id and is_user_id_valid(user_id):
        log_access("out")
    else:
        messagebox.showerror("Invalid ID", "ID not found")


def is_user_id_valid(user_id):
    cursor = connection.cursor()
    cursor.execute("SELECT userID FROM Users WHERE userID = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    return result is not None


def admin_login():
    admin_id = admin_id_entry.get()
    if admin_id.startswith('%A127890011'):
        # Create a new window for admin actions
        admin_window = tk.Toplevel(root)
        admin_window.title("Admin Access Records")

        global date_entry
        global time_range_entry
        global admin_user_id_entry
        global tree  # Declare tree as global

        global active
        global suspend

        # Create filter options
        filter_frame = ttk.LabelFrame(admin_window, text="Filter Options")
        filter_frame.pack(padx=10, pady=10, fill="both", expand="yes")

        date_label = ttk.Label(filter_frame, text="Filter by Date:")
        date_label.grid(row=0, column=0)

        date_ex = ttk.Label(filter_frame, text="Ex: 2020-03-21")
        date_ex.grid(row=0, column=2)

        date_entry = ttk.Entry(filter_frame)
        date_entry.grid(row=0, column=1)

        user_ex = ttk.Label(filter_frame, text="Filter by ID:")
        user_ex.grid(row=1, column=0)

        id_label = ttk.Label(filter_frame, text="Ex: 674839301")
        id_label.grid(row=1, column=2)

        admin_user_id_entry = ttk.Entry(filter_frame)
        admin_user_id_entry.grid(row=1, column=1)

        time_range_label = ttk.Label(filter_frame, text="Filter by Time Range:")
        time_range_label.grid(row=2, column=0)

        time_ex = ttk.Label(filter_frame, text="Ex: 14:51:00 to 17:23:12")
        time_ex.grid(row=2, column=2)

        time_range_entry = ttk.Entry(filter_frame)
        time_range_entry.grid(row=2, column=1)

        filter_button = ttk.Button(filter_frame, text="Apply Filter", command=apply_filter)
        filter_button.grid(row=3, columnspan=2)

        activate_button = ttk.Button(filter_frame, text="Activate", command=activate_user)
        activate_button.grid(row=6, columnspan=1)

        active = ttk.Entry(filter_frame)
        active.grid(row=6, column=1)

        suspend_button = ttk.Button(filter_frame, text="Suspend", command=suspend_user)
        suspend_button.grid(row=7, columnspan=1)

        suspend = ttk.Entry(filter_frame)
        suspend.grid(row=7, column=1)

        # Create a treeview to display the records
        tree = ttk.Treeview(admin_window, columns=("User ID", "Timestamp", "Entry Type"))
        tree.heading("#1", text="User ID")
        tree.heading("#2", text="Timestamp")
        tree.heading("#3", text="Entry Type")

        # Fetch and display access records
        cursor = connection.cursor()
        cursor.execute("SELECT userID, timestamp, entryType FROM AccessRecords")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)

        cursor.close()

        tree.pack()

    else:
        messagebox.showerror("Login Failed", "Invalid Admin ID")


def activate_user():
    user_id = active.get()
    if is_user_id_valid(user_id):
        cursor = connection.cursor()
        # Execute an SQL query to activate the student based on their ID.
        query = "UPDATE Users SET user_status = TRUE WHERE userID = %s"
        cursor.execute(query, (user_id,))
        connection.commit()
        cursor.close()


def suspend_user():
    user_id = suspend.get()
    if is_user_id_valid(user_id):
        cursor = connection.cursor()
        # Execute an SQL query to suspend the student based on their ID.
        query = "UPDATE Users SET user_status = FALSE WHERE userID = %s"
        cursor.execute(query, (user_id,))
        connection.commit()
        cursor.close()

def old_records():
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=5*365)

    cursor = connection.cursor()
    query = "DELETE From AccessRecords WHERE timestamp < %s"

    cursor.execute(query, (cutoff_date,))
    connection.commit()
    cursor.close()

    print(f"Old records before {cutoff_date} have been deleted")


def apply_filter():
    # Get filter criteria
    selected_date = date_entry.get()
    selected_user_id = admin_user_id_entry.get()
    selected_time_range = time_range_entry.get()

    # Debugging: Print the filter criteria
    print("Selected Date:", repr(selected_date))
    print("Selected ID:", repr(selected_user_id))
    print("Selected Time Range:", repr(selected_time_range))

    # Start with a base query
    query = "SELECT userID, timestamp, entryType FROM AccessRecords WHERE 1"

    # Create a list to store filter conditions
    conditions = []

    if selected_date:
        conditions.append(f"DATE(timestamp) = '{selected_date}'")

    if selected_user_id:
        conditions.append(f"userID = '{selected_user_id}'")

    if selected_time_range:
        start_time, end_time = selected_time_range.split(" to ")
        conditions.append(f"TIME(timestamp) BETWEEN '{start_time}' AND '{end_time}'")

    # Add the conditions to the query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Debugging: Print the generated query
    print("Generated Query:", query)

    # Execute the query and update the treeview
    cursor = connection.cursor()
    cursor.execute(query)
    records = cursor.fetchall()

    tree.delete(*tree.get_children())  # Delete previous records

    for record in records:
        tree.insert("", "end", values=record)

    cursor.close()


root = tk.Tk()
root.title("Lab Access Tracking")
root.geometry("800x600")

user_id_label = ttk.Label(root, text="Student/Faculty ID:")
user_id_entry = ttk.Entry(root)
user_id_entry.pack()

entry_button = ttk.Button(root, text="Log Entry", command=on_entry)
exit_button = ttk.Button(root, text="Log Exit", command=on_exit)

admin_id_label = ttk.Label(root, text="Admin ID:")
admin_id_entry = ttk.Entry(root)

admin_button = ttk.Button(root, text="Admin Login", command=admin_login)

user_id_label.pack()
entry_button.pack()
exit_button.pack()
admin_id_label.pack()
admin_id_entry.pack()
admin_button.pack()

old_records()

root.mainloop()