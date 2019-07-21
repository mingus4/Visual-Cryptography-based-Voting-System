#!/usr/bin/python
# -*- coding: utf-8 -*-

from tkinter import *
from crypto import *
import tkinter.filedialog
import socket
from PIL import ImageTk, Image
import socket  # Import socket module
import threading
import sqlite3
import os
import sys

root = None
canvas = None
B3 = None
B4 = None
ButtonsList = None
ClientsList = [] # list of clients created so I'd be able to close connection any time
server_socket = None
dict2 = {}


def on_new_client(client_socket, addr, dict, QuestionSubject):
    global dict2
    user_email_addr = None
    global ClientsList
    ClientsList.append(client_socket)
    for i in list(dict.keys()):
        dict[i] = 0
    global ButtonsList
    classobject = crypto()
    image1 = classobject.GetPicture()

    client_socket.send(str(len(image1)).encode('utf-8').strip())
    while len(image1) > 0:
        client_socket.send(image1[:1024])
        image1 = image1[1024:]

    conn = sqlite3.connect('elections_results.db')
    try:
        while True:
            user_email_addr = client_socket.recv(1024)
            user_email_addr = user_email_addr.decode()

            cursor = conn.execute('SELECT email from votes')
            found = False
            for i in cursor:
                if user_email_addr in i:
                    found = True
            if found:
                client_socket.send('Not Valid'.encode())
            else:
                client_socket.send('Ok'.encode())
                break
        # Prevent same person same time registration
        conn.execute('INSERT INTO votes(email,vote) VALUES (?,?)',
                     (user_email_addr, ""))
        conn.commit()
        classobject.Send_Out2_By_Email(user_email_addr)

        password_from_crypto = classobject.GetPassword()

        while True:
            password_from_entry = client_socket.recv(1024)
            password_from_entry = password_from_entry.decode()
            if password_from_entry != password_from_crypto:
                client_socket.send('Wrong Password'.encode())
            else:
                client_socket.send('Ok'.encode())
                client_socket.send((QuestionSubject + '?' + str(ButtonsList)).encode())
                break

        voted_option = client_socket.recv(1024)
        voted_option = voted_option.decode()
        conn.execute("DELETE FROM votes WHERE (email,vote) = (?, ?)", (user_email_addr, ""))
        conn.commit()
        conn.execute('INSERT INTO votes(email,vote) VALUES (?, ?)',
                     (user_email_addr, voted_option))
        conn.commit()

        # find value's number of votes:

        cursor = conn.execute('SELECT vote from votes')
        conn.commit()
        for i in cursor:
            if ButtonsList[0] in i:
                dict[ButtonsList[0]] += 1
            elif ButtonsList[1] in i:
                dict[ButtonsList[1]] += 1
            elif len(ButtonsList) > 2:
                if ButtonsList[2] in i:
                    dict[ButtonsList[2]] += 1
                    if len(ButtonsList) == 4:
                        if ButtonsList[3] in i:
                            dict[ButtonsList[3]] += 1
        dict2 = dict
        conn.close()

        leader_name = ButtonsList[0]
        leader_num = dict[ButtonsList[0]]
        if leader_num < dict[ButtonsList[1]]:
            leader_name = ButtonsList[1]
            leader_num = dict[ButtonsList[1]]
        if len(ButtonsList) > 2:
            if leader_num < dict[ButtonsList[2]]:
                leader_name = ButtonsList[2]
                leader_num = dict[ButtonsList[2]]
                if len(ButtonsList) == 4:
                    if leader_num < dict[ButtonsList[3]]:
                        leader_name = ButtonsList[3]
                        leader_num = dict[ButtonsList[3]]
        if voted_option == leader_name:  # tie case in which the voted option leading
            txt = str(dict[voted_option]) + '?' + voted_option + '?' \
                + str(leader_num)
            client_socket.send((str(dict[voted_option]) + '?' + voted_option
                               + '?' + str(leader_num)).encode())
        else:
            txt = str(dict[voted_option]) + '?' + leader_name + '?' \
                + str(leader_num)
            client_socket.send((str(dict[voted_option]) + '?' + leader_name
                               + '?' + str(leader_num)).encode())
        client_socket.close()
    except:
        if (user_email_addr != None):
            try:    
                conn.execute("DELETE FROM votes WHERE (email,vote) = (?, ?)", (user_email_addr, ""))
                conn.commit()
            except:
                pass
        print ("Unexpected Client Error 2.")


