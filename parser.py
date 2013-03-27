'''
Created on Mar 26, 2013

@author: migdus
'''
import zipfile,tempfile,Tkinter, tkFileDialog
global_dict = {}

class parser:
    
    def __init__(self,master):
        master.title('Quick n\' Dirty Google Reader Takeout Parser')
        frame = Tkinter.Frame(master)
        frame.grid()
        
        textLabel = '1. Select your zip File.\n2. Check how would you like your info parsed.\n3.Select parsed files destination.\n4. Done!'
        self.mainLabel = Tkinter.Label(frame,text=textLabel)
        self.mainLabel.grid(row=0,column=0,columnspan=2)
        
        find_zip_entry_content=Tkinter.StringVar()
        select_file_text= 'Select a zip file'
        find_zip_dict_key = 'zip_path'
        self.buttonFindZip = Tkinter.Button(frame, text='Find zip',command=lambda:self.select_file_path(select_file_text,find_zip_dict_key,find_zip_entry_content))
        self.buttonFindZip.grid(row=1,column=0)
        
        self.zip_path_field=Tkinter.Entry(frame, textvariable=find_zip_entry_content)
        self.zip_path_field.config(state=Tkinter.DISABLED)
        self.zip_path_field.grid(row=1,column=1)
        
        find_dir_entry_content=Tkinter.StringVar()
        select_dir_text = 'Select a directory'
        find_dest_dict_key = 'destination_path' 
        self.buttonDest = Tkinter.Button(frame,text='Destination',command=lambda:self.select_dir_path(select_dir_text, find_dest_dict_key,find_dir_entry_content))
        self.buttonDest.grid(row=2,column=0)
        
        self.dest_field=Tkinter.Entry(frame, textvariable=lambda:global_dict[find_dest_dict_key])
        self.dest_field.config(state=Tkinter.DISABLED)
        self.dest_field.grid(row=2,column=1)
        
        csv_checked = Tkinter.IntVar()
        self.checkbox_csv = Tkinter.Checkbutton(frame, text="CSV", variable=csv_checked)
        self.checkbox_csv.grid(row=3,column=0)
        
        plain_checked = Tkinter.IntVar()
        self.checkbox_plain = Tkinter.Checkbutton(frame, text="Plain text", variable=plain_checked)
        self.checkbox_plain.grid(row=3,column=1)

    def select_dir_path(self,window_title,dict_key,entry_content):
        root = Tkinter.Tk()
        root.withdraw()
        dirname = tkFileDialog.askdirectory(parent=root,initialdir="/",title=window_title)
        global_dict[dict_key]=dirname
        entry_content.set(dirname)
        return
    
    def select_file_path(self,window_title,dict_key,entry_content):
        root = Tkinter.Tk()
        root.withdraw()
        file_name=tkFileDialog.askopenfilename(parent=root,initialdir="/",title=window_title)
        global_dict[dict_key] = file_name
        entry_content.set(file_name)
        return
    
    def unzip(self,source):
        td = tempfile.mkdtemp()
        with zipfile.ZipFile(source) as src:
            for member in src.infolist():
                src.extract(member,td)
        return td


root =Tk()
app=parser(root)
root.mainloop()

