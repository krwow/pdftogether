from tkinter import Tk, Frame, Label, Button, Listbox, Scrollbar, END,\
    SINGLE, filedialog, StringVar, messagebox
from pypdf import PdfWriter
from pathlib import Path


class Pdftogether(Tk):
    def __init__(self):
        super().__init__()
        # Dictionary for files on listbox.
        self.files = {}
        # Warning messages.
        self.message_list_duplicate = ('File with such name has been already'
                                       ' added to list or selected file is'
                                       ' not a pdf file.')
        self.message_issue_with_file = ('There is an issue with one of the'
                                        ' files. It will be excluded from'
                                        ' merging.')
        self.message_nothing_to_do = ('There is nothing to merge as there is'
                                      ' not at least one proper pdf file on'
                                      ' list.')
        self.set_window_settings()
        self.create_widgets()

    def set_window_settings(self):
        # Window title and minimal size settings.
        self.title('pdftogether')
        self.minsize(250, 170)
        # Configure whole window resizing.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)        

    def create_widgets(self):
        # Creating listbox and frame for it.
        frm_list_with_scroll = Frame(self, bd=2)
        self.main_listbox = Listbox(frm_list_with_scroll,
                                    height = 10,
                                    width = 40,
                                    activestyle = 'dotbox',
                                    font = ('Helvetica', 9),
                                    selectmode=SINGLE)
        self.main_listbox.grid(row=0, column=0, sticky='nsew')
        # Creating scrollbar and adding it to listbox frame.
        scrollbar = Scrollbar(frm_list_with_scroll)
        scrollbar.grid(row=0, column=1, sticky='nsew')
        frm_list_with_scroll.grid(row=1, column=0, sticky='nsew', padx=(5,5),
                                pady=5)
        # Connecting scrollbar with listbox.
        self.main_listbox.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command = self.main_listbox.yview)
        # Making just listbox resizable in width, not scrollbar.
        frm_list_with_scroll.columnconfigure(0, weight=1)
        frm_list_with_scroll.rowconfigure(0, weight=1)

        # Creating top buttons and a frame for them.
        frm_top_buttons = Frame(self, bd=2)
        btn_add = Button(frm_top_buttons, text='Add (to list)', width = 20,
                        command=self.add_to_list)
        btn_add.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        btn_remove = Button(frm_top_buttons, text='Remove (from list)',
                            width = 20, command=self.remove_from_list)
        btn_remove.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        frm_top_buttons.grid(row=0, column=0, sticky='wen')
        # Configuring frame for top buttons resizing.
        frm_top_buttons.columnconfigure(0, weight=1)
        frm_top_buttons.columnconfigure(1, weight=1)

        # Adding elements for displaying number of files and a frame for them.
        frm_labels = Frame(self, bd=2)
        lbl_txt_count = Label(frm_labels, text='Number of added pdf files: ')
        lbl_txt_count.grid(row=0, column=0, sticky='w', padx = (15,0))
        self.string_var = StringVar(self, value=0)
        lbl_count = Label(frm_labels, textvariable=self.string_var)
        lbl_count.grid(row=0, column=1, sticky='w')
        frm_labels.grid(row=3, column=0, sticky='ews')

        # Creating button at the bottom and a frame for it.
        frm_bottom_buttons = Frame(self, bd=2)
        btn_build = Button(frm_bottom_buttons, text='Build', width = 20,
                        command=self.build_pdf)
        btn_build.grid(row=0, column=0, sticky='ews', padx=5, pady=5)
        frm_bottom_buttons.grid(row=4, column=0, sticky='ews')
        # Configuring frame with bottom button resizing. 
        frm_bottom_buttons.columnconfigure(0, weight=1)
    
    def add_to_list(self):
        # Always show additional .url files no matter what is set...
        # It should filter out just pdf files, so there wouldn't be need for
        # checking file extension later.
        filetypes_pdf = [('PDF files', '*.pdf')]
        name_and_path = filedialog.askopenfilename(title='Select PDF file',
                                                   filetypes=filetypes_pdf)
        # Proceed if any file was selected.
        if name_and_path != '':
            # os.path instead?
            name = Path(name_and_path).name
            file_extension = Path(name_and_path).suffix
            # Checking if there hasn't been already file with such filepath
            # and filename in a dict and if the extension of file is pdf.
            if name_and_path not in self.files.values() and file_extension\
                == '.pdf':
                # Adding key with a filename and an extension to dictionary.
                # If the name already exists, but filepath is different, then
                # item on listbox and key in dictionary is altered. 
                # Value is the full path with a filename and an extension.
                if name in self.files:
                    name = name + ' (' + name_and_path + ')'
                self.files[name] = name_and_path                    
                # Adding filename with extension at the end of listbox.
                self.main_listbox.insert(END, name)
                number_of_files_str = str(len(self.files))
                # Displaying the current number of files in dictionary.
                self.string_var.set(number_of_files_str)
                # Clearing selection on listbox.
                self.main_listbox.selection_clear(0, 'end')
                # Setting last element as selected.
                self.main_listbox.selection_set('end', 'end')
            else:
                messagebox.showwarning('Warning', self.message_list_duplicate)

    def remove_from_list(self):
        selected_on_listbox = self.main_listbox.curselection()
        # Move on if anything is selected on listbox.
        if len(selected_on_listbox) > 0:
            # Getting filename with extension from listbox.
            listbox_name = self.main_listbox.get(selected_on_listbox)
            # Removing element from listbox.
            self.main_listbox.delete(selected_on_listbox)
            # Removing file from dictionary.
            # Create a function? #
            del self.files[listbox_name]
            number_of_files_str = str(len(self.files))
            self.string_var.set(number_of_files_str)
            self.main_listbox.selection_clear(0, 'end')
            self.main_listbox.selection_set('end', 'end')

    def build_pdf(self):
        filetypes_pdf = (('PDF files', '*.pdf'),)
        # If there's any file on a listbox, go on.
        if self.main_listbox.size() > 0:
            # Using pypdf.
            merger = PdfWriter()
            # Getting every path with filename from dictionary and appending
            # it to a list.
            for key in self.files.keys():
                name_and_path = self.files[key]
                # Adding only proper pdf files to merging.
                try:
                    merger.append(name_and_path)
                except:
                    message_txt = self.message_issue_with_file + '\n\nFile: '\
                        + name_and_path
                    messagebox.showwarning('Warning', message_txt)
            # Getting total number of pages from proper pdf files.
            number_of_pages = len(merger.pages)
            output_name_and_path = None
            # Displaying file dialog only if there's at least one proper page.
            if number_of_pages > 0:
                output_name_and_path = filedialog.asksaveasfile(
                    title='Save merged file', filetypes=filetypes_pdf,
                    initialfile='merged', defaultextension='.pdf')
            else:
                messagebox.showwarning('Warning', self.message_nothing_to_do)
            # Saving file if a place to save a file was chosen.
            if output_name_and_path is not None:
                merger.write(output_name_and_path.name)
            merger.close()


if __name__ == '__main__':
    app = Pdftogether()
    app.mainloop()