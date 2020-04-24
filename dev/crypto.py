#!/usr/bin/python
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import random
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class crypto:

    def __init__(self):
        """the fuction creates a photo and splits it then to two with visual cryptography"""
        # Text_Pic
        img = Image.new('1', (150, 150), color=255)  # creates a new image sized 150x150, black&white (mode 1)
        self.txt = ''
        for i in range(6):
            self.txt += chr(random.randint(97, 122))
        ImageDraw.Draw(img).text(xy=(0, 50), text=self.txt,
                                 font=ImageFont.truetype('C:\WINDOWS\Fonts\ARLRDBD.TTF'
                                 , 37))
        img.save('source_image.jpg')


        # Generate
        # my visual cryptography works with this concept (minimum):
        # when black pixel with a black pixel merged, the output will be a black pixel
        # when white pixel and black pixels merged or white pixel and white pixel - output will be white

        image = Image.open('source_image.jpg')
        image = image.convert('1') # mode 1 turns picture to black and white only!
        # now we will create two images in mode 1- black and white
        # size will be duplicated

        out1 = Image.new('1', [dimension * 2 for dimension in
                                image.size])  # PIL.Image.new(mode, size, color=0), size is doubled
        out2 = Image.new('1', [dimension * 2 for dimension in
                                image.size])

        lists=[[255,0,255,0], [0,255,0,255]]
        for x in range(0, image.size[0]): # a loop from 0 to the x of the image
           for y in range(0, image.size[1]): # a loop from 0 to the y of the image
                pixel=image.getpixel((x,y)) # loops - for each x all the ys
                pattern=random.choice(lists) #Return a random list from the list of pattern lists
                if pixel==0: # if the pixel is black the pixel splits by the random pattern with an anti pattern
                     out1.putpixel((x * 2, y * 2), pattern[0])
                     out1.putpixel((x * 2 + 1, y * 2), pattern[1])
                     out1.putpixel((x * 2, y * 2 + 1), pattern[2])
                     out1.putpixel((x * 2 + 1, y * 2 + 1), pattern[3])
                     
                     out2.putpixel((x * 2, y * 2), 255-pattern[0])
                     out2.putpixel((x * 2 + 1, y * 2), 255-pattern[1])
                     out2.putpixel((x * 2, y * 2 + 1), 255-pattern[2])
                     out2.putpixel((x * 2 + 1, y * 2 + 1), 255-pattern[3])
                else: # if the pixel is white the pixel splits by the random pattern with the same pattern
                     out1.putpixel((x * 2, y * 2), pattern[0])
                     out1.putpixel((x * 2 + 1, y * 2), pattern[1])
                     out1.putpixel((x * 2, y * 2 + 1), pattern[2])
                     out1.putpixel((x * 2 + 1, y * 2 + 1), pattern[3])
                     
                     out2.putpixel((x * 2, y * 2), pattern[0])
                     out2.putpixel((x * 2 + 1, y * 2), pattern[1])
                     out2.putpixel((x * 2, y * 2 + 1), pattern[2])
                     out2.putpixel((x * 2 + 1, y * 2 + 1), pattern[3])


        # pictures saved

        out1.save(r'out1.jpg')
        out2.save('out2.jpg')


    def GetPassword(self):
        return self.txt


    def GetPicture(self):
        with open(r'out1.jpg', 'rb') as infile1:
            infile_read = infile1.read()
        infile1.close()
        return infile_read


    def Send_Out2_By_Email(self, email_addr):
        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = 587
        content = MIMEMultipart()
        content['From'] = 'CREATE_AN_EMAIL@gmail.com'
        content['To'] = email_addr
        content['Subject'] = 'Password First Picture'
        content.attach(MIMEText('Here is the first picture of the password:'
                       , 'plain'))
        filename = 'out2.jpg'
        attachment = open(filename, 'rb')

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename= '
                        + filename)

        content.attach(part)
        content = content.as_string()
        mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        mail.starttls()
        mail.login('CREATE_AN_EMAIL@gmail.com', 'YOUR CREATED EMAIL"S PASSWORD')

        # To run the project you have to create an email (or use an existing one)
        # The email will send the out2.jpg file to the client
        try:
            mail.sendmail('CREATE_AN_EMAIL@gmail.com', [email_addr], content)
        except:
            print ("Unexpected Client Error 1.")