def server_open(entry_1, entry_2, entry_3, entry_4, QuestionSubject):
    server_socket = socket.socket()  # Create a socket object
    PORT = 8000
    IP = '127.0.0.1' 
    
    global B4
    global ButtonsList

    if os.path.isfile('elections_results.db'):
        os.remove('elections_results.db')
    conn = sqlite3.connect('elections_results.db')
    conn.execute('CREATE TABLE votes(email TEXT, vote TEXT)')
    conn.commit()
    conn.close()

    # SQLite objects created in a thread can only be used in that same thread.
    # Therefore, I have to close the connection and open it again in each thread.

    dict = {}
    ButtonsList = [entry_1, entry_2]
    dict = {ButtonsList[0]: 0, ButtonsList[1]: 0}
    if entry_3 != '':
        ButtonsList.append(entry_3)
        dict[ButtonsList[2]] = 0
    if entry_4 != '':
        ButtonsList.append(entry_4)
        dict[ButtonsList[3]] = 0

    print('Server started!')
    print('Waiting for clients...')
    server_socket.bind((IP, PORT))  # Bind to the port
    server_socket.listen(5000)  # Maximum 5 same-time connections
    while True:
        try:
            (client_socket, addr) = server_socket.accept()  # Establish connection with client.
            print(('Got connection from', addr))
            thread_func = threading.Thread(target=on_new_client,
                    args=(client_socket, addr, dict, QuestionSubject))
            thread_func.start()
        except:
            if (client_socket != None):
                client_socket.close()
            continue

        # that's how you pass arguments to functions when creating new threads using thread module
    server_socket.close()


def thread_func1(root):
    try:
        root.lbl4.pack_forget()
    except:
        pass
    global B3
    entry_1 = root.E1.get()
    entry_2 = root.E2.get()
    entry_3 = root.E3.get()
    entry_4 = root.E4.get()
    QuestionSubject = root.E5.get()
    if ((QuestionSubject != '') and (entry_1 != '') and (entry_2 != '')):
        if entry_4 != '' and entry_3 == '':
            root.lbl4 = Label(root,
                         text='Error. Enter again. Fill entries by order!'
                         , width=210)
            root.lbl4.pack(padx=40)
        elif ('?' in QuestionSubject):
            root.lbl4 = Label(root,
                     text='Question Mark Error. Enter again.  No question marks in question !'
                     , width=210)
            root.lbl4.pack(padx=40)
        elif entry_1 != '' and entry_1 == entry_2:
            root.lbl4 = Label(root,
                     text='Duplicates Error. Enter again. Fill entries differently !'
                     , width=210)
            root.lbl4.pack(padx=40)
        elif entry_1 != '' and entry_1 == entry_3:
            root.lbl4 = Label(root,
                     text='Duplicates Error. Enter again. Fill entries differently !'
                     , width=210)
            root.lbl4.pack(padx=40)
        elif entry_1 != '' and entry_1 == entry_4:
            root.lbl4 = Label(root,
                     text='Duplicates Error. Enter again. Fill entries differently !'
                     , width=210)
            root.lbl4.pack(padx=40)
        elif entry_2 != '' and entry_2 == entry_3:
            root.lbl4 = Label(root,
                     text='Duplicates Error. Enter again. Fill entries differently !'
                     , width=210)
            root.lbl4.pack(padx=40)
        elif entry_2 != '' and entry_2 == entry_4:
            root.lbl4 = Label(root,
                     text='Duplicates Error. Enter again. Fill entries differently !'
                     , width=210)
            root.lbl4.pack(padx=40)
        elif entry_3 != '' and entry_3 == entry_4:
            root.lbl4 = Label(root,
                     text='Duplicates Error. Enter again. Fill entries differently !'
                     , width=210)
            root.lbl4.pack(padx=40)
        else:
            root.B3.config(state=DISABLED)
            try:
                root.lbl4.pack_forget()
            except:
                pass
            try:
                t1 = threading.Thread(target=lambda:server_open(entry_1, entry_2, entry_3, entry_4, QuestionSubject))
                t1.daemon = True
                # The thread is daemon so we won't need to keep track of it.
                # By setting a thread as daemon thread, we can let it run and when program quits, the daemon thread will be killed automatically.
                t1.start()
            except:
                print
    else:
        root.lbl4 = Label(root,
                     text='Error. Enter again. Fill question and atleast 2 entries!'
                     , width=210)
        root.lbl4.pack(padx=40)


