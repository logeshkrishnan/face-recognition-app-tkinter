import face_recognition
import sqlite3
import cv2
from threading import Thread
from imutils.io import TempFile
import tkinter as tk
from tkinter import *
import os

# Storing the image temporarily for the pop-up window
def send(image, ref_no):
	# create a temporary path for the image and write it to file
	tempImage = TempFile()
	cv2.imwrite(tempImage.path, image)
	way = tempImage.path
	now = datetime.datetime.now()
	date = now.strftime("%d-%m-%Y")
	reference_no = ref_no

	# start a thread to upload the file and send it
	t = Thread(target=add_new_customer, args=(tempImage, way, date, reference_no, image,))
	t.daemon = True
	t.start()

# Creating pop-up window for new customer
def add_new_customer(tempImage, way, date, reference_no, image):
	master = tk.Tk()
	master.title("Cusomter list")
	master.geometry('650x900+0+0')

	conn = sqlite3.connect('customers_database.db')
	c = conn.cursor()

	fol = way
	logo_path = "assets/logo.jpg"
	bg = ImageTk.PhotoImage(Image.open(logo_path))
	upload = ImageTk.PhotoImage(Image.open(fol))
	tempImage.cleanup()

	K0 = Label(master, text="Add new customer profile", font=("arial",30,"bold"), fg="steelblue").place(x=10,y=500)
	K1 = Label(master, image = upload).place(x=10,y=10)
	k2 = Label(master, image = bg).place(x=0,y=0)
	K3 = Label(master, text="Date: {}".format(date), font=("arial", 16)).place(x=10,y=550)
	K4 = Label(master, text="Reference Number: {}".format(reference_no), font=("arial", 16)).place(x=10,y=600)
	K5 = Label(master, text="Name:", font=("arial", 16)).place(x=10,y=650)
	K6 = Label(master, text="Mobile Number:", font=("arial", 16)).place(x=10,y=700)
	K7 = Label(master, text="Email:", font=("arial", 16)).place(x=10,y=750)
	K8 = Label(master, text="Purchased Items:", font=("arial", 16)).place(x=10,y=800)

	name = StringVar(master)
	mobile_no = StringVar(master)
	email = StringVar(master)
	purchased_items = StringVar(master)

	nameT = Entry(master, textvariable = name)
	nameT.place(x=200,y=660)
	mobile_noT = Entry(master, textvariable = mobile_no)
	mobile_noT.place(x=200,y=710)
	emailT = Entry(master, textvariable = email)
	emailT.place(x=200,y=760)
	purchased_itemsT = Entry(master, textvariable = purchased_items)
	purchased_itemsT.place(x=200,y=810)

	# Adding new customer details to the sqlite database
	def add_to_database():
		print("You have submitted a record")
		img_loc = "assets/img/customers/{}.jpg".format(name.get())
		cv2.imwrite(img_loc, image)

		c.execute('CREATE TABLE IF NOT EXISTS customers (date TEXT , name TEXT UNIQUE, mobile_no INTEGER UNIQUE, email TEXT UNIQUE, reference_no INTEGER PRIMARY KEY AUTOINCREMENT, img_loc TEXT)')
		c.execute('CREATE TABLE IF NOT EXISTS items (name TEXT, date TEXT, purchased_items TEXT)')
		c.execute('INSERT INTO customers (name, mobile_no, email, date, img_loc) VALUES (?, ?, ?, ?, ?)',(name.get(), mobile_no.get(), email.get(), date, img_loc))
		c.execute('INSERT INTO items (name, date, purchased_items) VALUES (?, ?, ?)', (name.get(), date, purchased_items.get()))
		conn.commit()

		name.set('')
		mobile_no.set('')
		email.set('')
		print("Record submitted successfully")
		master.destroy()

	V1 = Button(master, text='Submit', command=add_to_database).place(x=10,y=850)
	V2 = Button(master, text='Cancel', command=master.quit).place(x=300,y=850)
	master.mainloop()

# Declare all the list
known_face_encodings = []
known_face_names = []
known_faces_filenames = []

# Walk in the folder to add every file name to known_faces_filenames
for (dirpath, dirnames, filenames) in os.walk('assets/img/customers/'):
    known_faces_filenames.extend(filenames)
    break

# Walk in the folder
for filename in known_faces_filenames:
    # Load each file
    face = face_recognition.load_image_file('assets/img/customers/' + filename)
    # Extract the name of each employee and add it to known_face_names
    known_face_names.append(re.sub("[0-9]",'', filename[:-4]))
    # Encode de face of every employee
    known_face_encodings.append(face_recognition.face_encodings(face)[0])

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# Intializing the no of consecutive frame to
# track new/old customer
consec = None
reference_no = 0

# intialise the color of the frame
#color = (0, 255, 0)
lastSent = None

# Intialise video streaming
vs = cv2.VideoCapture(0)

# loop over the frames
while True:
	ret, frame = vs.read()
	new_customer = False
	old_customer = False

	if process_this_frame:
		# detect face locations
		face_location = face_recognition.face_locations(frame)
		face_encodings = face_recognition.face_encodings(frame, face_location)

		# getting time frame
		timestamp = datetime.datetime.now()
		ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")

		for face_encoding in face_encodings:
			matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
			if True in matches:
				prediction = "Known"

				if consec == None:
					consec = [prediction, 1]
					#color = (0, 255, 0)

				elif prediction == consec[0]:
					consec[1] += 1

				if consec[0] == "Known" and consec[1] >= 5:
					#color = (0, 255, 0)
					old_customer = True
					first_match_index = matches.index(True)
					name = known_face_names[first_match_index]

				# bounding box around face
				#for (top, right, bottom, left) in face_location:
					#cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

				# Retreving details of the old customer from the database and displaying it
				if old_customer:
					if lastSent is None or (timestamp - lastSent).seconds >= 20:

						conn = sqlite3.connect('customers_database.db')
						c1 = conn.cursor()
						c = conn.cursor()
						c1.execute('SELECT * FROM customers WHERE name = ?', (name,))
						c.execute('SELECT date,purchased_items FROM items WHERE name = ?', (name,))
						rows = c1.fetchall()
						dats = c.fetchall()
						(date, name, mobile_no, email, reference_no, img_loc) = rows[0]
						get(date, name, mobile_no, email, reference_no, img_loc, dats)
						lastSent = timestamp

			# Sending the image to the pop-up window for new customers
			else:
				prediction = "Unknown"

				if consec == None:
					consec = [prediction, 1]
					#color = (0, 255, 0)

				elif prediction == consec[0]:
					consec[1] += 1

				if consec[0] == "Unknown" and consec[1] >= 3:
					#color = (0, 0, 255)
					new_customer = True

				# bounding box around face
				#for (top, right, bottom, left) in face_location:
					#cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

				if new_customer:
					if lastSent is None or (timestamp - lastSent).seconds >= 30:
						# to get only the face image
						#(x, h, y, w) = face_location[0]
						#get_pic = frame[x:y, w:h]
						reference_no += 1
						send(image = frame, ref_no = reference_no)
						lastSent = timestamp

	process_this_frame = not process_this_frame

    # show the frame and record if the user presses a key
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF


	# if the `q` key is pressed, break from the loop
	if key == ord("q"):
		break

# clean up the camera and close any open windows
cv2.destroyAllWindows()
vs.release()
