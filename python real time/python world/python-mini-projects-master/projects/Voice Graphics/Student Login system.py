
from tkinter import *
from PIL import Image,ImageTk
from tkinter import messagebox as ms
from tkinter import ttk
from pygame import mixer
mixer.init()


# Sqlite Connectivity
import sqlite3 as sql
con = sql.connect(database="Student_db.sqlite")
cursor = con.cursor()
try:
    cursor.execute("Create table Student (Std_ID int primary key, Std_Name text, Std_Mob_No text, Std_Course text,Course_Fee int,Balance int)")
    cursor.execute("Create table Course(Course_Name text primary key ,Course_fee int)")
except Exception as e:
    print(e)
con.commit()
con.close()





# root window
root = Tk()
root.title("GUI")
root.state('zoom')
root.configure(bg = "powder blue")
root.resizable(width=False,height=False)

# global variables and widgets


# header of window

frame_header = Frame(root)
frame_header.configure(bg = "pink",bd = 10,relief = SUNKEN)
frame_header.place(x = 0 , y = 0,relwidth = 1,relheight = 0.20)
frame_header_label = Label(frame_header,text = "Student Management System",bg = "pink",font = ('comicsansms',50,'bold','underline'), pady = 25)
frame_header_label.pack()

img1 = Image.open("r.png")
img1 = img1.resize((150, 125), Image.ANTIALIAS)
deco = ImageTk.PhotoImage(img1)
img_label = Label(frame_header, image=deco,bg = "pink")
img_label.place(relx = 0.04,rely = 0.02)

img2 = Image.open("hello.png")
img2 = img2.resize((150, 125), Image.ANTIALIAS)
deco_1 = ImageTk.PhotoImage(img2)
img_label_1 = Label(frame_header, image=deco_1,bg = "pink")
img_label_1.place(relx = 0.8,rely = 0.02)


def sub_main_body():

    global login_photo,reset_photo
    def reset():
        main_body()

    def login():
        u = user_entry.get()
        p = pass_entry.get()
        if u == "" and p == "":
            ms.showwarning("Validation","Username and password can't be empty")
        else:
            if u == "1049525" and p == "Cbr@1122":
                frame_sub_main_body.destroy()
                login_body()
            else:
                ms.showerror("Validation", "Ivalid Username and password")

    frame_admin_welcome = Frame(frame_body)
    frame_admin_welcome.configure(relief=SUNKEN, bg="powder blue",bd = 5)
    frame_admin_welcome.place(relx=0.398, rely=0.1, relwidth=0.23, relheight=.1)

    label = Label(frame_admin_welcome, text="LOGIN ", font=('comicsansms', 25, 'bold'), bg="powder blue")
    label.pack(anchor=CENTER)


    frame_sub_main_body = Frame(frame_body)
    frame_sub_main_body.configure(bd = 5,relief = GROOVE)
    frame_sub_main_body.place(relx = 0.23,rely = 0.2,relwidth = 0.55,relheight = .4)

    label = Label(frame_sub_main_body,text = "Username :",padx = 60,pady = 37,font = ('comicsansms',25,'bold'))
    label.grid(row = 0 , column = 0)

    label = Label(frame_sub_main_body, text="Password :", padx=60, pady=35, font=('comicsansms', 25, 'bold'))
    label.grid(row=1, column=0)

    user_value = StringVar()
    pass_value = StringVar()

    user_entry = Entry(frame_sub_main_body,textvariable = user_value,width = 25,bd = 5,font = "large_font 20",justify = LEFT,insertwidth =2)
    user_entry.focus()
    user_entry.grid(row = 0,column = 1)

    pass_entry = Entry(frame_sub_main_body,textvariable = pass_value,width = 25,bd = 5,font = "large_font 20",justify = LEFT,insertwidth =.1,show = "*")
    pass_entry.grid(row = 1,column = 1)

    img = Image.open("login.png")
    img = img.resize((200, 60), Image.ANTIALIAS)
    login_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=login_photo)

    login_button = Button(frame_body,image = login_photo,font="comicsansms 25 bold",command = login,bd = 0,bg = "powder blue")
    login_button.place(relx = 0.52,rely = 0.7)

    img = Image.open("reset.png")
    img = img.resize((200, 60), Image.ANTIALIAS)
    reset_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=reset_photo)

    reset_button = Button(frame_body, image = reset_photo, font="comicsansms 25 bold",command = reset,bd = 0,bg = "powder blue")
    reset_button.place(relx=0.32, rely=0.7)