def tkGUI(root):
    global B3

    root.title('Elections Server')
    root.geometry('500x700+200+30')
    root.configure(background='#c9b3bf')

    root.lbl1 = Label(root,
                 text='To Start the Server, fill the entries by order. Then press submit'
                 , width=210)
    root.lbl1.pack(pady=30, padx=40)

    root.lbl2 = Label(root,
                 text='Enter Question Subject [without a question mark !]'
                 , bd=5, width=50)
    root.lbl2.pack(pady=10, padx=100)

    root.E5 = Entry(root, bd=5, width=50)
    root.E5.pack(pady=10, padx=100)

    root.lbl3 = Label(root,
                 text='Fill Atleast 2 Buttons; Unfilled will Not Appear'
                 , bd=5, width=50)
    root.lbl3.pack(pady=10, padx=100)

    root.E1 = Entry(root, bd=5, width=50)
    root.E1.pack(padx=100)
    root.E2 = Entry(root, bd=5, width=50)
    root.E2.pack(padx=100)
    root.E3 = Entry(root, bd=5, width=50)
    root.E3.pack(padx=100)
    root.E4 = Entry(root, bd=5, width=50)
    root.E4.pack(padx=100)
    
    root.B3 = Button(root, text='Submit', bd=5, width=50,
                command=lambda:thread_func1(root))
    root.B3.pack(pady=10, padx=100)

    root.B4 = Button(root, text='Results', bd=5, width=50,
                command=lambda:voting_results(root))
    root.B4.pack(pady=0, padx=100)
    
    root.B5 = Button(root, text='Close', bd=5, width=50,
                command=lambda:close(root))
    root.B5.pack(pady=0, padx=100)

    root.mainloop()


def voting_results(root):
    try:
        root.lbl8.pack_forget()
        root.lbl5.pack_forget()
        root.lbl6.pack_forget()
        root.lbl7.pack_forget()
    except:
        pass
    global dict2
    print (dict2)
    if dict2 != {}:
        root.lbl8 = Label(root,
                     text='{0} got {1} votes.'.format(list(dict2.keys())[0],
                     dict2[list(dict2.keys())[0]]), bd=5, width=50)
        root.lbl8.pack(pady=5, padx=100)
        root.lbl5 = Label(root,
                     text='{0} got {1} votes.'.format(list(dict2.keys())[1],
                     dict2[list(dict2.keys())[1]]), bd=5, width=50)
        root.lbl5.pack(pady=5, padx=100)
        if len(list(dict2.keys())) > 2:
            root.lbl6 = Label(root,
                         text='{0} got {1} votes.'.format(list(dict2.keys())[2],
                         dict2[list(dict2.keys())[2]]), bd=5, width=50)
            root.lbl6.pack(pady=5, padx=100)
            if len(list(dict2.keys())) == 4:
                root.lbl7 = Label(root,
                             text='{0} got {1} votes.'.format(list(dict2.keys())[3],
                             dict2[list(dict2.keys())[3]]), bd=5,
                             width=50)
                root.lbl7.pack(pady=5, padx=100)
    else:
        root.lbl8 = Label(root, text='There were no votes yet.', bd=5,
                     width=50)
        root.lbl8.pack(pady=10, padx=100)


def after_func1():
    # Checks connection
    try:
        socket.create_connection(("www.google.com", 80))
    except:
        print('No Connection error. Try again later.')
        sys.exit()
    root = Tk()
    try:
        root.after(1000, tkGUI(root))
    except:
        sys.exit()


def close(root):
    global ClientsList
    global server_socket
    for i in ClientsList:
        i.close()
    root.destroy()
    if (server_socket != None):
        server_socket.close()
    sys.exit()
    
    
def main():
    try:
        after_func1()
    except:
        sys.exit()


if __name__ == '__main__':
    main()    
