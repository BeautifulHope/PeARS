#!/usr/bin/env/python

import Tkinter as tk
from Tkinter import *
import Tkconstants, tkFileDialog
from threading import Thread
import os
import subprocess

class indexer_gui(Toplevel):
  def __init__(self,parent):
    Toplevel.__init__(self,parent)
    self.parent = parent
    self.initialise()

  def initialise(self):
    self.configure(bg = '#ffffff')
    self.grid()
    self.index_file_img = PhotoImage(file = './pears/static/gui-index-file.gif')
    self.index_history_img = PhotoImage(file = './pears/static/gui-index-history.gif')
    self.index_button_img = PhotoImage(file = './pears/static/gui-index-window-button.gif')
    self.separator_img = PhotoImage(file = './pears/static/gui-separator.gif')
    self.dir_img = PhotoImage(file = './pears/static/small-folder.gif')

    '''Beautify with pretty pictures'''
    label1 = Label(self, image=self.index_history_img, border=0)
    label1.image = self.index_history_img
    label1.grid(row = 0, column = 0, sticky=N)

    history_text = Message(self, text="Directly index pages from your Firefox browsing history.", border=0, bg='#ffffff', fg='#000000')
    history_text.grid(row = 0, column = 1, sticky=N)

    separator = Label(self, image=self.separator_img, border=0)
    separator.image = self.separator_img
    separator.grid(row = 0, column = 2, rowspan=3, sticky=N)

    label2 = Label(self, image=self.index_file_img, border=0)
    label2.image = self.index_file_img
    label2.grid(row = 0, column = 3, columnspan=2, sticky=N)

    urls_text = Message(self, text="Index pages from a .txt file, one url per line.", border=0, bg='#ffffff', fg='#000000')
    urls_text.grid(row = 0, column = 5, sticky=N)

    '''Define number of pages to index'''
    self.entryNumVariable = tk.StringVar()
    self.entry_history = tk.Entry(self,textvariable=self.entryNumVariable, width=23)
    self.entry_history.bind('<Button-1>', self.ClearHistoryBox)
    self.entry_history.grid(column=0,row=1,sticky='WN')
    self.entryNumVariable.set(u"Number of pages to index")

    '''Define checkbox for caching option (history)'''
    self.chk_history = tk.IntVar()
    index_history_checkbox = tk.Checkbutton(self,text="Cache", bg='#ffffff',\
        fg='#000000', highlightthickness=0, bd=0, variable=self.chk_history)
    index_history_checkbox.grid(column=1,row=1, sticky='NW')

    '''Define location of file to index'''
    self.entryFileVariable = tk.StringVar()
    self.entry_file = tk.Entry(self,textvariable=self.entryFileVariable, width=20)
    self.entry_file.bind('<Button-1>', self.ClearFileBox)
    self.entry_file.grid(column=3,row=1,sticky='EN')
    self.entryFileVariable.set(u"Location of URL file")

    '''Define button to choose file'''
    select_file_button = tk.Button(self,image=self.dir_img, command=self.OnSelectFileButtonClick, bg='#ffffff',\
        fg='#000000', relief='raised')
    select_file_button.grid(column=4,row=1, sticky='NW')

    '''Define checkbox for caching option (file)'''
    self.chk_file = tk.IntVar()
    index_file_checkbox = tk.Checkbutton(self,text="Cache", bg='#ffffff',\
        fg='#000000', highlightthickness=0, bd=0, variable=self.chk_file)
    index_file_checkbox.grid(column=5,row=1, sticky='NW')

    '''Define button to press to start indexing (history)'''
    index_history_button = tk.Button(self,image=self.index_button_img, command=self.OnHistoryButtonClick, bg='#ffffff',\
        fg='#000000', bd=0)
    index_history_button.grid(column=0,columnspan=2,row=2, sticky='NW')

    '''Define button to press to start indexing (file)'''
    index_file_button = tk.Button(self,image=self.index_button_img, command=self.OnFileButtonClick, bg='#ffffff',\
        fg='#000000', relief='ridge')
    index_file_button.grid(column=3,columnspan=3,row=2, sticky='N')
 
    '''Define text box for logging'''  
    self.logging = tk.Text(self, height=3)
    self.logging.grid(column=0,row=5,columnspan=6,pady=(0, 10))

    #self.resizable(False,False)
    self.update()
    self.geometry(self.geometry())

  def ThreadedHistoryIndexing(self):
    num_pages = self.entryNumVariable.get()
    if num_pages.isdigit():
      if self.chk_history.get() == 0:
        msg="Now indexing {} pages without caching option. This may take a few minutes...\n".format(num_pages)
        self.logging.insert(tk.END,msg)
        h=subprocess.Popen(["python", "indexer.py", "--history",num_pages],\
            shell=False).wait()
        self.logging.insert(tk.END,"Finished indexing. Thank you.")
      else:
        msg="Now indexing {} pages with caching option. This may take a few minutes...\n".format(num_pages)
        self.logging.insert(tk.END,msg)
        hc=subprocess.Popen(["python", "indexer.py",\
          "--history",num_pages,"--cache"], shell=False).wait()
        self.logging.insert(tk.END,"Finished indexing. Thank you.")
    else:
      self.entryNumVariable.set("Number of pages to index")

  def ThreadedFileIndexing(self):
    file_name = self.entryFileVariable.get()
    if self.chk_history.get() == 0:
      self.logging.insert(tk.END,"Now indexing",file_name,"without caching option")
      h=subprocess.Popen(["python", "indexer.py", "--file", file_name], shell=False).wait()
    else:
      self.logging.insert(tk.END,"Now indexing",file_name,"with caching option")
      hc=subprocess.Popen(["python", "indexer.py", "--file", file_name, "--cache"], shell=False).wait()

  def OnHistoryButtonClick(self):
    Thread(target=self.ThreadedHistoryIndexing).start()

  def OnFileButtonClick(self):
    Thread(target=self.ThreadedFileIndexing).start()

  def OnSelectFileButtonClick(self):
    filename = tkFileDialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("txt files","*.txt"),("all files","*.*")))
    self.entryFileVariable.set(filename)

  def ClearHistoryBox(self,event):
    self.entryNumVariable.set("")

  def ClearFileBox(self,event):
    self.entryFileVariable.set("")



