import sqlite3
from tkinter import *
from tkinter import messagebox, ttk
import random
import time
import datetime
from fpdf import FPDF

# Connect to SQLite Database
conn = sqlite3.connect('billing_system.db')
c = conn.cursor()

# Create tables if they don't exist
def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS bills (
                    bill_no INTEGER PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    total REAL NOT NULL,
                    date_time TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_no INTEGER,
                    item_name TEXT,
                    quantity REAL,
                    price REAL,
                    FOREIGN KEY (bill_no) REFERENCES bills(bill_no)
                )''')
    conn.commit()

create_tables()  # Ensure tables are created

root = Tk()
root.title("Almadina Billing Software")
root.geometry('1280x720')
bg_color = '#2E4053'

# ====================== Variables =================
c_name = StringVar()
c_phone = StringVar()
item = StringVar()
Rate = DoubleVar()  
quantity = DoubleVar()  
bill_no = StringVar()
total_amount = DoubleVar()

# Automatically Initialize Bill Number from the Database
def initialize_bill_number():
    c.execute("SELECT MAX(bill_no) FROM bills")
    last_bill_no = c.fetchone()[0]
    if last_bill_no:
        bill_no.set(str(last_bill_no + 1))
    else:
        bill_no.set("1")

initialize_bill_number()

global l
l = []

# ========================= Functions ================================

def additm():
    n = Rate.get()
    m = quantity.get() * n
    l.append(m)
    if item.get() != '':
        textarea.insert((10.0 + float(len(l) - 1)), f"{item.get()}\t\t{quantity.get()}\t\t{m}\n")
    else:
        messagebox.showerror('Error', 'Please enter item')

def gbill():
    if c_name.get() == "" or c_phone.get() == "":
        messagebox.showerror("Error", "Customer details are required")
    else:
        # Calculate total amount
        total = sum(l)
        total_amount.set(total)

        # Get the current date and time
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert bill details into the database
        c.execute("INSERT INTO bills (customer_name, phone, total, date_time) VALUES (?, ?, ?, ?)", 
                  (c_name.get(), c_phone.get(), total, current_time))
        
        # Get the last inserted bill number
        bill_no.set(c.lastrowid)

        # Insert item details into the database
        for i, item_name in enumerate(textarea.get(10.0, END).splitlines()):
            item_details = item_name.split('\t\t')
            if len(item_details) >= 3:
                c.execute("INSERT INTO items (bill_no, item_name, quantity, price) VALUES (?, ?, ?, ?)", 
                          (bill_no.get(), item_details[0], float(item_details[1]), float(item_details[2])))

        conn.commit()

        # Update the UI and save the bill to PDF
        textAreaText = textarea.get(10.0, (10.0 + float(len(l))))
        welcome()
        textarea.insert(END, textAreaText)
        textarea.insert(END, f"\n======================================")
        textarea.insert(END, f"\nTotal Amount :\t\t      {total}")
        textarea.insert(END, f"\n\n======================================")

        save_bill()  # Save the bill details to a PDF

def save_bill():
    op = messagebox.askyesno("Save Bill", "Do you want to save the Bill as PDF?")
    if op > 0:
        bill_details = textarea.get('1.0', END)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in bill_details.split('\n'):
            pdf.cell(200, 10, txt=line, ln=True)
        pdf.output(f"bills/{bill_no.get()}.pdf")  # Use updated bill number
        messagebox.showinfo("Saved", f"Bill no: {bill_no.get()} saved successfully as PDF")
    else:
        return
# Initialization of bill number
try:
    with open("bill_no.txt", "r") as f:
        last_bill_no = f.read()
        if last_bill_no:
            bill_no.set(last_bill_no)
        else:
            bill_no.set("1")
except FileNotFoundError:
    # If the file does not exist, start from 1
    bill_no.set("1")

def print_bill():
    bill_text = textarea.get("1.0", END)
    print(bill_text)  # This prints the bill to the console
    messagebox.showinfo("Print", "Bill printed successfully!")
def clear():
    c_name.set('')
    c_phone.set('')
    item.set('')
    Rate.set(0.0)
    quantity.set(0.0)
    l.clear()  # Clear the item list
    textarea.delete(1.0, END)
    initialize_bill_number()  # Reset the bill number for a new bill
    welcome()

def exit():
    op = messagebox.askyesno("Exit", "Do you really want to exit?")
    if op > 0:
        conn.close()  # Close the database connection
        root.destroy()

def welcome():
    textarea.delete(1.0, END)
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    textarea.insert(END, "\t  Welcome to Almadina Chicken Shop")
    textarea.insert(END, f"\n\nBill Number:\t\t{bill_no.get()}")
    textarea.insert(END, f"\nCustomer Name:\t\t{c_name.get()}")
    textarea.insert(END, f"\nPhone Number:\t\t{c_phone.get()}")
    textarea.insert(END, f"\nDate and Time:\t\t{current_time}")
    textarea.insert(END, f"\n\n======================================")
    textarea.insert(END, "\nProduct\t\tQTY\t\tPrice")
    textarea.insert(END, f"\n======================================\n")
    textarea.configure(font='arial 12 bold')

# ====================== GUI Components ====================
title = Label(root, pady=2, text="Almadina Billing Software", bd=12, bg=bg_color, fg='white',
              font=('times new roman', 30, 'bold'), relief=GROOVE, justify=CENTER)
title.pack(fill=X)

# Customer Details
F1 = LabelFrame(root, bd=10, relief=GROOVE, text='Customer Details', font=('times new roman', 15, 'bold'),
                fg='gold', bg=bg_color)
F1.place(x=0, y=80, relwidth=1)

cname_lbl = Label(F1, text='Customer Name', font=('times new roman', 18, 'bold'), bg=bg_color, fg='white').grid(
    row=0, column=0, padx=20, pady=5)
cname_txt = Entry(F1, width=15, textvariable=c_name, font='arial 15 bold', relief=SUNKEN, bd=7).grid(
    row=0, column=1, padx=10, pady=5)

cphone_lbl = Label(F1, text='Phone No.', font=('times new roman', 18, 'bold'), bg=bg_color, fg='white').grid(
    row=0, column=2, padx=20, pady=5)
cphone_txt = Entry(F1, width=15, font='arial 15 bold', textvariable=c_phone, relief=SUNKEN, bd=7).grid(
    row=0, column=3, padx=10, pady=5)

# Adding date and time fields
date_lbl = Label(F1, text='Date', font=('times new roman', 18, 'bold'), bg=bg_color, fg='white').grid(
    row=0, column=4, padx=20, pady=5)
date_txt = Label(F1, text=datetime.datetime.now().strftime("%Y-%m-%d"), font='arial 15 bold', bg=bg_color, fg='white')
date_txt.grid(row=0, column=5, padx=10, pady=5)
btn_print = Button(F1, text='Print Bill', font='arial 12 bold', command=print_bill, padx=10, pady=5, bg='orange')
btn_print.grid(row=0, column=6, padx=10, pady=5)
# Product Details
F2 = LabelFrame(root, text='Product Details', font=('times new roman', 18, 'bold'), fg='gold', bg=bg_color)
F2.place(x=20, y=180, width=630, height=500)

itm = Label(F2, text='Product Name', font=('times new roman', 18, 'bold'), bg=bg_color, fg='lightgreen').grid(
    row=0, column=0, padx=30, pady=20)
itm_txt = ttk.Combobox(F2, width=20, textvariable=item, font='arial 15 bold')  # Using Combobox for dropdown
itm_txt['values'] = ["Chicken", "Mutton", "Fish"]  # Example item list
itm_txt.grid(row=0, column=1, padx=10, pady=20)

rate = Label(F2, text='Product Rate', font=('times new roman', 18, 'bold'), bg=bg_color, fg='lightgreen').grid(
    row=1, column=0, padx=30, pady=20)
rate_txt = Entry(F2, width=20, textvariable=Rate, font='arial 15 bold', relief=SUNKEN, bd=7).grid(row=1, column=1, padx=10, pady=20)

n = Label(F2, text='Product Quantity', font=('times new roman', 18, 'bold'), bg=bg_color, fg='lightgreen').grid(
    row=2, column=0, padx=30, pady=20)
n_txt = Entry(F2, width=20, textvariable=quantity, font='arial 15 bold', relief=SUNKEN, bd=7).grid(row=2, column=1, padx=10, pady=20)

# ======================== Bill Area ================
F3 = Frame(root, relief=GROOVE, bd=10)
F3.place(x=700, y=180, width=500, height=500)

bill_title = Label(F3, text='Bill Area', font='arial 15 bold', bd=7, relief=GROOVE).pack(fill=X)
scrol_y = Scrollbar(F3, orient=VERTICAL)
textarea = Text(F3, yscrollcommand=scrol_y.set)
scrol_y.pack(side=RIGHT, fill=Y)
scrol_y.config(command=textarea.yview)
textarea.pack()
welcome()

# ========================= Buttons ======================
btn1 = Button(F2, text='Add Item', font='arial 15 bold', command=additm, padx=5, pady=10, bg='lime', width=15)
btn1.grid(row=5, column=0, padx=10, pady=30)

btn2 = Button(F2, text='Generate Bill', font='arial 15 bold', command=gbill, padx=5, pady=10, bg='lime', width=15)
btn2.grid(row=5, column=1, padx=10, pady=30)

btn3 = Button(F2, text='Clear', font='arial 15 bold', command=clear, padx=5, pady=10, bg='lime', width=15)
btn3.grid(row=6, column=0, padx=10, pady=30)

btn4 = Button(F2, text='Exit', font='arial 15 bold', command=exit, padx=5, pady=10, bg='lime', width=15)
btn4.grid(row=6, column=1, padx=10, pady=30)

root.mainloop()

