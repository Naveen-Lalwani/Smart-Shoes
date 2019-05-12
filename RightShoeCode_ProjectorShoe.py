'''
Final Project: Smart Shoes

17-722: Building User Focused Sensor Systems

This file is to be implemented in the right shoe which has the Projector to
display the GUI and the data from the sensors and respond to the input from the
capacitive touch.

Authors: Naveen Lalwani, Rangeesh Muthaiyan
Andrew ID: naveenl@andrew.cmu.edu, rmuthaiy@andrew.cmu.edu
''' 
import tkinter as tk
from PIL import ImageTk, Image
from tkinter import messagebox as msg
import matplotlib.pyplot as plt
from tkinter import ttk
import statistics
from bluetooth import *

'''
Making Connection to the Raspberry Pi on the left shoe (Sensor Shoe)
'''
server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

# Hardcoded uuid
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( server_sock, "SampleServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ] 
                    )                   
print ("Waiting for connection on RFCOMM channel %d" % port)
client_sock, client_info = server_sock.accept()
print ("Accepted connection from ", client_info)


def displayMessage():
    msg.showinfo("Smart Shoes", "Congratulations. You are wearing smartshoes.")

'''
Infinite Loop for running the program again and again.
'''
while True:
    # Listen to the data from the server and receive it in command.
    command = ""
    try:
        command = client_sock.recv(1024)
        command = str(command)
        print ("received [%s]" % command)
    except IOError:
        pass
    
    # Modifying command to get rid of header and other information to get the desired string.
    command = command[2:len(command)-1]
    '''
    Now we proceed as follows:
    If the Command is STEPS, we create STEP COUNTER GUI and wait to receive step
    counts to display and then wait for the EXIT command to close the GUI.
    
    If the Command is HEART, we create the HEART RATE MONITOR GUI and wait to 
    receive the user's heart rate data and then display the user's present heart
    rate and statistics and graph of all the readings stored in database. Then,
    we wait for the EXIT command to close the GUI.
    '''
    
    if (command == "STEPS"):
        '''
        Setting up the main window of 'Step Counter' GUI
        '''
        root = tk.Tk()
        root.minsize(300, 300)
        root.title("Step Counter - Smart Shoes")
        
        '''
        Setting up the MENU BAR for the window
        '''
        menubar = tk.Menu()
        root.config(menu = menubar)
        # Adding File menu
        fileMenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label = "File", menu = fileMenu)
        fileMenu.add_command(label = "Reset")
        fileMenu.add_command(label = "Exit")
        # Adding Help menu
        helpMenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label = "Help", menu = helpMenu)
        helpMenu.add_command(label = "About Us", command= displayMessage)        
        
        '''
        Setting up MULTIPLE FRAMES within the window
        '''
        frame2 = tk.Frame(root, height = 50, width = 300, pady = 20, padx = 20) # Progress Bar
        frame3 = tk.Frame(root, height = 110, width = 150, pady = 20, padx = 20) # FootSteps Image
        frame4 = tk.Frame(root, height = 50, width = 300, pady = 20, padx = 20) # Current Steps
        frame5 = tk.Frame(root, height = 250, width = 200, pady = 20, padx = 20) # Current Steps
        '''
        Setting Up frame 2 that displays the progress bar.
        '''
        tg = tk.Label(frame2, text = "GOAL COMPLETION")
        progress = ttk.Progressbar(frame2, orient = "horizontal", length = 600, mode = "determinate")
        progress["maximum"] = 1000
        '''
        Setting Up frame 5 that displays today's goal and it's entry. 
        '''
        goal = tk.Label(frame5, text="Goal: ")
        goalEntry = tk.Entry(frame5, width = 20)
        goalEntry.insert(0, "1000")
        '''
        Positioning within Frame 5
        '''
        tg.grid(row = 0, column = 0)
        progress.grid(row = 2, column = 0)
        i = 8       # variable to manage ROW position
        j = 1       # variable to manage COLUMN position
        goal.grid(row = i + 1, column = j)
        goalEntry.grid(row = i + 1, column = j + 1)
        '''
        Setting up the FRAME 3 Footsteps display for visual treat.
        '''
        canvas = tk.Canvas(frame3, height = 100, width = 100, background = "black")
        canvas.pack()
        img = Image.open('/home/pi/Desktop/Foot.png')
        canvas.image = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, image = canvas.image, anchor = 'nw')
        '''
        Setting up the FRAME 4 for displaying the present number of steps & current state.
        '''
        # Current Steps Label and it's text box.
        currSteps = tk.Label(frame4, text="Current Footsteps")
        currStepsEntry = tk.Entry(frame4, width = 20)
        currSteps.grid(row = 10, column = 0)
        currStepsEntry.grid(row = 10, column = 1)
        
        #State label and it's text box.
        stateLabel = tk.Label(frame4, text="Current State")
        stateEntry = tk.Entry(frame4, width = 20)
        stateLabel.grid(row = 12, column = 0)
        stateEntry.grid(row = 12, column = 1)
        ''' 
        Positioning the Frames within the Main Window.
        '''
        frame2.grid(row = 200, column = 100)
        frame3.grid(row = 100, column = 100, columnspan = 300)
        frame4.grid(row = 150, column = 100, columnspan = 20)
        frame5.grid(row = 202, column = 100)
        
        '''
        Listening for the values from the left shoe to display in the GUI.
        '''
        # Getting the Step Count.
        stepCounting = client_sock.recv(1024)
        stepCounting = str(stepCounting)
        stepCounting = stepCounting[2: len(stepCounting) - 1]
        progress["value"] = 2 * float(stepCounting)
        print(stepCounting)
        currStepsEntry.insert(1, str(2*int(stepCounting)))
        
        # Getting the State of the User.
        state = client_sock.recv(1024)
        state = str(state)
        state = state[2: len(state) - 1]
        print(state)
        stateEntry.insert(1, state)
        
        '''
        Initiating the GUI Interface.
        '''
        root.update()
        '''
        Running Background task to exit the main window. Wait for EXIT command
        from the left shoe to exit the GUI. If the command is not exit, keep on
        dislaying the current window.
        '''
        exitWindow = True 
        while(exitWindow):
            # Listening for the EXIT command.
            command2 = client_sock.recv(1024)
            command2 = str(command2)
            command2 = command2[2:len(command2) - 1]
            if (command2 != "EXIT"):
                root.update_idletasks
            else:
                root.quit()
                root.destroy()
                exitWindow = False
                
    ###########################################################################
    if (command == "HEART"):
        # Flag text to identify the state of the window.
        print("I am in heart")
        '''
        Setting up the main window of 'Heart Rate Monitor' GUI
        '''
        root = tk.Tk()
        root.minsize(250, 350)
        root.title("Heart Rate Monitor - Smart Shoes")

        '''
        Setting up the MENU BAR for the window
        '''
        menubar = tk.Menu()
        root.config(menu = menubar)
        # Adding File menu
        fileMenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label = "File", menu = fileMenu)
        fileMenu.add_command(label = "New")
        fileMenu.add_command(label = "Exit")
        # Adding Help menu
        helpMenu = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label = "Help", menu = helpMenu)
        helpMenu.add_command(label = "About Us", command= displayMessage)

        '''
        Setting up MULTIPLE FRAMES within the window
        '''
        frame2 = tk.Frame(root, height = 50, width = 50, pady = 5, padx = 10) # Statistics
        frame3 = tk.Frame(root, height = 100, width = 100, pady = 5, padx = 10) # Heart Image
        frame4 = tk.Frame(root, height = 100, width = 50, pady = 5, padx = 50) # Present Heart Rate
        frame5 = tk.Frame(root, height = 250, width = 300, pady = 5, padx = 10) # MatPlotLib
        '''
        Setting Up frame 2 that displays heart rate statistics 
        '''
        hs = tk.Label(frame2, text = " HEART RATE STATISTICS")
    
        mean = tk.Label(frame2, text="Mean: ")
        meanEntry = tk.Entry(frame2, width = 20)
        median = tk.Label(frame2, text="Median: ")
        medianEntry = tk.Entry(frame2, width = 20)
        maxHeart = tk.Label(frame2, text="Max: ")
        maxHeartEntry = tk.Entry(frame2, width = 20)
        minHeart = tk.Label(frame2, text="Min: ")
        minHeartEntry = tk.Entry(frame2, width = 20)
        
        hs.grid(row = 0, column = 0)
        i = 2       # variable to manage ROW position
        j = 0       # variable to manage COLUMN position
        mean.grid(row = i + 1, column = j)
        median.grid(row = i + 2, column = j)
        maxHeart.grid(row = i + 3, column = j)
        minHeart.grid(row = i + 4, column = j)
        
        meanEntry.grid(row = i + 1, column = j + 1)
        medianEntry.grid(row = i + 2, column = j + 1)
        maxHeartEntry.grid(row = i + 3, column = j + 1)
        minHeartEntry.grid(row = i + 4, column = j + 1)
        
        '''
        Setting up the FRAME 3 heart image display for visual treat
        '''
        canvas = tk.Canvas(frame3, height = 100, width = 100, background = "black")
        canvas.pack()
        img = Image.open('/home/pi/Desktop/heart.png')
        canvas.image = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, image = canvas.image, anchor = 'nw')
        
        '''
        Setting up the FRAME 4 for displaying the present heart rate
        '''
        presentHeartRate = tk.Label(frame4, text="Present Heart Rate:")
        presentHeartRateEntry = tk.Entry(frame4, width = 20)
        presentHeartRate.grid(row = 10, column = 0)
        presentHeartRateEntry.grid(row = 10, column = 1)
        
        '''
        Setting up the FRAME 5 for presenting the graph
        '''
        X = []
        Y = []
        # Loading data from the database.
        with open("/home/pi/Desktop/heartRate.txt") as logFile:
            i = 1
            for line in logFile:
                line = line.split('\n')
                X.append(int(line[0]))
                Y.append(i)
                i = i + 1
        logFile.close()
        plt.plot(Y, X)
        plt.savefig('/home/pi/Desktop/foo.png')
        canvas = tk.Canvas(frame5, height = 250, width = 300)
        canvas.pack()
        img = Image.open('/home/pi/Desktop/foo.png')
        
        # Resizing Image to make it fit within the frame.
        basewidth = 350
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize))
        canvas.image = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, image = canvas.image, anchor = 'nw')
        
        # Filling the heart rate statistics in the statistics box.
        meanEntry.insert(0, statistics.mean(X))
        medianEntry.insert(0, statistics.median(X))
        maxHeartEntry.insert(0, max(X))
        minHeartEntry.insert(0, min(X))
        
        ''' 
        Positioning the frames within the window.
        '''
        frame2.grid(row = 100, column = 50)
        frame3.grid(row = 50, column = 50)
        frame4.grid(row = 50, column = 100)
        frame5.grid(row = 100, column = 100)
        
        '''
        Receiving the current heart rate from the user sensed in the left shoe.
        '''
        heartRateString = client_sock.recv(1024)
        heartRateString = str(heartRateString)
        heartRateString = heartRateString[2: len(heartRateString) - 1]
        # Flag for the developer
        print(heartRateString)
        
        # Inserting the heart rate in the text box.
        presentHeartRateEntry.insert(1, heartRateString)
        
        # Writing the heart rate data to the database file.
        with open("/home/pi/Desktop/heartRate.txt", "a") as logFile:
            logFile.writelines(heartRateString)
            logFile.writelines("\n")
        logFile.close()
        
        '''
        Initiating the GUI Interface.
        '''
        root.update()
        
        '''
        Running Background task to exit the main window. Wait for EXIT command
        from the left shoe to exit the GUI. If the command is not exit, keep on
        dislaying the current window.
        '''
        exitWindow = True 
        while(exitWindow):
            # Listening for the EXIT Commmand.
            command2 = client_sock.recv(1024)
            command2 = str(command2)
            command2 = command2[2:len(command2) - 1]
            if (command2 != "EXIT"):
                root.update_idletasks
            else:
                root.quit()
                root.destroy()
                exitWindow = False
        