def main_body():
    global frame_body,photo
    frame_body = Frame(root)
    frame_body.configure(bg = "powder blue")
    frame_body.place(x = 0,rely = 0.2,relwidth = 1,relheight = .8)
    sub_main_body()


def login_body():

    global logout_photo
    mixer.music.load("Welcome.mp3")
    mixer.music.play(1)

    def logout():
        frame_login_body.destroy()
        main_body()

    def Register_Student():
        frame_login_body.destroy()
        Register_Student_body()

    def Find_Student():
        frame_login_body.destroy()
        Find_Stundent_body()

    def Deposit_Fee():
        frame_login_body.destroy()
        Deposite_Fee_Body()

    def Add_Course():
        frame_login_body.destroy()
        Add_Course_Body()

    def Update_Course():
        frame_login_body.destroy()
        Update_Course_Body()

    frame_login_body = Frame(root)
    frame_login_body.configure(bg="powder blue")
    frame_login_body.place(x=0, rely=0.2, relwidth=1, relheight=.8)

    frame_admin_welcome = Frame(frame_login_body)
    frame_admin_welcome.configure(relief = SUNKEN,bg = "#f79c96")
    frame_admin_welcome.place(relx = 0.0001,rely = 0.001,relwidth = 0.23,relheight = .1)

    label = Label(frame_admin_welcome, text="Welcome Admin", font=('comicsansms', 25, 'bold'),bg = "#f79c96")
    label.pack(anchor = CENTER)

    img = Image.open("logout.png")
    img = img.resize((200, 60), Image.ANTIALIAS)
    logout_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=logout_photo,bg = "powder blue")

    logout_button = Button(frame_login_body, image = logout_photo,command=logout,bd = 0,bg = "powder blue")
    logout_button.place(relx=0.85, rely=0.002)

    #Sub login frame  and  login buttons

    frame_sub_login_body = Frame(frame_login_body)
    frame_sub_login_body.configure(bd=5, relief=GROOVE)
    frame_sub_login_body.place(relx=0.33, rely=0.08, relwidth=0.42, relheight=.9)

    Register_button = Button(frame_sub_login_body, text="Register Student", font="comicsansms 25 bold", padx=20, pady=2, bg="#7ee431",command = Register_Student,width = 20)
    Register_button.place(relx=0.1, rely=0.06)

    Find_button = Button(frame_sub_login_body, text="Find Student", font="comicsansms 25 bold", padx=20, pady=2, bg="#7ee431",command = Find_Student ,width = 20)
    Find_button.place(relx=0.1, rely=0.26)

    Deposit_button = Button(frame_sub_login_body, text="Deposit Fee", font="comicsansms 25 bold", padx=20, pady=2, bg="#7ee431",command = Deposit_Fee,width = 20)
    Deposit_button.place(relx=0.1, rely=0.44)

    Add_Course_button = Button(frame_sub_login_body, text="Add Course", font="comicsansms 25 bold", padx=20, pady=2, bg="#7ee431",command = Add_Course ,width = 20)
    Add_Course_button.place(relx=0.1, rely=0.62)

    Update_Fee_button = Button(frame_sub_login_body, text="Update Fee", font="comicsansms 25 bold", padx=20, pady=2, bg="#7ee431",command = Update_Course,width = 20)
    Update_Fee_button.place(relx=0.1, rely=0.8)


