import glob
import os
import shutil #For copying files
import pathlib
import time
import re
import linecache
from datetime import datetime
#Allows the user to search for a file
#Make it default to the one drive, and then use the c drive if it's not there.
#Convert from a autosave file to a movie file - Check, also deletes the .file if there's a duplicate.
HGC = { #This dictionary will constantly update it's contents of each individual Halo Game, stands for HaloGameClips
    "HaloReach": [],
    "Halo2A": [],
    "Halo3": [],
    "Halo3ODST": [],
    "Halo4": [],
}
HGCD = { #This dictionary contains each individual directory for Halo MCC Clips HGCD stands for Halo Game CLips Directory
    "HaloReach": rf"{os.path.expanduser('~')}\AppData\LocalLow\MCC\Temporary\UserContent\HaloReach\Movie",
    "Halo2A": rf"{os.path.expanduser('~')}\AppData\LocalLow\MCC\Temporary\UserContent\Halo2A\Movie",
    "Halo3": rf"{os.path.expanduser('~')}\AppData\LocalLow\MCC\Temporary\UserContent\Halo3\Movie",
    "Halo3ODST": rf"{os.path.expanduser('~')}\AppData\LocalLow\MCC\Temporary\UserContent\Halo3ODST\Movie",
    "Halo4": rf"{os.path.expanduser('~')}\AppData\LocalLow\MCC\Temporary\UserContent\Halo4\Movie",
}
HGCDF = { #This dictionary contains each individual directory for Halo MCC Clips with .file extensions HGCDF stands for Halo Game CLips Directory .film
    "HaloReach": rf"{os.path.expanduser('~')}\AppData\LocalLow\MCC\Temporary\HaloReach\autosave",
    "Halo2A": rf"{os.path.expanduser('~')}\AppData\LocalLow\MCC\Temporary\Halo2A\autosave",
    "Halo3": rf"{os.path.expanduser('~')}\AppData\LocalLow\MCC\Temporary\Halo3\autosave",
    "Halo3ODST": rf"{os.path.expanduser('~')}\AppData\LocalLow\MCC\Temporary\Halo3ODST\autosave",
    "Halo4": rf"{os.path.expanduser('~')}\AppData\LocalLow\MCC\Temporary\Halo4\autosave",
}
gameNames = ("HaloReach", "Halo2A", "Halo3", "Halo3ODST", "Halo4") #For easy access
DIRECTORIES = [rf'{os.path.expanduser("~")}\OneDrive\MCCTheaterBackup', rf'C:\MCCTheaterBackup'] #Purposely spelled one wrong
currentDirectory = DIRECTORIES[0] #Default is the One Drive
backupTimer = 300
def refreshHGC():
    HGC = {
        # This dictionary will constantly update it's contents of each individual Halo Game, stands for HaloGameClips
        "HaloReach": [],
        "Halo2A": [],
        "Halo3": [],
        "Halo3ODST": [],
        "Halo4": [],
    }
    return HGC

def updateTotalEntries(): #Updates the total entries of the list in the Halo folder.
    totalEntries = {
        "HaloReach": len(HGC["HaloReach"]),
        "Halo2A": len(HGC["Halo2A"]),
        "Halo3": len(HGC["Halo3"]),
        "Halo3ODST": len(HGC["Halo3ODST"]),
        "Halo4": len(HGC["Halo4"]),
    }
    return totalEntries

def getDate(): #Gets the date
    now = datetime.now()
    currentTime = now.strftime("%m/%d/%Y %H:%M:%S")
    return currentTime

def createDirectory(): #Creates a directory with each game if it's not already created
    applySettings()
    global currentDirectory
    try: #Create the parent directory using the OneDrive first
        pathlib.Path(currentDirectory).mkdir(parents=False, exist_ok=False)
    except FileNotFoundError: #If the One Drive doesn't exist
        print("One Drive doesn't exist, using C Drive")
        try:
            currentDirectory = DIRECTORIES[1]
            pathlib.Path(currentDirectory).mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            pass #No one drive exists and the C drive directory has already been created
    except FileExistsError:
        pass
    try:
        with open(rf'{currentDirectory}\Settings.txt', 'x') as f: #Create the file if it's not made, hence the x
            #Beginning of Settings file
            f.write(f"Created on {getDate()}\n")
            f.write(f"Backup Timer: {backupTimer}")
            f.write("\n")
            f.write(f"Current directory: {currentDirectory}")
            f.close()
            #End of Settings file
    except FileExistsError:
        pass
    try:
        with open(rf'{currentDirectory}\Saves.txt', 'x') as f: #Create the file if it's not made, hence the x
            f.write(f"Created on {getDate()}\n")
            f.close()
    except FileExistsError:
        with open(rf'{currentDirectory}\Saves.txt', 'a') as f:
            f.write("-   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -\n")
            f.write("Restarting, Current Individual Totals:\n")
            f.close()
            printTotalFileCounts()
            #Include the totals here.
    for key in HGCD: #Create each sub directory
        try:
            pathlib.Path(rf'{currentDirectory}\{key}').mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            pass

