# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk
import tkinter.filedialog
import random
import socket
from PIL import ImageTk, Image
import threading
import ast
import sys
import sqlite3
import re
from validate_email import validate_email
import time

CryptoImage1 = None
client_socket = None
length_original = 0
root = None
canvas = None
E1 = None
E2 = None
B1 = None
B2 = None
B3 = None
B4 = None
lbl1 = None
QuestionSubject = None
ButtonsList = None
root = None
validate_email_answer = None


def email_check(root):
    # Check if the email exists
    global E1
    global B1
    global B2
    global B3
    global lbl1
    global client_socket
    global validate_email_answer
    email_addr = root.E1.get()
    try:
        root.lbl1.pack_forget()
        root.prog.pack_forget()
    except:
        pass

    match = re.match(r'([\w\.-]+)@([\w\.-]+)(\.[\w\.]+)', email_addr)
    # \w	Returns a match where the string contains any word characters
    #  +    Matches 1 or more occurrence of preceding expression.
    # []    Set of characters that you wish to match. 
    # ()    Group together the expressions contained inside them.
    #  \    Remove the special meaning of a character ('.' in our case).
    #  +    Matches one or more times.
    root.lbl1 = Label(root, text="The program checks email address's validation. Please wait.", width=200)
    root.lbl1.pack(padx=40)
    root.update()
    try:
        if (match != None):
            progress_bar(root, email_addr)
        else:
            root.lbl1.config(text="Email Address Syntax Error. Enter again.")
    except:
        print ("Unexpected Server Error 2.")
        close(root)

    
def thread_func2(email_addr):
    t2 = threading.Thread(target=validation, args=(email_addr,))
    t2.start()

    
def validation(email_addr):
    global validate_email_answer
    if (validate_email(email_addr, check_mx=True, verify=True, smtp_timeout=60)):
        validate_email_answer = True
    else:
        validate_email_answer = False
    

def progress_bar(root, email_addr):
    thread_func2(email_addr)
    root.prog = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    root.prog.pack(pady=5)
    start_progress(root, email_addr)

    
def start_progress(root, email_addr):
    global validate_email_answer
    global client_socket
    for i in range(100):
        time.sleep(0.4)
        root.prog["value"] = i
        root.prog.update()
    if validate_email_answer is False:
        root.lbl1.config(text="Not an Existing Email Address Error. Enter again.")
    else:
        client_socket.send(email_addr.encode())
        msg = client_socket.recv(1024)
        msg = msg.decode()
        if msg == 'Ok':
            root.lbl1.config(text="Image 'out2.jpg' sent to your email! Please check inbox and attach the image.")
            root.prog.pack_forget()
            root.B1.config(state=DISABLED)
            root.B2.config(state=NORMAL)
            root.B3.config(state=NORMAL)
        else:
            root.lbl1.config(text="Already Participated Error. Enter another email or log out.")
        

def tkGUI(root):
    global E1
    global E2
    global B1
    global B2
    global B3
    global B4
    global CryptoImage1
    global length_original
    
    root.title('Elections Opening Screen')
    root.geometry('600x700+600+25')
    root.configure(background='#c9b3bf')

    root.lbl = Label(root,
                     text='To Vote in the Elections, Please Enter Email Address:'
                     , width=200)
    root.lbl.pack(pady=10, padx=40)

    root.E1 = Entry(root, bd=5, width=50)
    root.E1.pack(pady=0, padx=100)

    root.B1 = Button(root, text='Submit Email', bd=5, width=50,
                     command=lambda:email_check(root))
    root.B1.pack(pady=0, padx=100)

    root.B2 = Button(
        root,
        text="Get Cryptography's Image 1",
        bd=5,
        width=50,
        command=lambda:browser(root),
        state=DISABLED,
        )
    root.B2.pack(pady=0, padx=100)

    global canvas
    root.canvas = Canvas(root, width=300, height=300)
    root.canvas.pack(pady=10)

    PhotoImage(width=150, height=150)
    img = ImageTk.PhotoImage(CryptoImage1, int(length_original))
    root.canvas.create_image(0, 0, anchor=NW, image=img)

    root.L1 = Label(root, text='Password:', width=50)
    root.L1.pack(pady=10, padx=100)

    root.E2 = Entry(root, bd=5, width=10)
    root.E2.pack(pady=0, padx=100)

    root.B3 = Button(
        root,
        text='Submit',
        bd=5,
        width=50,
        command=lambda:thread_func1(root),
        state=DISABLED,
        )
    root.B3.pack(pady=0, padx=105)

    root.B4 = Button(
        root,
        text='Vote',
        bd=5,
        width=50,
        command=lambda:after_func2(root),
        state=DISABLED,
        )
    root.B4.pack(pady=0, padx=105)

    root.B5 = Button(root, text='Close', bd=5, width=50,
                     command=lambda:close(root))
    root.B5.pack(pady=10, padx=105)

    root.mainloop()