def Register_Student_body():
    global logout_photo,Home_photo,register_photo,course_combobox
    Rool_value, Name_value, Mobile_value, Fee_value = StringVar(), StringVar(), StringVar(), StringVar()

    def logout():
        frame_register_body.destroy()
        main_body()

    def Home():
        frame_register_body.destroy()
        login_body()

    def Register_Std_db():

        class Phone_Number_Error(Exception):
            def __init__(self, value):
                self.value = value

        Mobile = Mobile_value.get()
        Registeration_Fee = Fee_value.get()
        l = course_combobox.get().split()
        con = sql.connect(database="Student_db.sqlite")
        cursor = con.cursor()
        try:
            Registeration_Fee = int(Registeration_Fee)
            Student_Course = l[0]
            course_fee = int(l[1])
            Balance = course_fee - Registeration_Fee
            if len(Mobile) != 10:
                raise Phone_Number_Error("Mobile Number Should of 10 digits")
            cursor.execute("insert into Student values (?,?,?,?,?,?)",(Rool_value.get(),Name_value.get(), Mobile,Student_Course,course_fee,Balance ))
            con.commit()
            ms.showinfo("","Registered Successfully")
        except Phone_Number_Error as P:
            ms.showwarning("Warning",f"{P}")
        except Exception as e:
            ms.showwarning("Warning",f"Something Is Going Wrong, {e}")
        finally:
            con.close()


    frame_register_body = Frame(root)
    frame_register_body.configure(bg="powder blue")
    frame_register_body.place(x=0, rely=0.2, relwidth=1, relheight=.8)

    frame_admin_welcome = Frame(frame_register_body)
    frame_admin_welcome.configure(relief=SUNKEN, bg="#f79c96")
    frame_admin_welcome.place(relx=0.0001, rely=0.001, relwidth=0.23, relheight=.1)

    label = Label(frame_admin_welcome, text="Welcome Admin", font=('comicsansms', 25, 'bold'), bg="#f79c96")
    label.pack(anchor=CENTER)

    img = Image.open("logout.png")
    img = img.resize((200, 60), Image.ANTIALIAS)
    logout_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=logout_photo, bg="powder blue")

    logout_button = Button(frame_register_body, image=logout_photo, command=logout, bd=0, bg="powder blue")
    logout_button.place(relx=0.85, rely=0.002)

    img = Image.open("home6.png")
    img = img.resize((80, 60), Image.ANTIALIAS)
    Home_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=Home_photo, bg="powder blue")

    Home_button = Button(frame_register_body, image=Home_photo, command=Home, bd=0, bg="powder blue")
    Home_button.place(relx=0.78, rely=0.002)

    # Sub register frame  and  login buttons

    frame_sub_register_body = Frame(frame_register_body)
    frame_sub_register_body.configure(bd=5, relief=GROOVE)
    frame_sub_register_body.place(relx=0.245, rely=0.1, relwidth=0.52, relheight=0.7)


    # connectivity to sqlite
    con = sql.connect(database="Student_db.sqlite")
    cursor = con.cursor()
    cursor.execute("Select max(Std_Id) from student")
    max_id = cursor.fetchone()
    if max_id[0] == None:
        Std_id = 1
    else:
        Std_id = max_id[0] + 1
    con.commit()
    con.close()
    Rool_value.set(Std_id)


    Student_Roll_label = Label(frame_sub_register_body,fg = "darkblue", text="Student Reg Id :", font=('comicsansms', 25, 'bold'))
    Student_Roll_label.place(relx=0.02, rely=0.1)
    Student_Name_label = Label(frame_sub_register_body,fg = "darkblue" ,text="Student Name  :", font=('comicsansms', 25, 'bold'))
    Student_Name_label.place(relx = 0.02,rely = 0.28)
    Student_Mobile_label = Label(frame_sub_register_body,fg = "darkblue", text="Student Phone :", font=('comicsansms', 25, 'bold'))
    Student_Mobile_label.place(relx = 0.02,rely = 0.46)
    Student_course_label = Label(frame_sub_register_body,fg = "darkblue", text="Select Course  :", font=('comicsansms', 25, 'bold'))
    Student_course_label.place(relx = 0.02,rely = 0.64)
    Student_Registeration_fee_label = Label(frame_sub_register_body,fg = "darkblue", text="Std Course Fee:", font=('comicsansms', 25, 'bold'))
    Student_Registeration_fee_label.place(relx = 0.02,rely = 0.82)


    Roll_entry = Entry(frame_sub_register_body,state = DISABLED ,textvariable=Rool_value, width=25, bd=5, font="large_font 20",justify=LEFT, insertwidth=2)
    Roll_entry.place(relx=0.4, rely=0.1)
    Name_entry = Entry(frame_sub_register_body, textvariable=Name_value, width=25, bd=5, font="large_font 20", justify=LEFT,insertwidth=2)
    Name_entry.focus()
    Name_entry.place(relx = 0.4,rely = 0.28)
    Mobile_entry = Entry(frame_sub_register_body, textvariable=Mobile_value, width=25, bd=5, font="large_font 20", justify=LEFT,insertwidth=2)
    Mobile_entry.place(relx = 0.4,rely = 0.46)

    # connection to sqlite

    con = sql.connect(database="Student_db.sqlite")
    cursor = con.cursor()
    cursor.execute("select * from course")
    Courses = cursor.fetchall()
    cursor.close()
    print(Courses)
    Courses.insert(0,"----Select Course----")


    course_combobox = ttk.Combobox(frame_sub_register_body,width = 25, font="large_font 20",justify=LEFT,values = Courses)
    # values = ["----Select Course----", "Python", "Django", "Java", "Java Script"]
    course_combobox.place(relx = 0.4,rely = 0.64)
    course_combobox.current(0)

    Fee_entry = Entry(frame_sub_register_body, textvariable=Fee_value, width=25, bd=5, font="large_font 20", justify=LEFT,insertwidth=2)
    Fee_entry.place(relx = 0.4,rely = 0.82)


    img = Image.open("register.png")
    img = img.resize((250, 80), Image.ANTIALIAS)
    register_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=register_photo, bg="powder blue")

    Register_button = Button(frame_register_body, image=register_photo, command=Register_Std_db, bd=0, bg="powder blue")
    Register_button.place(relx=0.42, rely=0.83)