class pears_gui(tk.Tk):
  def __init__(self,parent):
    tk.Tk.__init__(self,parent)
    self.parent = parent
    self.initialise()

  def on_closing(self):
    if self.search_process is not None:
      print "Search running on pid...",self.search_process.pid, "Killing it..."
      self.search_process.terminate()
      print "Killing process on port 5000..."
      subprocess.Popen(["fuser", "-k", "5000/tcp"], shell=False)
    print "Goodbye!"
    self.destroy()

  def initialise(self):
    self.search_process=None
    self.wm_protocol("WM_DELETE_WINDOW", self.on_closing)
    self.configure(bg = '#ffffff')
    self.grid()
    self.logo = PhotoImage(file = './pears/static/gui-logo-main.gif')
    self.index = PhotoImage(file = './pears/static/gui-write.gif')
    self.search = PhotoImage(file = './pears/static/gui-network.gif')

    label1 = Label(self, image=self.logo, border=0)
    label1.image = self.logo
    label1.grid(row = 0, column = 0, rowspan = 2, sticky=NW, padx=(7,0))


    index_button = tk.Button(self,image=self.index, command=self.OnIndexButtonClick, bg='#ffffff',\
        fg='#000000', relief='ridge', border=0)
    index_button.grid(column=1,row=0, sticky='N', pady=(4,2), padx=(0,7))

    search_button = tk.Button(self,image=self.search, command=self.OnSearchButtonClick,\
        fg='#000000', relief='ridge', border=0)
    search_button.grid(column=1,row=1, sticky='N', pady=(2,4), padx=(0,7))


    '''Define text box for logging'''
    self.logging = tk.Text(self, height=3, width=60)
    self.logging.grid(column=0,row=2,columnspan=2,pady=(0, 5))
 
    self.grid_columnconfigure(0,weight=1)
    self.resizable(False,False)
    self.update()
    self.geometry(self.geometry())

  def OnIndexButtonClick(self):
    self.logging.insert(tk.END,"Opening the indexer...")
    indexer=indexer_gui(self)
    indexer.title('PeARS indexer')

  def ThreadedSearch(self):
    msg="Opening search server. Please go to your browser and visit http://0.0.0.5000/."
    self.logging.insert(tk.END,msg)
    self.search_process=subprocess.Popen(["python", "run.py"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  def OnSearchButtonClick(self):
    search_thread = Thread(target=self.ThreadedSearch)
    search_thread.setDaemon(True)
    search_thread.start()

if __name__ == "__main__":
  gui = pears_gui(None)
  gui.title('PeARS')
  gui.mainloop()