def Show(infile2):
    global CryptoImage1
    infile1 = CryptoImage1

    outfile = Image.new('1', infile1.size)

    for x in range(infile1.size[0]):
        for y in range(infile1.size[1]):
            outfile.putpixel((x, y), max(infile1.getpixel((x, y)),
                             infile2.getpixel((x, y))))

    outfile.save(r'out.jpg')


def browser(root):
    ImageFile = ""
    while True:
        if (ImageFile == "" or ImageFile[-4:] != ".jpg"):
            Tk().withdraw()
            ImageFile = tkinter.filedialog.askopenfilename()
        else:
            break
    global canvas

    Show(Image.open(ImageFile))
    infile = open(r'out.jpg', 'rb')
    PhotoImage(width=300, height=300)
    img = ImageTk.PhotoImage(Image.open(infile))
    root.canvas.create_image(0, 0, anchor=NW, image=img)
    infile.close()
    root.mainloop()


def socket_func():
    global E1
    global CryptoImage1
    global length_original
    global client_socket

    PORT = 8000
    IP = '127.0.0.1'

    # Checks connection
    try:
        socket.create_connection(("www.google.com", 80))
    except:
        print('No Connection error. Try again later.')
        sys.exit()

    client_socket = socket.socket()
    try:
        client_socket.connect((IP, int(PORT)))
        try:
            newfile = open('CryptoImage1.jpg', 'wb')
            length = client_socket.recv(1024)
            length = int(length.decode())
            data = client_socket.recv(1024)
            newfile.write(data)
            length -= len(data)
            try:
                while length != 0:
                    try:
                        data = client_socket.recv(1024)
                        newfile.write(data)
                        length -= len(data)
                    except:
                        break
            except:
                print('Reciving error. Try again later. Please check wheather the server is running.')
                sys.exit()
            newfile.close()
            CryptoImage1 = Image.open('CryptoImage1.jpg')
        except:
            print('Reciving error. Try again later. Please check wheather the server is running.')
            sys.exit()
    except:
        print('Connection error. Try again later. Please check wheather the server is running.')
        sys.exit()
    after_func1()

   
def after_func1():
    root = Tk()
    root.after(1000, tkGUI(root))


def voting_details(root):
    global E2
    global client_socket
    global QuestionSubject
    global ButtonsList
    global B4
    global B3

    password_from_entry = root.E2.get()
    client_socket.send(password_from_entry.encode())
    try:
        msg = client_socket.recv(1024)
        msg = msg.decode()
        if msg == 'Ok':
            recived = client_socket.recv(1024)
            recived = recived.decode()
            recived = recived.split('?')
            QuestionSubject = recived[0] + '?'
            ButtonsList = recived[1]
            ButtonsList = ast.literal_eval(ButtonsList)
            root.B4.config(state=NORMAL)
            root.B3.config(state=DISABLED)
        else:
            # password_from_entry --> Wrong password
            try:
                root.lbl1.pack_forget()
            except:
                pass
            root.lbl2 = Label(root,
                              text='Wrong password error. Enter again. Enter Again.'
                              , width=200)
            root.lbl2.pack(padx=40)
    except:
        print ("Unexpected Server Error 3.")
        close(root)


def thread_func1(root):
    t1 = threading.Thread(target=voting_details, args=(root,))
    t1.start()


def all_children(window):
    _list = window.winfo_children()

    for item in _list:
        if item.winfo_children():
            _list.extend(item.winfo_children())

    return _list