def Find_Stundent_body():

    global logout_photo, Home_photo, register_photo, Search_photo
    def logout():
        frame_Find_student_body.destroy()
        main_body()

    def Home():
        frame_Find_student_body.destroy()
        login_body()

    def Search_Student():
        con = sql.connect(database="Student_db.sqlite")
        cursor = con.cursor()
        try:
            if len(Find_Student_value.get()) == 0:
                raise Exception

            cursor.execute(f"SELECT * from Student WHERE Std_Id = '{Find_Student_value.get()}'")
            Student_record = cursor.fetchall()
            s = Student_record[0]

            frame_Print_Main = Frame(frame_Find_student_body)
            frame_Print_Main.configure(relief=SUNKEN,bd = 10,bg = "powder blue")
            frame_Print_Main.place(relx=0.07, rely=0.68, relwidth=0.89, relheight=.2)

            # Student Labels Frame and their labels

            frame_Print_Student_label = Frame(frame_Print_Main)
            frame_Print_Student_label.configure(relief=SUNKEN,width = 600)
            frame_Print_Student_label.grid(row = 0 , column = 0)

            label_name = Label(frame_Print_Student_label, text=f"| Student ID   |", font=('comicsansms', 18, 'bold','underline'),bg = "#f79c96")
            label_name.grid(row = 0,column = 0)
            label_name = Label(frame_Print_Student_label, text=f" Student Name  |", font=('comicsansms', 18, 'bold','underline'),bg = "#f79c96")
            label_name.grid(row = 0,column = 1)
            label_name = Label(frame_Print_Student_label, text=f" Student Phone |", font=('comicsansms', 18, 'bold','underline'),bg = "#f79c96")
            label_name.grid(row = 0,column = 2)
            label_name = Label(frame_Print_Student_label, text=f" Student Course  |", font=('comicsansms', 18, 'bold','underline'),bg = "#f79c96")
            label_name.grid(row = 0,column = 3)
            label_name = Label(frame_Print_Student_label, text=f" Std Course Fee  |", font=('comicsansms', 18, 'bold','underline'),bg = "#f79c96")
            label_name.grid(row = 0,column = 4)
            label_name = Label(frame_Print_Student_label, text=f" Reamaining Fee |", font=('comicsansms', 18, 'bold','underline'),bg = "#f79c96")
            label_name.grid(row = 0,column = 5)

            # Student Records Frame and their labels


            label_name = Label(frame_Print_Main, text=f"{s[0]}", font=('comicsansms', 16, 'bold'),bg = "powder blue")
            label_name.place(relx = 0.03,rely = 0.51)
            label_name = Label(frame_Print_Main, text=f"{s[1]}", font=('comicsansms', 16, 'bold'),bg = "powder blue")
            label_name.place(relx = 0.14,rely = 0.51)
            label_name = Label(frame_Print_Main, text=f"{s[2]}", font=('comicsansms', 16, 'bold'),bg = "powder blue")
            label_name.place(relx = 0.32,rely = 0.51)
            label_name = Label(frame_Print_Main, text=f"{s[3]}", font=('comicsansms', 16, 'bold'),bg = "powder blue")
            label_name.place(relx = 0.47,rely = 0.51)
            label_name = Label(frame_Print_Main, text=f"{s[4]}", font=('comicsansms', 16, 'bold'),bg = "powder blue")
            label_name.place(relx = 0.7,rely = 0.51)
            label_name = Label(frame_Print_Main, text=f"{s[5]}", font=('comicsansms', 16, 'bold'),bg = "powder blue")
            label_name.place(relx = 0.88,rely = 0.51)

        except:
            ms.showwarning("Warning","Please Enter the Student Registeration Id")


    frame_Find_student_body = Frame(root)
    frame_Find_student_body.configure(bg="powder blue")
    frame_Find_student_body.place(x=0, rely=0.2, relwidth=1, relheight=.8)

    frame_admin_welcome = Frame(frame_Find_student_body)
    frame_admin_welcome.configure(relief=SUNKEN, bg="#f79c96")
    frame_admin_welcome.place(relx=0.0001, rely=0.001, relwidth=0.23, relheight=.1)

    label = Label(frame_admin_welcome, text="Welcome Admin", font=('comicsansms', 25, 'bold'), bg="#f79c96")
    label.pack(anchor=CENTER)

    img = Image.open("logout.png")
    img = img.resize((200, 60), Image.ANTIALIAS)
    logout_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=logout_photo, bg="powder blue")

    logout_button = Button(frame_Find_student_body, image=logout_photo, command=logout, bd=0, bg="powder blue")
    logout_button.place(relx=0.85, rely=0.002)

    img = Image.open("home6.png")
    img = img.resize((80, 60), Image.ANTIALIAS)
    Home_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=Home_photo, bg="powder blue")

    Home_button = Button(frame_Find_student_body, image=Home_photo, command=Home, bd=0, bg="powder blue")
    Home_button.place(relx=0.78, rely=0.002)

    # Sub find Studnet frame and button

    frame_sub_find_student_body = Frame(frame_Find_student_body)
    frame_sub_find_student_body.configure(bd=5, relief=GROOVE)
    frame_sub_find_student_body.place(relx=0.255, rely=0.15, relwidth=0.52, relheight=0.27)

    Find_Student_value = StringVar()

    Student_Id_label = Label(frame_sub_find_student_body, fg="darkblue", text="Student Reg id :",font=('comicsansms', 25, 'bold'))
    Student_Id_label.place(relx=0.02, rely=0.32)

    Find_Student_entry = Entry(frame_sub_find_student_body, textvariable=Find_Student_value, width=25, bd=5, font="large_font 20",justify=LEFT, insertwidth=2)
    Find_Student_entry.focus()
    Find_Student_entry.place(relx=0.4, rely=0.3)

    img = Image.open("Search1.png")
    img = img.resize((300, 75), Image.ANTIALIAS)
    Search_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=Search_photo, bg="powder blue")

    Search_button = Button(frame_Find_student_body, image=Search_photo, command=Search_Student, bd=0, bg="powder blue")
    Search_button.place(relx=0.4, rely=0.46)




