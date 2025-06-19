import wget

example2 = r"C:\Users\hcps-mulderlr\dev\examples\playlist2.m3u"

#locating the data in the m3u file
with open(example2, "r") as file2:
    text = file2.read()
    
    # Split into entries based on #EXTVDJ lines
    entries = []
    lines = text.split('\n')
    current_entry = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('#EXTVDJ:'):
            if current_entry:
                entries.append('\n'.join(current_entry))
            current_entry = [line]
        elif line and current_entry:
            current_entry.append(line)
    
    if current_entry:
        entries.append('\n'.join(current_entry))
    
    # Function to escape XML characters
    def escape_xml(text):
        if not text:
            return ''
        text = str(text)
        # text = text.replace('&', '&amp;')
        # text = text.replace('<', '&lt;')
        # text = text.replace('>', '&gt;')
        # text = text.replace('"', '&quot;')
        # text = text.replace("'", '&apos;')
        return text
    
    # Function to extract value between tags
    def extract_tag_value(text, tag):
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"
        start_idx = text.find(start_tag)
        if start_idx == -1:
            return ""
        start_idx += len(start_tag)
        end_idx = text.find(end_tag, start_idx)
        if end_idx == -1:
            return ""
        return text[start_idx:end_idx]
    
    #writing the start of the file
    m3u8File = open("example2.m3u8", "w")
    m3u8File.write("#EXTM3U\n")
    
    #getting the data
    for i, entry in enumerate(entries):
        # Extract metadata from each entry
        title = extract_tag_value(entry, "title")
        artist = extract_tag_value(entry, "artist")
        time = extract_tag_value(entry, "time")
        size = extract_tag_value(entry, "filesize")
        
        # Extract file location (last line that's not a #EXTVDJ line)
        entry_lines = entry.split('\n')
        fileLocation = ""
        for line in reversed(entry_lines):
            line = line.strip()
            if line and not line.startswith('#') and (':\\' in line or line.startswith('/')):
                fileLocation = line
                break
        
        # Clean up and escape XML characters
        title = escape_xml(title.strip())
        artist = escape_xml(artist.strip())
        time = escape_xml(time.strip())
        size = escape_xml(size.strip())
        fileLocation = escape_xml(fileLocation.strip())
        
        print(title)
        
        #printing out the data
        print("Title:" + str(title) + "\nArtist: " + str(artist) + "\nDuration: " + str(time) + "\nSize: " + str(size) + "\n" + "\nFile Location: " + str(fileLocation) + "\n")
        
        m3u8File.write("#EXTINF:" + str(time) + "," + str(artist) + " - " + str(title) + "\n" + str(fileLocation) + "\n")
    
    #closing the file
    m3u8File.close()