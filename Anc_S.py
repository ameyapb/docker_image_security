import subprocess

#Command parameters
print("--Requesting anchor-engine credentials-- \n")
url = input("Enter url (associated with anchor-image api): ") # http://localhost:8228/v1
admin = input("Enter user: ") # admin
pwd = input("Enter password: ") # foobar
anchoreDirectory = input("Enter anchor-engine directory: ") # /home/ameya/anchore

#Recurring variables
emptyString = ""
newLine = "\n"
slashCharacter = "/"
spaceCharacter = " "
utf8 = "utf-8"

#Show non-null Images from the list
def Images(out):
    for x in out:
        if x!=emptyString or len(x)>1:
            print()
            print(x)

#Generate all vulnarabilities of an image for the user
def show(image):
    isImage = False
    proc = subprocess.Popen(["anchore-cli --url " + url + " --u " + admin + " --p " + pwd + " image list"], stdout=subprocess.PIPE, shell=True, cwd=anchoreDirectory)
    (out, err) = proc.communicate()
    outList = out.decode(utf8).split(newLine)
    req = emptyString
    for x in range(1, len(outList)):
        if image in outList[x].split(spaceCharacter)[0].split(slashCharacter)[-1]:
            isImage = True
            break

    if isImage:
        decider = False
        while not decider:
            proc = subprocess.Popen(["anchore-cli --url " + url + " --u " + admin + " --p " + pwd + " image list"], stdout=subprocess.PIPE, shell=True, cwd=anchoreDirectory)
            (out, err) = proc.communicate()
            outList = out.decode(utf8).split(newLine)
            req = emptyString
            for x in range(1, len(outList)):
                if image in outList[x].split(spaceCharacter)[0].split(slashCharacter)[-1]:
                    if "analyzed" in  outList[x].split(spaceCharacter):
                        decider = True
                        break
        print("Finished analysis of the image, thanks for your patience!")

        proc = subprocess.Popen(["anchore-cli --url " + url + " --u " + admin + " --p " + pwd + " image vuln " + image + " all"], stdout=subprocess.PIPE, shell=True, cwd=anchoreDirectory)
        (out, err) = proc.communicate()
        out = out.decode(utf8)
        store = []
        arr = out.split(newLine)
        for i in range(len(arr)):
            if "severity" in arr[i]:
                store.append(i)

        results = []
        for x in store:
            output = []
            output.append("Severity: " + arr[x].split('"')[-2])
            output.append("Url: " + arr[x+1].split('"')[-2])
            output.append("Vulnarability: " + arr[x+2].split('"')[-2])
            results.append(output)
        print("Vulnarabilities for the image:")
        print()
        for x in results:
            print(x[0])
            print(x[2])
            print(x[1])
            print()
            print()

        proc = subprocess.Popen(["anchore-cli --url " + url + " --u " + admin + " --p " + pwd + " evaluate check " + image], stdout=subprocess.PIPE, shell=True, cwd=anchoreDirectory)
        (out, err) = proc.communicate()
        outList = out.decode(utf8).split(newLine)
        print(outList[2])
        print()
    else:
        print("This image does not exist!")
        print()

#Show images to the user
def showImages():
    proc = subprocess.Popen(["anchore-cli --url " + url + " --u " + admin + " --p " + pwd + " image list"], stdout=subprocess.PIPE, shell=True, cwd=anchoreDirectory)
    (out, err) = proc.communicate()
    outList = out.decode(utf8).split(newLine)
    allNames = []
    for x in range(1, len(outList)):
        allNames.append(outList[x].split(spaceCharacter)[0].split(slashCharacter)[-1])
    Images(allNames)

def deleteImage(image):
    proc = subprocess.Popen(["anchore-cli --url " + url + " --u " + admin + " --p " + pwd + " image del " + image + " --force"], stdout=subprocess.PIPE, shell=True, cwd=anchoreDirectory)
    (out, err) = proc.communicate()
    outList = out.decode(utf8).split(newLine)
    if "Error" in out.decode(utf8):
        print("Provide a valid image name or check the image name!")
    else:
        print("Successfully deleted the image.")

def createImage(image):
    proc = subprocess.Popen(["anchore-cli --url " + url + " --u " + admin + " --p " + pwd + " image list"], stdout=subprocess.PIPE, shell=True, cwd=anchoreDirectory)
    (out, err) = proc.communicate()
    outList = out.decode(utf8).split(newLine)
    allNames = []
    for x in range(1, len(outList)):
        allNames.append(outList[x].split(spaceCharacter)[0].split(slashCharacter)[-1])

    if image in allNames:
        print("Please provide an image that does not exist in the docker!")
        Images(allNames)
    else:
        proc = subprocess.Popen(["anchore-cli --url " + url + " --u " + admin + " --p " + pwd + " image add " + image], stdout=subprocess.PIPE, shell=True, cwd=anchoreDirectory)
        (out, err) = proc.communicate()
        if "Error" in out.decode(utf8):
            print("Provide a valid image name!")
            Images(allNames)
        else:
            allNames = []
            for x in range(1, len(outList)):
                allNames.append(outList[x].split(spaceCharacter)[0].split(slashCharacter)[-1])
            identifier = False
            for x in allNames:
                if image in x:
                    identifier = True
                    break
            if identifier:
                print("Provide a new image or the tool will just default to the existing image!")
                Images(allNames)
            else:
                proc = subprocess.Popen(["anchore-cli --url " + url + " --u " + admin + " --p " + pwd + " image add " + image], stdout=subprocess.PIPE, shell=True, cwd=anchoreDirectory)
                (out, err) = proc.communicate()
                print("Successfully created the image!")
                print("Analyzing for vulnarabilties, hold still...")
                show(image)

#Common text to display
def message():
    print("1. Show all images")
    print("2. See vulnarabilties for an existing image")
    print("3. Create a new image")
    print("4. Delete an existing image")
    print("5. Exit")
    selection = input("Provide numerical option: ")
    return selection

#startup
proc = subprocess.Popen(["docker-compose up -d"], stdout=subprocess.PIPE, shell=True, cwd=anchoreDirectory)
(out, err) = proc.communicate()
proc = subprocess.Popen(["docker-compose ps"], stdout=subprocess.PIPE, shell=True, cwd=anchoreDirectory)
(out, err) = proc.communicate()
print("Welcome! What would you like to do today?")
selection = int(message())
while selection < 5 and selection > 0:
    if selection == 1:
        showImages()
        print()
        selection = int(message())
    if selection == 2:
        image = input("Enter image name: ")
        show(image)
        print()
        selection = int(message())
    if selection == 3:
        image = input("Enter image name: ")
        createImage(image)
        print()
        selection = int(message())
    if selection == 4:
        image = input("Enter image name: ")
        deleteImage(image)
        print()
        selection = int(message())
print("Thank you!")