def Deposite_Fee_Body():
    global logout_photo, Home_photo, register_photo,deposite_photo,Submit_photo
    Rool_value, Remaining_Fee_value, Amount_value = StringVar(), StringVar(), StringVar()

    class Check_Remaining_Fee(Exception):
        def __init__(self, value):
            self.value = value

    def logout():
        frame_Deposite_Fee_Body.destroy()
        main_body()

    def Home():
        frame_Deposite_Fee_Body.destroy()
        login_body()

    global check
    check = 0
    def Update_Remaining_Fee():
        global check
        check = 1
        con = sql.connect(database="Student_db.sqlite")
        cursor = con.cursor()
        try:
            y = Rool_value.get()
            if len(y) == 0:
                raise Exception
            cursor.execute(f"SELECT Balance from Student WHERE Std_Id = '{y}'")
            Balamce = cursor.fetchone()
            Remaining_Fee_value.set(f"{Balamce[0]}")
        except:
            ms.showwarning("Warning","Please Enter Student Registeration Id bofore Pressing Submit button")



    def Deposit_Fee_DB():
        con = sql.connect(database="Student_db.sqlite")
        cursor = con.cursor()
        try:
            cursor.execute(f"SELECT Balance from Student WHERE Std_Id = '{Rool_value.get()}'")
            balance = cursor.fetchone()
            if int(Amount_value.get()) > int(balance[0]):
                raise Exception
            balance = int(balance[0]) - int(Amount_value.get())
            if check == 0:
                raise Check_Remaining_Fee("Please Click To Submit Button To Check Remaining Fee Before Dopositing Remaining Amount")
            cursor.execute(f"UPDATE Student SET Balance = {balance} WHERE Std_Id = {Rool_value.get()}")
            con.commit()
            ms.showinfo("",f"Fee Deposited Successfully, Now your remaining balance is {balance}")
            # Remaining_Fee_entry.configure(state = 'active')
            Remaining_Fee_value.set(f"{balance}")
            Remaining_Fee_entry.configure(state='disabled')
        except Check_Remaining_Fee as C:
            ms.showwarning("Warning ",f"{C}")
        except Exception as e:

            ms.showwarning("Warning",f"Something Is Going Wrong  {e}")
        finally:
            con.close()


    frame_Deposite_Fee_Body = Frame(root)
    frame_Deposite_Fee_Body.configure(bg="powder blue")
    frame_Deposite_Fee_Body.place(x=0, rely=0.2, relwidth=1, relheight=.8)

    frame_admin_welcome = Frame(frame_Deposite_Fee_Body)
    frame_admin_welcome.configure(relief=SUNKEN, bg="#f79c96")
    frame_admin_welcome.place(relx=0.0001, rely=0.001, relwidth=0.23, relheight=.1)

    label = Label(frame_admin_welcome, text="Welcome Admin", font=('comicsansms', 25, 'bold'), bg="#f79c96")
    label.pack(anchor=CENTER)

    img = Image.open("logout.png")
    img = img.resize((200, 60), Image.ANTIALIAS)
    logout_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=logout_photo, bg="powder blue")

    logout_button = Button(frame_Deposite_Fee_Body, image=logout_photo, command=logout, bd=0, bg="powder blue")
    logout_button.place(relx=0.85, rely=0.002)

    img = Image.open("home6.png")
    img = img.resize((80, 60), Image.ANTIALIAS)
    Home_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=Home_photo, bg="powder blue")

    Home_button = Button(frame_Deposite_Fee_Body, image=Home_photo, command=Home, bd=0, bg="powder blue")
    Home_button.place(relx=0.78, rely=0.002)

    # Sub register frame  and  login buttons

    frame_sub_Deposite_Fee_Body = Frame(frame_Deposite_Fee_Body)
    frame_sub_Deposite_Fee_Body.configure(bd=5, relief=GROOVE)
    frame_sub_Deposite_Fee_Body.place(relx=0.245, rely=0.22, relwidth=0.52, relheight=0.5)

    Student_Roll_label = Label(frame_sub_Deposite_Fee_Body, fg="darkblue", text="Student Reg id :",font=('comicsansms', 25, 'bold'))
    Student_Roll_label.place(relx=0.02, rely=0.1)
    Student_Remaining_Fee_label = Label(frame_sub_Deposite_Fee_Body, fg="darkblue", text="Remaining Fee :",font=('comicsansms', 25, 'bold'))
    Student_Remaining_Fee_label.place(relx=0.02, rely=0.4)
    Student_Amount_label = Label(frame_sub_Deposite_Fee_Body, fg="darkblue", text="Deposite Amn :",font=('comicsansms', 25, 'bold'))
    Student_Amount_label.place(relx=0.02, rely=0.7)



    Roll_entry = Entry(frame_sub_Deposite_Fee_Body, textvariable=Rool_value, width=25, bd=5,font="large_font 20", justify=LEFT, insertwidth=2)
    Roll_entry.focus()
    Roll_entry.place(relx=0.4, rely=0.1)

    # connectivity to sqlite
    con = sql.connect(database="Student_db.sqlite")
    cursor = con.cursor()
    cursor.execute(f"SELECT Balance from Student WHERE Std_Id = '{Rool_value.get()}'")
    x = cursor.fetchone()

    x = Rool_value.get()
    # Remaining_Fee_value.set()


    Remaining_Fee_entry = Entry(frame_sub_Deposite_Fee_Body, textvariable=Remaining_Fee_value,state = DISABLED, width=25, bd=5, font="large_font 20",justify=LEFT, insertwidth=2)
    Remaining_Fee_entry.place(relx=0.4, rely=0.4)
    Amount_entry= Entry(frame_sub_Deposite_Fee_Body, textvariable=Amount_value, width=25, bd=5, font="large_font 20",justify=LEFT, insertwidth=2)
    Amount_entry.place(relx=0.4, rely=0.7)


    img = Image.open("deposte.png")
    img = img.resize((250, 80), Image.ANTIALIAS)
    deposite_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=deposite_photo, bg="powder blue")

    Deposite_button = Button(frame_Deposite_Fee_Body, image=deposite_photo, command=Deposit_Fee_DB, bd=0, bg="powder blue")
    Deposite_button.place(relx=0.42, rely=0.77)

    img = Image.open("submit.png")
    img = img.resize((200, 60), Image.ANTIALIAS)
    Submit_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=Submit_photo, bg="powder blue")

    Deposite_button = Button(frame_Deposite_Fee_Body, image=Submit_photo, command=Update_Remaining_Fee, bd=0, bg="powder blue")
    Deposite_button.place(relx=0.77, rely=0.27)




