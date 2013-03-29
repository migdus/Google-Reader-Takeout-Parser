'''
Created on Mar 26, 2013

@author: migdus
'''
import zipfile, tempfile, Tkinter, tkFileDialog, xml.etree.ElementTree as xml, os, listparser,csv

from datetime import datetime

class csv_writer:
    def __init__(self, path):
        self.f = open(path, 'w')
        
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.f.close();
    
        
class parser:
    
    def __init__(self, master):
        self.dest_filename = 'google_takeout_parsed'
        
        self.global_dict = {}
        self.find_zip_dict_key = 'zip_path'
        self.find_dest_dict_key = 'destination_path' 
        
        
        self.widget_dict = {}
        self.main_csv_key = 'main_csv'
        self.csv_first_line_header_key = 'header_csv'
    
        master.title('Quick n\' Dirty Google Reader Takeout Parser')
        frame = Tkinter.Frame(master)
        frame.grid()
        
        textLabel = '1. Select your zip File.\n2. Check how would you like your info parsed.\n3.Select parsed files destination.\n4. Done!'
        self.mainLabel = Tkinter.Label(frame, text=textLabel)
        self.mainLabel.grid(row=0, column=0, columnspan=2)
        
        find_zip_entry_content = Tkinter.StringVar()
        select_file_text = 'Select a zip file'
        
        self.buttonFindZip = Tkinter.Button(frame, text='Find zip', command=lambda:self.select_file_path(select_file_text, self.find_zip_dict_key, find_zip_entry_content))
        self.buttonFindZip.grid(row=1, column=0)
        
        self.zip_path_field = Tkinter.Entry(frame, textvariable=find_zip_entry_content)
        self.zip_path_field.config(state=Tkinter.DISABLED)
        self.zip_path_field.grid(row=1, column=1)
        
        find_dir_entry_content = Tkinter.StringVar()
        select_dir_text = 'Select a directory'
       
        self.buttonDest = Tkinter.Button(frame, text='Destination', command=lambda:self.select_dir_path(
                                                                                                        select_dir_text, 
                                                                                                        self.find_dest_dict_key, 
                                                                                                        find_dir_entry_content))
        self.buttonDest.grid(row=2, column=0)
        
        self.dest_field = Tkinter.Entry(frame, textvariable=lambda:self.global_dict[self.find_dest_dict_key])
        self.dest_field.config(state=Tkinter.DISABLED)
        self.dest_field.grid(row=2, column=1)
        
        csv_first_line_header = Tkinter.IntVar()
        self.checkbox_csv_first_line_header = Tkinter.Checkbutton(frame, text="1st line as column name",variable=csv_first_line_header)
        self.checkbox_csv_first_line_header.configure(state='disabled')
        self.checkbox_csv_first_line_header.grid(row=4, column=0)
        self.widget_dict[self.csv_first_line_header_key] = self.checkbox_csv_first_line_header
        
        csv_checked = Tkinter.IntVar()
        self.checkbox_csv = Tkinter.Checkbutton(frame, text="CSV", variable=csv_checked,
                                                command=lambda:self.csv_checkbox_state(
                                                                                       csv_checked,
                                                                                       self.csv_first_line_header_key,                                                                                       
                                                                                       csv_first_line_header))
        self.checkbox_csv.grid(row=3, column=0)
        self.widget_dict[self.main_csv_key] = self.checkbox_csv
        
        plain_checked = Tkinter.IntVar()
        self.checkbox_plain = Tkinter.Checkbutton(frame, text="Plain text", variable=plain_checked)
        self.checkbox_plain.grid(row=3, column=1)

        
        self.buttonStart = Tkinter.Button(frame, text='Start Parsing', command=lambda:self.start_parsing(find_dir_entry_content,
                                                                                                         csv_checked,
                                                                                                         csv_first_line_header, 
                                                                                                         plain_checked))
        self.buttonStart.grid(row=5, column=0, columnspan=2)

        self.scrollbar = Tkinter.Scrollbar(frame)
        self.scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.scrollbar.grid(row=6, column=0, columnspan=2)

        self.logbox = Tkinter.Listbox(frame, yscrollcommand=self.scrollbar.set)
        self.logbox.grid(row=6, column=0, columnspan=2)
        
        self.logbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.logbox.yview)
        
        self.gui_logger("Program Started")
    
    def csv_checkbox_state(self,variable,child_key,child_key_var):
        if variable.get() == 0:
            self.widget_dict[child_key].configure(state='disabled')
            child_key_var.set(0)
        if variable.get() == 1:
            self.widget_dict[child_key].configure(state='normal')
            child_key_var.set(1)
        
    def gui_logger(self, message):
        self.logbox.insert(Tkinter.END, datetime.now().isoformat()) 
        self.logbox.insert(Tkinter.END, message)
    
    def start_parsing(self, dest_path,csv_checked, csv_first_line_header,plain_checked):
        self.gui_logger("Starting")
        if(csv_checked.get() == 1):
            self.gui_logger("CSV Option selected")
            
        if plain_checked.get() == 1:
            self.gui_logger("Plain Text Option selected")
        
        td = self.unzip(self.global_dict[self.find_zip_dict_key])
        
        files = self.search_path_files(td)
        
        for f in files:
            fileName, fileExtension = os.path.splitext(f)
            if fileExtension == '.xml':
                if(csv_checked.get() == 1):
                        flag_header_written = False
                        with open(os.path.join(dest_path.get(),self.dest_filename+'.csv'),'wb') as csvfile:
                            csvwriter=csv.writer(csvfile,delimiter=',',quotechar='"',quoting=csv.QUOTE_MINIMAL)
                            
                            parsedxml = listparser.parse(f)
                            
                            keys=parsedxml.feeds[0].keys()
                            
                            if(csv_first_line_header.get() == 1 and not flag_header_written):
                                csvwriter.writerow(keys)
                                flag_header_written = True

                            for e in parsedxml.feeds:
                                outs=''
                                for k in keys:
                                    outs+=str(e[k])
                                csvwriter.writerow(outs)
                    
                if plain_checked.get() == 1:
                    self.gui_logger("Plain Text Option selected")
                    self.gui_logger(e)
                
            
 
    def select_dir_path(self, window_title, dict_key, entry_content):
        root = Tkinter.Tk()
        root.withdraw()
        dirname = tkFileDialog.askdirectory(parent=root, initialdir="/", title=window_title)
        self.global_dict[dict_key] = dirname
        entry_content.set(dirname)
    
    def select_file_path(self, window_title, dict_key, entry_content):
        root = Tkinter.Tk()
        root.withdraw()
        file_name = tkFileDialog.askopenfilename(parent=root, initialdir="/", title=window_title)
        self.global_dict[dict_key] = file_name
        entry_content.set(file_name)
    
    def unzip(self, source):
        td = tempfile.mkdtemp()
        with zipfile.ZipFile(source) as src:
            for member in src.infolist():
                src.extract(member, td)
        return td
    
    def search_path_files(self, td):
        files = []
        full_dir_path = ''
        for (dirpath, dirname, filenames) in os.walk(td):
            files.extend(filenames)
            full_dir_path = dirpath
            if len(files) > 0:
                break
        for i in range(0, len(files)):
            files[i] = os.path.join(full_dir_path, files[i])
        return files

    def parse_xml(self, xml_path):
        
        tree = xml.parse(xml_path)
        rootElement = tree.getroot()
        entries = {}
        tag = ''
        for element in rootElement.iter('outline'):
            if element.attrib.keys() == ['text', 'title']:
                tag = element.attrib['title']
            else: 
                if element.attrib.keys() == ['xmlUrl', 'text', 'type', 'htmlUrl', 'title']:
                    if element.attrib['xmlUrl'] not in entries.keys():
                        if not element.attrib.has_key('tag'):
                            element.attrib['tag'] = []
                        
                        if not tag in element.attrib['tag']:
                            element.attrib['tag'].append(tag)
                            
                        entries[element.attrib['xmlUrl']] = element.attrib




root = Tkinter.Tk()
app = parser(root)
root.mainloop()

