import wget

example2 = r"C:\Users\hcps-mulderlr\dev\examples\playlist2.m3u"


#locating the data in the m3u file
with open(example2, "r") as file2:
    text = file2.read()

    
    startSub = "<title>"
    startTitle = []
    start = 0
    while(index := text.find(startSub, start)) != -1:
        startTitle.append(index)
        start = index + len(startSub)
    
    endSub = "</title>"
    endTitle = []
    start = 0
    while(index := text.find(endSub, start)) != -1:
        endTitle.append(index)
        start = index + len(endSub)
    
    startSubA = "<artist>"
    startArtist = []
    start = 0
    while(index := text.find(startSubA, start)) != -1:
        startArtist.append(index)
        start = index + len(startSubA)
    
    endSubA = "</artist>"
    endArtist = []
    start = 0
    while(index := text.find(endSubA, start)) != -1:
        endArtist.append(index)
        start = index + len(endSubA)
    
    startSubT = "<time>"
    startTime = []
    start = 0
    while(index := text.find(startSubT, start)) != -1:
        startTime.append(index)
        start = index + len(startSubT)
    
    endSubT = "</time>"
    endTime = []
    start = 0
    while(index := text.find(endSubT, start)) != -1:
        endTime.append(index)
        start = index + len(endSubT)
    
    startSubF = "<filesize>"
    startSize = []
    start = 0
    while(index := text.find(startSubF, start)) != -1:
        startSize.append(index)
        start = index + len(startSubF)
    
    endSubF = "</filesize>"
    endSize = []
    start = 0
    while(index := text.find(endSubF, start)) != -1:
        endSize.append(index)
        start = index + len(endSubF)
    
    startSubFT = "</title>"
    startFT = []
    start = 0
    while(index := text.find(startSubFT, start)) != -1:
        startFT.append(index)
        start = index + len(startSubFT)
    
    endSubFT = "#"
    endFT = []
    start = 0
    while(index := text.find(endSubFT, start)) != -1:
        endFT.append(index)
        start = index + len(endSubFT)
    endFT.remove(0)
    

    
    #writing the start of the file
    xmlFile = open("example2.xml", "w")
    xmlFile.write("<?xml version='1.0' encoding='UTF-8'?>\n<DJ_PLAYLISTS Version='1.0.0'>\n<PRODUCT Name='rekordbox' Version='5.6.1' Company='Pioneer DJ'/>\n<COLLECTION Entries='" + str(len(startTitle)) + "'>\n")
    
    #getting the data
    for i in range(len(startTitle)):
        title = text[startTitle[i] + len(startSub):endTitle[i]]

        artist = text[startArtist[i] + len(startSubA):endArtist[i]]

        time = text[startTime[i] + len(startSubT):endTime[i]]

        size = text[startSize[i] + len(startSubF):endSize[i]]
        fileLocation = text[startFT[i] + len(startSubFT):endFT[i]]
        
        # reset file location
        fileLocation = fileLocation.strip()
        # Function to escape XML characters
        def escape_xml(text):
            if not text:
                return ''
            text = str(text)
            text = text.replace('&', '&amp;')
            text = text.replace('<', '&lt;')
            text = text.replace('>', '&gt;')
            text = text.replace('"', '&quot;')
            text = text.replace("'", '&apos;')
            return text
        # Escape XML characters
        title = escape_xml(title)
        artist = escape_xml(artist)
        time = escape_xml(time)
        size = escape_xml(size)
        fileLocation = escape_xml(fileLocation)
        
        print(startTitle)
        print(endTitle)
        print(str(title))
        print(str(artist))
        
        #printing out the data
        # print("Title:" + str(title) + "\nArtist: " + str(artist) + "\nDuration: " + str(time) + "\nSize: " + str(size) + "\n" + "\nFile Location: " + str(fileLocation) + "\n")
        
        xmlFile.write("<TRACK TrackID='" + str(i+1) + "' Name='" + str(title) + "' Artist='" + str(artist) + "' TotalTime='" + str(time) + "' Size='" + str(size) + "' Location='" + str(fileLocation) + "'>\n</TRACK>\n")
    
    #closing the file
    xmlFile.write("</COLLECTION>\n</DJ_PLAYLISTS>\n")
    xmlFile.close()