def Add_Course_Body():

    global logout_photo, Home_photo, register_photo, deposite_photo

    def logout():
        frame_Add_Course_Body.destroy()
        main_body()

    def Home():
        frame_Add_Course_Body.destroy()
        login_body()

    def add_course_db():

        n = Course_Nmae_value.get()
        f = Course_Fee_value.get()
        try :
            if len(n) == 0 or len(f) == 0:
                raise Exception
        except:
            ms.showwarning("void", "Please Enter Record, Empty record can't be inserted  ")

        else:
            try:
                if n.isdigit():
                    raise Exception
                n,f = str(n),int(f)
                n = n.upper()
            except:
                ms.showwarning("Invalid", "Course Name Should be String type and Course Fee Should be integer type")
            else:
                con = sql.connect(database="Student_db.sqlite")
                cursor = con.cursor()
                try:
                    cursor.execute("insert into course values (?,?)",(n,f))
                    con.commit()
                    ms.showinfo("","Course Added Successfully")
                except:
                    ms.showwarning("Duplicate","Course Already exist ")
                con.close()



    frame_Add_Course_Body = Frame(root)
    frame_Add_Course_Body.configure(bg="powder blue")
    frame_Add_Course_Body.place(x=0, rely=0.2, relwidth=1, relheight=.8)

    frame_admin_welcome = Frame(frame_Add_Course_Body)
    frame_admin_welcome.configure(relief=SUNKEN, bg="#f79c96")
    frame_admin_welcome.place(relx=0.0001, rely=0.001, relwidth=0.23, relheight=.1)

    label = Label(frame_admin_welcome, text="Welcome Admin", font=('comicsansms', 25, 'bold'), bg="#f79c96")
    label.pack(anchor=CENTER)

    img = Image.open("logout.png")
    img = img.resize((200, 60), Image.ANTIALIAS)
    logout_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=logout_photo, bg="powder blue")

    logout_button = Button(frame_Add_Course_Body, image=logout_photo, command=logout, bd=0, bg="powder blue")
    logout_button.place(relx=0.85, rely=0.002)

    img = Image.open("home6.png")
    img = img.resize((80, 60), Image.ANTIALIAS)
    Home_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=Home_photo, bg="powder blue")

    Home_button = Button(frame_Add_Course_Body, image=Home_photo, command=Home, bd=0, bg="powder blue")
    Home_button.place(relx=0.78, rely=0.002)

    # Sub register frame  and  login buttons

    frame_sub_Add_Course_Body = Frame(frame_Add_Course_Body)
    frame_sub_Add_Course_Body.configure(bd=5, relief=GROOVE)
    frame_sub_Add_Course_Body.place(relx=0.245, rely=0.25, relwidth=0.52, relheight=0.4)

    Course_Name_label = Label(frame_sub_Add_Course_Body, fg="darkblue", text="Course Name :",font=('comicsansms', 25, 'bold'))
    Course_Name_label.place(relx=0.02, rely=0.2)
    Course_Fee_label = Label(frame_sub_Add_Course_Body, fg="darkblue", text="Course Fee :",font=('comicsansms', 25, 'bold'))
    Course_Fee_label.place(relx=0.02, rely=0.6)

    Course_Nmae_value, Course_Fee_value = StringVar(), StringVar()

    Course_Name_entry = Entry(frame_sub_Add_Course_Body, textvariable=Course_Nmae_value, width=25, bd=5, font="large_font 20",justify=LEFT, insertwidth=2)
    Course_Name_entry.focus()
    Course_Name_entry.place(relx=0.4, rely=0.2)
    Course_Fee_entry = Entry(frame_sub_Add_Course_Body, textvariable=Course_Fee_value, width=25, bd=5,font="large_font 20", justify=LEFT, insertwidth=2)
    Course_Fee_entry.place(relx=0.4, rely=0.6)

    img = Image.open("add.png")
    img = img.resize((250, 80), Image.ANTIALIAS)
    deposite_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=deposite_photo, bg="powder blue")

    Deposite_button = Button(frame_Add_Course_Body, image=deposite_photo, command= add_course_db , bd=0, bg="powder blue")
    Deposite_button.place(relx=0.39, rely=0.75)


