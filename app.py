import os, io
import psycopg2
from flask import Flask, render_template, request, url_for, redirect, send_file
from flask_bcrypt import Bcrypt
from flask import flash
import getpass
import os.path
import wget

app = Flask(__name__)

username = getpass.getuser()
downloads_path = os.path.join("C:\\Users", username, "Downloads")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    
    if 'playlistFile' not in request.files:
        flash('No file')
        return render_template('index.html')
    file = request.files['playlistFile']
    
    if file.filename == '':
        return render_template('index.html')
    
    if file:
        filename = file.filename
        # file_path = r'"'+ str(os.path.join(downloads_path, filename))+'"'
        file_path = os.path.join(downloads_path, filename)
        file.save(file_path)

    
    if request.method == 'POST':
        convertTo = request.form.get('format')
        if convertTo == 'm3u':
            extension = os.path.splitext(file.filename)[1].lower()
            if extension == '.m3u':
                return 'File is already in M3U format'
            elif extension == '.xml':
                # convert XML to M3U
                # Placeholder for conversion logic
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    print(text)
                
                entries = []
                lines = text.split('\n')
                current_entry = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('<TRACK'):
                        if current_entry:
                            entries.append('\n'.join(current_entry))
                        current_entry = [line]
                    elif line and current_entry:
                        current_entry.append(line)
                
                if current_entry:
                    entries.append('\n'.join(current_entry))
                
                def unescape_xml(text):
                    if not text:
                        return ''
                    text = str(text)
                    text = text.replace('&amp;', '&')
                    text = text.replace('&lt;', '<')
                    text = text.replace('&gt;', '>')
                    text = text.replace('&quot;', '"')
                    text = text.replace('&apos;', "'")
                    return text
                
                def extract_tag_value(text, tag):
                    # Try both single and double quotes
                    for quote in ["'", '"']:
                        start_tag = f'{tag}={quote}'
                        start_idx = text.find(start_tag)
                        if start_idx != -1:
                            start_idx += len(start_tag)
                            end_idx = text.find(quote, start_idx)
                            if end_idx != -1:
                                return text[start_idx:end_idx]
                    return ""
                
                output_filename = os.path.splitext(filename)[0] + '.m3u'
                output_path = os.path.join(downloads_path, output_filename)
                print(output_path)
                with open(output_path, "w", encoding="utf-8") as m3uFile:
                    m3uFile.write("#EXTM3U\n")  # Add M3U header
                    
                    for i, entry in enumerate(entries):
                        # Extract metadata from each entry
                        title = extract_tag_value(entry, "Name")
                        artist = extract_tag_value(entry, "Artist")
                        time = extract_tag_value(entry, "TotalTime")
                        size = extract_tag_value(entry, "Size")
                        fileLocation = extract_tag_value(entry, "Location")
                        # Clean up and escape XML characters
                        title = unescape_xml(title.strip()) if title else "Unknown Title"
                        artist = unescape_xml(artist.strip()) if artist else "Unknown Artist"
                        time = unescape_xml(time.strip()) if time else "0"
                        size = unescape_xml(size.strip()) if size else "0"
                        fileLocation = unescape_xml(fileLocation.strip()) if fileLocation else ""
                        # print(f"Title: {title}, Artist: {artist}, Time: {time}, Size: {size}, Location: {fileLocation}")
                        
                        if fileLocation:  # Only write entries that have a file location
                            m3uFile.write("#EXTVDJ: <time>" + str(time) + "</time><lastplaytime>0</lastplaytime><filesize>" + str(size) + "</filesize><artist>" + str(artist) + "</artist><title>" + str(title) + "</title>\n" + str(fileLocation) +"\n")
                
                return send_file(output_path, as_attachment=True)
            elif extension == '.nml':
                # convert NML to M3U
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    
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
                
                def unescape_xml(text):
                    if not text:
                        return ''
                    text = str(text)
                    text = text.replace('&amp;', '&')
                    text = text.replace('&lt;', '<')
                    text = text.replace('&gt;', '>')
                    text = text.replace('&quot;', '"')
                    text = text.replace('&apos;', "'")
                    return text
                
                def extract_tag_value(text, tag):
                    # Try both single and double quotes
                    for quote in ["'", '"']:
                        start_tag = f'{tag}={quote}'
                        start_idx = text.find(start_tag)
                        if start_idx != -1:
                            start_idx += len(start_tag)
                            end_idx = text.find(quote, start_idx)
                            if end_idx != -1:
                                return text[start_idx:end_idx]
                    return ""
                
                output_filename = os.path.splitext(filename)[0] + '.m3u'
                output_path = os.path.join(downloads_path, output_filename)
                
                with open(output_path, "w", encoding="utf-8") as m3uFile:
                    m3uFile.write("#EXTM3U\n")  # Add M3U header
                    
                    for i, entry in enumerate(entries):
                        title = extract_tag_value(entry, "TITLE")
                        artist = extract_tag_value(entry, "ARTIST")
                        time = extract_tag_value(entry, "time")
                        size = extract_tag_value(entry, "FILESIZE")
                        fileLocation = extract_tag_value(entry, "DIR")
                        
                        title = unescape_xml(title.strip()) if title else "Unknown Title"
                        artist = unescape_xml(artist.strip()) if artist else "Unknown Artist"
                        time = unescape_xml(time.strip()) if time else "0"
                        size = unescape_xml(size.strip()) if size else "0"
                        fileLocation = unescape_xml(fileLocation.strip()) if fileLocation else ""
                        
                        if fileLocation:  # Only write entries that have a file location
                            m3uFile.write("#EXTVDJ: <time>" + str(time) + "</time><lastplaytime>0</lastplaytime><filesize>" + str(size) + "</filesize><artist>" + str(artist) + "</artist><title>" + str(title) + "</title>\n" + str(fileLocation) +"\n")
                
                return send_file(output_path, as_attachment=True)
            else:
                # convert M3U8 to M3U
                # Placeholder for conversion logic
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    
                entries = []
                lines = text.split('\n')
                current_entry = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('#EXTINF'):
                        if current_entry:
                            entries.append('\n'.join(current_entry))
                        current_entry = [line]
                    elif line and current_entry:
                        current_entry.append(line)
                
                if current_entry:
                    entries.append('\n'.join(current_entry))
                
                def unescape_xml(text):
                    if not text:
                        return ''
                    text = str(text)
                    text = text.replace('&amp;', '&')
                    text = text.replace('&lt;', '<')
                    text = text.replace('&gt;', '>')
                    text = text.replace('&quot;', '"')
                    text = text.replace('&apos;', "'")
                    return text
                
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
                
                output_filename = os.path.splitext(filename)[0] + '.m3u'
                output_path = os.path.join(downloads_path, output_filename)
                
                with open(output_path, "w", encoding="utf-8") as m3uFile:
                    xmlFile.write("#EXTM3U\n")  # Add M3U header
                    
                    for i, entry in enumerate(entries):
                        entry_lines = entry.split('\n')
                        extinf_line = ""
                        fileLocation = ""
                        
                        for line in entry_lines:
                            line = line.strip()
                            if line.startswith('#EXTINF:'):
                                extinf_line = line
                            elif line and not line.startswith('#'):
                                fileLocation = line
                                break
                        
                        #ai generated
                        if extinf_line:
                            extinf_parts = extinf_line[8:]
                            comma_idx = extinf_parts.find(',')
                            if comma_idx != -1:
                                time = extinf_parts[:comma_idx]
                                artist_title = extinf_parts[comma_idx+1:]
                                if ' - ' in artist_title:
                                    artist, title = artist_title.split(' - ', 1)
                                else:
                                    artist = ""
                                    title = artist_title
                            else:
                                time = ""
                                artist = ""
                                title = ""
                        else:
                            time = ""
                            artist = ""
                            title = ""
                        
                        size = ""
                        #end of ai generated code
                        # Clean up and escape XML characters
                        title = title.strip()
                        artist = artist.strip()
                        time =  time.strip()
                        size =  size.strip()
                        fileLocation = fileLocation.strip()
                        
                        if fileLocation:  # Only write entries that have a file location
                            m3uFile.write("#EXTVDJ: <time>" + str(time) + "</time><lastplaytime>0</lastplaytime><filesize>" + str(size) + "</filesize><artist>" + str(artist) + "</artist><title>" + str(title) + "</title>\n" + str(fileLocation) +"\n")
                
                return send_file(output_path, as_attachment=True)
        elif convertTo == 'xml':
            extension = os.path.splitext(file.filename)[1].lower()
            if extension == '.xml':
                return 'File is already in XML format'
            elif extension == '.m3u':
                # convert M3U to XML
                # Placeholder for conversion logic
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    
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
                
                output_filename = os.path.splitext(filename)[0] + '.xml'
                output_path = os.path.join(downloads_path, output_filename)
                
                with open(output_path, "w", encoding="utf-8") as xmlFile:
                    xmlFile.write("<?xml version='1.0' encoding='UTF-8'?>\n<DJ_PLAYLISTS Version='1.0.0'>\n<PRODUCT Name='rekordbox' Version='5.6.1' Company='Pioneer DJ'/>\n<COLLECTION Entries='" + str(len(entries)) + "'>\n")
                    
                    for i, entry in enumerate(entries):
                        title = extract_tag_value(entry, "title")
                        artist = extract_tag_value(entry, "artist")
                        time = extract_tag_value(entry, "time")
                        size = extract_tag_value(entry, "filesize")
                        entry_lines = entry.split('\n')
                        fileLocation = ""
                        for line in reversed(entry_lines):
                            line = line.strip()
                            if line and not line.startswith('#') and (':\\' in line or line.startswith('/')):
                                fileLocation = line
                                break
                        title = escape_xml(title.strip()) if title else "Unknown Title"
                        artist = escape_xml(artist.strip()) if artist else "Unknown Artist"
                        time = escape_xml(time.strip()) if time else "0"
                        size = escape_xml(size.strip()) if size else "0"
                        fileLocation = escape_xml(fileLocation.strip()) if fileLocation else ""
                        
                        
                        xmlFile.write("<TRACK TrackID='" + str(i+1) + "' Name='" + str(title) + "' Artist='" + str(artist) + "' TotalTime='" + str(time) + "' Size='" + str(size) + "' Location='" + str(fileLocation) + "'>\n</TRACK>\n")
                    xmlFile.write("</COLLECTION>\n</DJ_PLAYLISTS>\n")
                
                return send_file(output_path, as_attachment=True)
            elif extension == '.nml':
                # convert NML to XML
                # Placeholder for conversion logic
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    
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
                
                def extract_tag_value(text, tag):
                    # Try both single and double quotes
                    for quote in ["'", '"']:
                        start_tag = f'{tag}={quote}'
                        start_idx = text.find(start_tag)
                        if start_idx != -1:
                            start_idx += len(start_tag)
                            end_idx = text.find(quote, start_idx)
                            if end_idx != -1:
                                return text[start_idx:end_idx]
                    return ""
                
                output_filename = os.path.splitext(filename)[0] + '.xml'
                output_path = os.path.join(downloads_path, output_filename)
                
                with open(output_path, "w", encoding="utf-8") as xmlFile:
                    xmlFile.write("<?xml version='1.0' encoding='UTF-8'?>\n<DJ_PLAYLISTS Version='1.0.0'>\n<PRODUCT Name='rekordbox' Version='5.6.1' Company='Pioneer DJ'/>\n<COLLECTION Entries='" + str(len(entries)) + "'>\n")
                    
                    for i, entry in enumerate(entries):
                        title = extract_tag_value(entry, "TITLE")
                        artist = extract_tag_value(entry, "ARTIST")
                        time = extract_tag_value(entry, "time")
                        size = extract_tag_value(entry, "FILESIZE")
                        fileLocation = extract_tag_value(entry, "DIR")
                        
                        title = title.strip() if title else "Unknown Title"
                        artist = artist.strip() if artist else "Unknown Artist"
                        time = time.strip() if time else "0"
                        size = size.strip() if size else "0"
                        fileLocation = fileLocation.strip() if fileLocation else ""
                        
                        
                        xmlFile.write("<TRACK TrackID='" + str(i+1) + "' Name='" + str(title) + "' Artist='" + str(artist) + "' TotalTime='" + str(time) + "' Size='" + str(size) + "' Location='" + str(fileLocation) + "'>\n</TRACK>\n")
                    xmlFile.write("</COLLECTION>\n</DJ_PLAYLISTS>\n")
                return send_file(output_path, as_attachment=True)
            else:
                # convert M3U8 to XML
                # Placeholder for conversion logic
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    
                entries = []
                lines = text.split('\n')
                current_entry = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('#EXTINF'):
                        if current_entry:
                            entries.append('\n'.join(current_entry))
                        current_entry = [line]
                    elif line and current_entry:
                        current_entry.append(line)
                
                if current_entry:
                    entries.append('\n'.join(current_entry))
                
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
                
                output_filename = os.path.splitext(filename)[0] + '.xml'
                output_path = os.path.join(downloads_path, output_filename)
                
                with open(output_path, "w", encoding="utf-8") as xmlFile:
                    xmlFile.write("<?xml version='1.0' encoding='UTF-8'?>\n<DJ_PLAYLISTS Version='1.0.0'>\n<PRODUCT Name='rekordbox' Version='5.6.1' Company='Pioneer DJ'/>\n<COLLECTION Entries='" + str(len(entries)) + "'>\n")
                    
                    for i, entry in enumerate(entries):
                        entry_lines = entry.split('\n')
                        extinf_line = ""
                        fileLocation = ""
                        
                        for line in entry_lines:
                            line = line.strip()
                            if line.startswith('#EXTINF:'):
                                extinf_line = line
                            elif line and not line.startswith('#'):
                                fileLocation = line
                                break
                        
                        #ai generated
                        if extinf_line:
                            extinf_parts = extinf_line[8:]
                            comma_idx = extinf_parts.find(',')
                            if comma_idx != -1:
                                time = extinf_parts[:comma_idx]
                                artist_title = extinf_parts[comma_idx+1:]
                                if ' - ' in artist_title:
                                    artist, title = artist_title.split(' - ', 1)
                                else:
                                    artist = ""
                                    title = artist_title
                            else:
                                time = ""
                                artist = ""
                                title = ""
                        else:
                            time = ""
                            artist = ""
                            title = ""
                        
                        size = ""
                        #end of ai generated code
                        # Clean up and escape XML characters
                        title = escape_xml(title.strip())
                        artist = escape_xml(artist.strip())
                        time = escape_xml(time.strip())
                        size = escape_xml(size.strip())
                        fileLocation = escape_xml(fileLocation.strip())
                        
                        
                        xmlFile.write("<TRACK TrackID='" + str(i+1) + "' Name='" + str(title) + "' Artist='" + str(artist) + "' TotalTime='" + str(time) + "' Size='" + str(size) + "' Location='" + str(fileLocation) + "'>\n</TRACK>\n")
                    xmlFile.write("</COLLECTION>\n</DJ_PLAYLISTS>\n")
                return send_file(output_path, as_attachment=True)

        # elif convertTo == 'nml':
        #     extension = os.path.splitext(file.filename)[1].lower()
        #     if extension == '.nml':
        #         return 'File is already in NML format'
        #     elif extension == '.m3u':
        #         # convert M3U to NML
        #         # Placeholder for conversion logic
        #     elif extension == '.xml':
        #         # convert XML to NML
        #         # Placeholder for conversion logic
        #     else:
        #         # convert M3U8 to NML
        #         # Placeholder for conversion logic
        # else:
        #     extension = os.path.splitext(file.filename)[1].lower()
        #     if extension == '.m3u8':
        #         return 'File is already in M3U8 format'
        #     elif extension == '.m3u':
        #         # convert M3U to M3U8
        #         # Placeholder for conversion logic
        #     elif extension == '.xml':
        #         # convert XML to M3U8
        #         # Placeholder for conversion logic
        #     else:

if __name__ == '__main__':
    app.run(debug=True)