def after_func2(root):
    global QuestionSubject
    global ButtonsList
    widget_list = all_children(root)
    for item in widget_list:
        item.pack_forget()
    root.after(1000, voting(root, QuestionSubject, ButtonsList))


def voted_option(root, chosen_option):
    global client_socket
    
    try:
        client_socket.send(chosen_option.encode())
        recived = client_socket.recv(1024)
        recived = recived.decode()
        recived = recived.split('?')
        votes = recived[0]
        leader_name = recived[1]
        leader_num = recived[2]
        client_socket.close()
        root.after(1000, result(root, leader_name, chosen_option, votes,
                   leader_num))
    except:
        print ("Unexpected Server Error 1.")
        close(root)


def result(
    root,
    leader_name,
    chosen_option,
    votes,
    leader_num,
    ):
    global ButtonsList
    root.B1.config(state=DISABLED)
    root.B2.config(state=DISABLED)
    if len(ButtonsList) > 2:
        root.B3.config(state=DISABLED)
        if len(ButtonsList) == 4:
            root.B4.config(state=DISABLED)
    txt = \
        'You voted for {0}. {0} has {1} votes.'.format(chosen_option,
            votes)
    root.lbl2 = Label(root, text=txt, width=200)
    root.lbl2.pack(padx=20)
    if leader_num == votes:
        txt = \
            'Your voted option "{0}" is the leader.'.format(chosen_option,
                votes)
        root.lbl3 = Label(root, text=txt, width=200)
        root.lbl3.pack(padx=20)
    else:
        txt = 'Leader is : "{0}". with {1} votes.'.format(leader_name,
                leader_num)
        root.lbl3 = Label(root, text=txt, width=200)
        root.lbl3.pack(padx=20)
    root.B = Button(
        root,
        text='Close Program',
        bd=10,
        bg='#F7E1E4',
        relief=GROOVE,
        activeforeground='#E86F81',
        activebackground='#A60C23',
        width=50,
        height=2,
        command=lambda : close(root),
        )
    root.B.pack(pady=15, padx=100)


def close(root):
    global client_socket
    root.destroy()
    client_socket.close()
    sys.exit()


def voting(root, QuestionSubject, ButtonsList):

    root.lbl = Label(
        root,
        text=QuestionSubject,
        width=200,
        bg='#E6455B',
        relief=GROOVE,
        activeforeground='#E86F81',
        activebackground='#A60C23',
        height=2,
        )
    root.lbl.pack(pady=50, padx=40)

    root.B1 = Button(
        root,
        text=ButtonsList[0],
        bd=10,
        bg='#F7E1E4',
        relief=GROOVE,
        activeforeground='#E86F81',
        activebackground='#A60C23',
        width=50,
        height=4,
        command=lambda : voted_option(root, ButtonsList[0]),
        )
    root.B1.pack(pady=15, padx=100)
    root.B2 = Button(
        root,
        text=ButtonsList[1],
        bd=10,
        bg='#F7E1E4',
        relief=GROOVE,
        activeforeground='#E86F81',
        activebackground='#A60C23',
        width=50,
        height=4,
        command=lambda : voted_option(root, ButtonsList[1]),
        )
    root.B2.pack(pady=15, padx=100)
    if len(ButtonsList) > 2:
        root.B3 = Button(
            root,
            text=ButtonsList[2],
            bd=10,
            bg='#F7E1E4',
            relief=GROOVE,
            activeforeground='#E86F81',
            activebackground='#A60C23',
            width=50,
            height=4,
            command=lambda : voted_option(root, ButtonsList[2]),
            )
        root.B3.pack(pady=15, padx=100)
        if len(ButtonsList) == 4:
            root.B4 = Button(
                root,
                text=ButtonsList[3],
                bd=10,
                bg='#F7E1E4',
                relief=GROOVE,
                activeforeground='#E86F81',
                activebackground='#A60C23',
                width=50,
                height=4,
                command=lambda : voted_option(root, ButtonsList[3]),
                )
            root.B4.pack(pady=15, padx=100)

    root.mainloop()


def main():
    try:
        socket_func()
    except:
        sys.exit()


if __name__ == '__main__':
    main()