def Update_Course_Body():
    global logout_photo, Home_photo, register_photo, deposite_photo,Update_photo

    class Course_Not_Exist_Error(Exception):
        def __init__(self, value):
            self.value = value

    def logout():
        frame_Update_Course_Body.destroy()
        main_body()

    def Home():
        frame_Update_Course_Body.destroy()
        login_body()

    def Update_Fee_DB():
        count = 0
        con = sql.connect(database="Student_db.sqlite")
        cursor = con.cursor()
        course = Course_Name_entry.get()
        course_fee = Course_Fee_entry.get()

        try:
            course = course.upper()
            print(course)
            course_fee = int(course_fee)
            cursor.execute("select Course_Name from Course")
            for i in cursor.fetchall():
                if i[0] != course:
                    pass
                else:
                    count += 1
            if count != 1:
                raise Course_Not_Exist_Error("Course does not exist")
            cursor.execute(f"Update Course Set Course_fee = {course_fee} Where Course_Name = '{course}'")
            con.commit()
            ms.showinfo("","Change Successfully")
        except Course_Not_Exist_Error as C:
            ms.showwarning("Warning",f"{C}")
        except Exception as e:
            ms.showwarning("Warning",f"Something is going wrong, {e} ")
        finally:
            con.close()








    frame_Update_Course_Body = Frame(root)
    frame_Update_Course_Body.configure(bg="powder blue")
    frame_Update_Course_Body.place(x=0, rely=0.2, relwidth=1, relheight=.8)

    frame_admin_welcome = Frame(frame_Update_Course_Body)
    frame_admin_welcome.configure(relief=SUNKEN, bg="#f79c96")
    frame_admin_welcome.place(relx=0.0001, rely=0.001, relwidth=0.23, relheight=.1)

    label = Label(frame_admin_welcome, text="Welcome Admin", font=('comicsansms', 25, 'bold'), bg="#f79c96")
    label.pack(anchor=CENTER)

    img = Image.open("logout.png")
    img = img.resize((200, 60), Image.ANTIALIAS)
    logout_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=logout_photo, bg="powder blue")

    logout_button = Button(frame_Update_Course_Body, image=logout_photo, command=logout, bd=0, bg="powder blue")
    logout_button.place(relx=0.85, rely=0.002)

    img = Image.open("home6.png")
    img = img.resize((80, 60), Image.ANTIALIAS)
    Home_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=Home_photo, bg="powder blue")

    Home_button = Button(frame_Update_Course_Body, image=Home_photo, command=Home, bd=0, bg="powder blue")
    Home_button.place(relx=0.78, rely=0.002)

    # Sub register frame  and  login buttons

    frame_sub_Update_Course_Body = Frame(frame_Update_Course_Body)
    frame_sub_Update_Course_Body.configure(bd=5, relief=GROOVE)
    frame_sub_Update_Course_Body.place(relx=0.245, rely=0.25, relwidth=0.52, relheight=0.4)
    Course_Name_label = Label(frame_sub_Update_Course_Body, fg="darkblue", text="Course Name :",font=('comicsansms', 25, 'bold'))
    Course_Name_label.place(relx=0.02, rely=0.2)
    Course_Fee_label = Label(frame_sub_Update_Course_Body, fg="darkblue", text="Course Fee :",font=('comicsansms', 25, 'bold'))
    Course_Fee_label.place(relx=0.02, rely=0.6)
    Course_Name_value, Course_Fee_value = StringVar(), StringVar()
    Course_Name_entry = Entry(frame_sub_Update_Course_Body, textvariable=Course_Name_value, width=25, bd=5, font="large_font 20",justify=LEFT, insertwidth=2)
    Course_Name_entry.focus()
    Course_Name_entry.place(relx=0.4, rely=0.2)
    Course_Fee_entry = Entry(frame_sub_Update_Course_Body, textvariable=Course_Fee_value, width=25, bd=5,font="large_font 20", justify=LEFT, insertwidth=2)

    Course_Fee_entry.place(relx=0.4, rely=0.6)

    img = Image.open("Update.png")
    img = img.resize((250, 80), Image.ANTIALIAS)
    Update_photo = ImageTk.PhotoImage(img)
    img_label = Label(frame_body, image=Update_photo, bg="powder blue")

    Update_button = Button(frame_Update_Course_Body, image=Update_photo, command=Update_Fee_DB, bd=0, bg="powder blue")
    Update_button.place(relx=0.42, rely=0.75)











main_body()













root.mainloop()