def applySettings(): #Will apply the settings from the text file.
    global backupTimer, currentDirectory
    try:
        file = open(rf"{currentDirectory}\Settings.txt")
        settingLine = file.readlines()  # Start at 1 for backup timer, 2 for directory
        backupTimer = int(re.sub("\D", "", settingLine[1]))
        currentDirectory = settingLine[2].replace("Current directory: ", "")
    except FileNotFoundError:
        pass #Pass because this will be the first time the program is ever ran

def getGameClips(haloGame, targetFolder): #Purpose is to take the game name and it's directory and get each individual file name.
    os.chdir(targetFolder) #Open the target game folder
    for file in glob.glob("*.mov"):
        if file not in HGC[haloGame]: #Thank god, this fixed many future errors.
            HGC[haloGame] += [file] #This works!
    for file in glob.glob("*.film"):
        if file not in HGC[haloGame]: #Thank god, this fixed many future errors.
            HGC[haloGame] += [file] #This works!

def updateHGC(): #Purpose is to update the HGC directory with every game's file
    for key in HGCD: #Goes through each key inside HGCD
        getGameClips(key, HGCD[key]) #Populates the entire dictionary and will add new ones, .mov
        getGameClips(key, HGCDF[key])  # Populates the entire dictionary and will add new ones, .film

def copyPaste(haloGame, original): #Purpose is to copy each games theater clip into a backup folder(My choosing right now)
    targetFolder = rf'{currentDirectory}\{haloGame}' #Target folder
    try:
        shutil.copy2(original, targetFolder)
    except FileNotFoundError:
        pass

def commenceBackUp(previousTotal): #Backup each individual game
    updateHGC()
    # try:
    for haloGame in gameNames: #Go through each halo game name
        for x in range(0, len(HGC[haloGame])):  # Gets the length
            copyPaste(haloGame, rf"{HGCD[haloGame]}\{HGC[haloGame][x]}") #copyPaste does it's magic, for Movie directory
            copyPaste(haloGame, rf"{HGCDF[haloGame]}\{HGC[haloGame][x]}") #copyPaste does it's magic, for autosave directory
    # except FileNotFoundError:
    #     pass
    convertToMOV()
    writeToSaveFile(previousTotal)

def getTotalAddedFiles(): #Get the total integer value of the files added.
    total = 0
    totalEntries = updateTotalEntries() #Get the most recent total
    for key in totalEntries: #Loop through
        total += totalEntries[key] #Add
    return total

def printTotalFileCounts(): #Might be Lengthy, gets the actual total amount.
    global currentDirectory
    totals = {  # Features the total changes between the old and new save
        "HaloReach": 0,
        "Halo2A": 0,
        "Halo3": 0,
        "Halo3ODST": 0,
        "Halo4": 0,
    }
    for key in totals:
        os.chdir(rf'{currentDirectory}\{key}')
        for file in glob.glob("*.mov"):
            totals[key] += 1
    for key in totals:
        with open(rf'{currentDirectory}\Saves.txt', 'a') as f:
            f.write(f"{key}: {totals[key]}\n")
        f.close()

def returnTotalFileCounts(): #Might be Lengthy, gets the actual total amount, used for "saving"
    global currentDirectory
    totals = {  # Features the total changes between the old and new save
        "HaloReach": 0,
        "Halo2A": 0,
        "Halo3": 0,
        "Halo3ODST": 0,
        "Halo4": 0,
    }
    for key in totals:
        os.chdir(rf'{currentDirectory}\{key}')
        for file in glob.glob("*.mov"):
            totals[key] += 1
    return totals

def getTotalFiles(): #Might be Lengthy, gets the actual total amount altogether
    global currentDirectory
    totals = {  # Features the total changes between the old and new save
        "HaloReach": 0,
        "Halo2A": 0,
        "Halo3": 0,
        "Halo3ODST": 0,
        "Halo4": 0,
    }
    totalFiles = 0
    for key in totals:
        os.chdir(rf'{currentDirectory}\{key}')
        for file in glob.glob("*.mov"):
            totalFiles += 1
        # print(totalFiles)
    return totalFiles

def writeToSaveFile(previousTotal): #Writes to the saved file, will eventually note changes.
    global currentDirectory
    with open(rf'{currentDirectory}\Saves.txt', 'a') as f:
        f.write("***************************************\n")
        f.write(f"New save on: {getDate()}\n")
        f.write(f"Total files: {getTotalFiles()}\n")
        f.write("Changes:\n")
        for key in returnTotalFileCounts():
            f.write(f"{key}: {returnTotalFileCounts()[key] - previousTotal[key]} Added\n")
        f.close()

def convertToMOV(): #Use this to convert the .film to a .mov, will go right before the move to the directory.
    global currentDirectory
    for haloGame in gameNames:
        os.chdir(rf'{currentDirectory}\{haloGame}')
        for file in glob.glob("*.film"):
            newFile = file.replace(".film", ".mov")
            try:
                os.rename(rf'{currentDirectory}\{haloGame}\{file}', rf'{currentDirectory}\{haloGame}\{newFile}')
            except FileExistsError:
                os.remove(rf'{currentDirectory}\{haloGame}\{file}')

#Beginning of the program.
createDirectory()
while True:
    HGC = refreshHGC() #Might prevent the file not found bug, update: It did!
    previousTotal = returnTotalFileCounts()
    commenceBackUp(previousTotal)
    print(f"Backup complete at {getDate()}")
    time.sleep(backupTimer)
