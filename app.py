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
