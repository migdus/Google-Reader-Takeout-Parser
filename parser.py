'''
Created on Mar 26, 2013

@author: migdus
'''
import zipfile, tempfile, Tkinter, tkFileDialog, xml.etree.ElementTree as xml, os, listparser,csv

from datetime import datetime
from zipfile import BadZipfile

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
        
        self.path_dict = {}
        self.FIND_ZIP_DICT_KEY = 'zip_path'
        self.FIND_DEST_DICT_KEY = 'destination_path' 
        
        
        self.widget_dict = {}
        self.MAIN_CSV_WIDGET_KEY = 'main_csv'
        self.CSV_FIRST_LINE_HEADER_KEY = 'header_csv'
    
        master.title('Quick n\' Dirty Google Reader Takeout Parser')
        frame = Tkinter.Frame(master)
        frame.grid(padx=(10,10),pady=(10,10))
        
        find_zip_entry_content = Tkinter.StringVar()
        select_file_text = 'Select a zip file'
        
        self.find_zip_button = Tkinter.Button(frame, text='Find zip', 
                                            command=lambda:self.select_file_path(
                                                                                 select_file_text, 
                                                                                 self.FIND_ZIP_DICT_KEY, 
                                                                                 find_zip_entry_content))
        self.find_zip_button.grid(row=1, column=0)
        
        self.zip_path_field = Tkinter.Entry(frame, textvariable=find_zip_entry_content)
        self.zip_path_field.config(state=Tkinter.DISABLED)
        self.zip_path_field.grid(row=1, column=1)
        
        find_dir_entry_content = Tkinter.StringVar()
        select_dir_text = 'Select a directory'
       
        self.destination_button = Tkinter.Button(frame, text='Destination', command=lambda:self.select_dir_path(
                                                                                                        select_dir_text, 
                                                                                                        self.FIND_DEST_DICT_KEY, 
                                                                                                        find_dir_entry_content))
        self.destination_button.grid(row=2, column=0)
        
        self.dest_field = Tkinter.Entry(frame, textvariable=find_dir_entry_content)
        self.dest_field.config(state=Tkinter.DISABLED)
        self.dest_field.grid(row=2, column=1)
        
        csv_first_line_header = Tkinter.IntVar()
        self.checkbox_csv_first_line_header = Tkinter.Checkbutton(frame, text="1st line as column name",variable=csv_first_line_header)
        self.checkbox_csv_first_line_header.configure(state='disabled')
        self.checkbox_csv_first_line_header.grid(row=4, column=0)
        self.widget_dict[self.CSV_FIRST_LINE_HEADER_KEY] = self.checkbox_csv_first_line_header
    
        csv_checked = Tkinter.IntVar()
        self.checkbox_csv = Tkinter.Checkbutton(frame, text="CSV", variable=csv_checked,
                                                command=lambda:self.csv_checkbox_state(
                                                                                       csv_checked,
                                                                                       self.CSV_FIRST_LINE_HEADER_KEY,                                                                                       
                                                                                       csv_first_line_header))
        self.checkbox_csv.grid(row=3, column=0)
        self.widget_dict[self.MAIN_CSV_WIDGET_KEY] = self.checkbox_csv
        
        plain_checked = Tkinter.IntVar()
        self.checkbox_plain = Tkinter.Checkbutton(frame, text="Plain text", variable=plain_checked)
        self.checkbox_plain.grid(row=3, column=1)

        
        self.start_button = Tkinter.Button(frame, text='Start Parsing', 
                                           command=lambda:self.start_parsing(find_dir_entry_content,
                                                                             csv_checked,
                                                                             csv_first_line_header, 
                                                                             plain_checked))
        self.start_button.grid(row=5, column=0, columnspan=2)

        self.scrollbar = Tkinter.Scrollbar(frame)
        self.scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.scrollbar.grid(row=6, column=0, columnspan=2)
        
        self.logbox = Tkinter.Listbox(frame, yscrollcommand=self.scrollbar.set)
        self.logbox.grid(row=6, column=0, columnspan=2,sticky=Tkinter.E+Tkinter.W)
        self.logbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.logbox.yview)

    def gui_logger(self, message):
        self.logbox.insert(Tkinter.END, datetime.now().isoformat().split('.')[0]+" "+message) 
        
    def csv_checkbox_state(self,variable,child_key,child_key_var):
        if variable.get() == 0:
            self.widget_dict[child_key].configure(state='disabled')
            child_key_var.set(0)
        if variable.get() == 1:
            self.widget_dict[child_key].configure(state='normal')
            child_key_var.set(1)
    
    def start_parsing(self, dest_path,csv_checked, csv_first_line_header,plain_checked):
        try:
            
            td = self.unzip(self.path_dict[self.FIND_ZIP_DICT_KEY])
            
            files = self.search_path_files(td)
            
            flag_subscriptions_xml_found = False
            destination_filename = self.dest_filename+'_subscriptions.csv'
            
            for f in files:
                fileName, fileExtension = os.path.splitext(f)
                if fileName.find('subscriptions')>=0 and fileExtension == '.xml':
                    flag_subscriptions_xml_found = True
                    
                    if(csv_checked.get() == 1):
                            flag_header_written = False
                            with open(os.path.join(dest_path.get(),destination_filename),'wb') as csvfile:
                                csv_writer=csv.writer(csvfile,delimiter=',',quotechar='"',quoting=csv.QUOTE_ALL)
                                
                                parsedxml = listparser.parse(f)
                                
                                keys=parsedxml.feeds[0].keys()
                                
                                if(csv_first_line_header.get() == 1 and not flag_header_written):
                                    csv_writer.writerow(keys)
                                    flag_header_written = True
    
                                for e in parsedxml.feeds:
                                    row = []
                                    for k in keys:
                                        if type(e[k]) is list:
                                            row.append(self.list_to_string(e[k]))
                                        else:
                                            row.append(e[k])
                                    csv_writer.writerow(row)
                            
                            self.gui_logger("File written: "+destination_filename)
                    
            
            if flag_subscriptions_xml_found is False:
                self.gui_logger("Error: subscriptions.xml not found in zip file.")
                                    
            self.gui_logger("Done!")
        
        except BadZipfile:
            self.gui_logger("Error: File is not a zip file.")

    def list_to_string(self,l):
        
        string_list = ""
        
        if len(l)>0:
            tempstr=''
            for ele in l:
                if type(ele) is list:
                    ele=self.list_to_string(ele)
                tempstr+=ele+','
                string_list=tempstr[:-1]
        return string_list

 
    def select_dir_path(self, window_title, dict_key, entry_content):
        root = Tkinter.Tk()
        root.withdraw()
        dir_name = tkFileDialog.askdirectory(parent=root, initialdir="/", title=window_title)
        self.path_dict[dict_key] = dir_name
        entry_content.set(dir_name)
    
    def select_file_path(self, window_title, dict_key, entry_content):
        root = Tkinter.Tk()
        root.withdraw()
        file_name = tkFileDialog.askopenfilename(parent=root, initialdir="/", title=window_title)
        self.path_dict[dict_key] = file_name
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
root.resizable(0,0)
root.mainloop()

