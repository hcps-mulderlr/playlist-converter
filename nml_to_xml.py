import wget

example2 = r"C:\Users\hcps-mulderlr\dev\example2.nml"

#locating the data in the m3u file
with open(example2, "r") as file2:
    text = file2.read()
    
    # Split into entries based on #EXTVDJ lines
    entries = []
    lines = text.split('\n')
    current_entry = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('<ENTRY'):
            if current_entry:
                entries.append('\n'.join(current_entry))
            current_entry = [line]
        elif line and current_entry:
            current_entry.append(line)
    
    if current_entry:
        entries.append('\n'.join(current_entry))
    
    # Function to unescape XML characters
    def unescape_xml(text):
        if not text:
            return ''
        text = str(text)
        # text = text.replace('&amp;', '&')
        # text = text.replace('&lt;', '<')
        # text = text.replace('&gt;', '>')
        # text = text.replace('&quot;', '"')
        # text = text.replace('&apos;', "'")
        return text
    
    # Function to extract value between tags
    def extract_tag_value(text, tag):
        start_tag = f"{tag}='"
        end_tag = f"'"
        start_idx = text.find(start_tag)
        if start_idx == -1:
            return ""
        start_idx += len(start_tag)
        end_idx = text.find(end_tag, start_idx)
        if end_idx == -1:
            return ""
        return text[start_idx:end_idx]
    
    #writing the start of the file
    xmlFile = open("example2.xml", "w")
    xmlFile.write("<?xml version='1.0' encoding='UTF-8'?>\n<DJ_PLAYLISTS Version='1.0.0'>\n<PRODUCT Name='rekordbox' Version='5.6.1' Company='Pioneer DJ'/>\n<COLLECTION Entries='" + str(len(entries)) + "'>\n")
    
    #getting the data
    for i, entry in enumerate(entries):
        # Extract metadata from each entry
        title = extract_tag_value(entry, "TITLE")
        artist = extract_tag_value(entry, "ARTIST")
        time = extract_tag_value(entry, "time")
        size = extract_tag_value(entry, "FILESIZE")
        fileLocation = extract_tag_value(entry, "DIR")
        
        # Clean up and escape XML characters
        title = unescape_xml(title.strip())
        artist = unescape_xml(artist.strip())
        time = unescape_xml(time.strip())
        size = unescape_xml(size.strip())
        fileLocation = unescape_xml(fileLocation.strip())
        
        print(title)
        
        #printing out the data
        print("Title:" + str(title) + "\nArtist: " + str(artist) + "\nDuration: " + str(time) + "\nSize: " + str(size) + "\n" + "\nFile Location: " + str(fileLocation) + "\n")
        
        xmlFile.write("<TRACK TrackID='" + str(i+1) + "' Name='" + str(title) + "' Artist='" + str(artist) + "' TotalTime='" + str(time) + "' Size='" + str(size) + "' Location='" + str(fileLocation) + "'>\n</TRACK>\n")
    
    #closing the file
    xmlFile.write("</COLLECTION>\n</DJ_PLAYLISTS>\n")
    xmlFile.close()