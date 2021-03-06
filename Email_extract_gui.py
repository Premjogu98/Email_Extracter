import wx
from wx import html2
import urllib.request
import urllib.parse
import requests
import html
import time
import sys, os
import re
from datetime import datetime
from concurrent import futures
import codecs

thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)

list_of_urls = []
Total_url_collected = 0
Total_url_done = 0
Total_url_error = 0
Total_email_found = 0
class MyApp(wx.App):
    def OnInit(self):
        NavBar(None , "Email Extracter").Show()
        return True


# class WebFrame():
#     def __init__(self , parent , title):
#         super().__init__(parent=None, title=title,pos = (110,90), size =(1300,700) ,style = wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER)

#         self._browser = html2.WebView.New(self,size=(800, 565), pos=(10, 58))
#         self._browser.LoadURL("")  # home page
#         self._bar = NavBar(self , self._browser)

#         sizer = wx.BoxSizer(wx.VERTICAL)
#         sizer.Add(self._bar , 0 , wx.EXPAND)
        
#         self.SetSizer(sizer)

#         self.Bind(html2.EVT_WEBVIEW_TITLE_CHANGED , self.OnTitle)

#     def OnTitle(self , event):
#         self.Title = event.GetString()


class NavBar(wx.Frame):
    def __init__(self , parent , title):
        super().__init__(parent=None, title=title,pos = (110,90), size =(1300,700) ,style = wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER)

        self.panel = wx.Panel(self,size=(1300, 700), pos=(0, 0), style=wx.SIMPLE_BORDER)

        self._url = wx.TextCtrl(self.panel ,size=(580, 30), pos=(20, 10))
        self._url.SetHint("Enter URL Here....")
        font = wx.Font(13, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self._url.SetFont(font)

        self.collected_email = wx.TextCtrl(self.panel,size = (400,565),pos=(865, 58),style = wx.TE_MULTILINE)
        self.collected_email.SetHint("Collected Email's Gonna show Here")
        font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.collected_email.SetFont(font)

        self.collected_url = wx.TextCtrl(self.panel,size = (820,565),pos=(20, 58),style = wx.TE_MULTILINE)
        self.collected_url.SetHint("Collected urls's Gonna show Here")
        font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.collected_url.SetFont(font)

        self.Exit_btn = wx.Button(self.panel, label='EXIT', pos=(1150, 10),size = (100,30),style=wx.NO_BORDER)
        font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.Exit_btn.SetFont(font)
        self.Exit_btn.SetCursor(wx.Cursor(wx.CURSOR_SPRAYCAN))
        self.Exit_btn.Bind(wx.EVT_BUTTON, self.exit)
        self.Exit_btn.SetForegroundColour('White')
        self.Exit_btn.SetBackgroundColour('#FF1313')

        self.save_emails_btn = wx.Button(self.panel, label="Save email's", pos=(1020, 10),size = (120,30),style=wx.NO_BORDER)
        font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.save_emails_btn.SetFont(font)
        self.save_emails_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.save_emails_btn.Bind(wx.EVT_BUTTON, self.save_emails)
        self.save_emails_btn.SetForegroundColour('black')
        self.save_emails_btn.SetBackgroundColour('#55FFDE')

        self.save_file_path = wx.StaticText(self.panel,pos=(15, 630))
        font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.save_file_path.SetFont(font)
        self.save_file_path.SetForegroundColour('Blue')

        self.clear_btn = wx.Button(self.panel, label='Clear', pos=(610, 12),size = (80,29))
        font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.clear_btn.SetFont(font)
        self.clear_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.clear_btn.Bind(wx.EVT_BUTTON, self.clear_textarea)
        self.clear_btn.SetForegroundColour('black')
        self.clear_btn.SetBackgroundColour('white')

        self.file_upload_btn = wx.Button(self.panel, label='Upload URL File', pos=(870, 10),size = (140,30),style=wx.NO_BORDER)
        font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.file_upload_btn.SetFont(font)
        self.file_upload_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.file_upload_btn.Bind(wx.EVT_BUTTON, self.upload_links)
        self.file_upload_btn.SetForegroundColour('black')
        self.file_upload_btn.SetBackgroundColour('#FFBE28')

        self.Go_btn = wx.Button(self.panel, label='GO', pos=(760, 10),size = (100,30),style=wx.NO_BORDER)
        font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.Go_btn.SetFont(font)
        self.Go_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND)) # cursor on hover
        self.Go_btn.Bind(wx.EVT_BUTTON, self.go_btn)
        self.Go_btn.SetForegroundColour('black')
        self.Go_btn.SetBackgroundColour('#1CFF00')

        self.Collected_email_count_lbl = wx.StaticText(self.panel,pos=(615, 628))
        self.Collected_email_count_lbl.SetLabel('Total Email Found: 0') 
        font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.Collected_email_count_lbl.SetFont(font)
        self.Collected_email_count_lbl.SetForegroundColour('#000AFF')

        self.URL_done_count_lbl = wx.StaticText(self.panel,pos=(840, 628))
        self.URL_done_count_lbl.SetLabel('URL Done: 0 / 0') 
        font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.URL_done_count_lbl.SetFont(font)
        self.URL_done_count_lbl.SetForegroundColour('#108D00')

        self.URL_error_count_lbl = wx.StaticText(self.panel,pos=(1030, 628))
        self.URL_error_count_lbl.SetLabel('URL Error: 0 / 0') 
        font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.URL_error_count_lbl.SetFont(font)
        self.URL_error_count_lbl.SetForegroundColour('Red')

        

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.panel , proportion=0 , flag=wx.ALL , border=0)
        self.SetSizer(sizer)
        
    def go_btn(self , event):
        thread_pool_executor.submit(self.onEnter)

    def onEnter(self):
        # self.Collected_email_count_lbl
        self.save_file_path.Hide()
        if str(self._url.Value) != '':
            del list_of_urls[:] # Clear list
            list_of_urls.append(str(self._url.Value))
        count = 1
        if len(list_of_urls) != 0:
            self.collected_email.SetValue('')
            global Total_url_collected
            global Total_email_found
            global Total_url_done
            global Total_url_error
            Total_email_found = 0
            Total_url_collected = 0
            Total_url_done = 0
            Total_url_error = 0
            Total_url_collected = int(len(list_of_urls))
            self.collected_url.SetValue("")
            font = wx.Font(12, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
            self.collected_url.SetFont(font)
            for url in list_of_urls:
                self.collected_url.AppendText(f'{url}\n')
            for url in list_of_urls:
                wx.CallAfter(self.scraping_things, str(url))
                time.sleep(2)
                count += 1
            wx.MessageBox(' All Urls Done ','Email Extracter', wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox(' -_o  Enter URL Please  -_o ','Email Extracter', wx.OK | wx.ICON_ERROR)

    def scraping_things(self,url):
        global Total_url_collected
        global Total_url_error
        global Total_url_done
        global Total_email_found
        try:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
            headers = {'User-Agent': user_agent}
            request = urllib.request.Request(str(url), None, headers)  # The assembled request
            response = urllib.request.urlopen(request)
            html_data = response.read()
            Total_url_done += 1
        except:
            print('Error While Navigating URL')
            Total_url_error += 1
            time.sleep(2)
        Email_list = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9_.+-]+\.[a-zA-Z]+)", str(html_data))
        if len(Email_list)!= "":
            remove_dup_email = []
            [remove_dup_email.append(a) for a in Email_list if a not in remove_dup_email]
            for email in remove_dup_email:
                self.collected_email.AppendText(f'{email}\n')
                Total_email_found += 1
                self.Collected_email_count_lbl.SetLabel(f'Total Email Found: {str(Total_email_found)}')
        else:
            self.collected_email.SetValue('No Email Found')
        self.URL_done_count_lbl.SetLabel(f'URL Done: {str(Total_url_done)} / {str(Total_url_collected)}')
        self.URL_error_count_lbl.SetLabel(f'URL Error: {str(Total_url_error)} / {str(Total_url_collected)}') 

    def exit(self,event):
        dlg = wx.MessageDialog(None, "Kya Aap Ko yaha Se Bahar Prasthan (EXIT) karna Hai !!!!", 'Email Extracter', wx.YES_NO | wx.ICON_WARNING)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            self.Destroy()
            sys.exit()
    
    def save_emails(self,event):
        if str(self.collected_email.GetValue()) != "": 
            self.save_file_path.Show()
            now = datetime.now()
            date_time = now.strftime("%Y%m%d%H%M%S")
            f = open(f"Scraped Email List {str(date_time)}.txt", "w")
            f.write(str(self.collected_email.Value))
            f.close()
            self.save_file_path.SetLabel(f'File Saved: {str(os.getcwd())}') 
        else:
            wx.MessageBox(' -_o  Nothing To Save  -_o ','Email Extracter', wx.OK | wx.ICON_ERROR)

    def clear_textarea(self,event):
        self._url.SetValue('')
        self.collected_email.SetValue('')
    
    def upload_links(self,event):
        del list_of_urls[:] # Clear list
        openFileDialog = wx.FileDialog(self.panel, "Open", "", "", "Text Files (*.txt)|*.txt", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        # print(openFileDialog.GetPath())
        if str(openFileDialog.GetPath()) != '':
            with codecs.open(str(openFileDialog.GetPath()), 'r', encoding='utf8') as f:
                urls_list = f.readlines()
                for urls in urls_list:
                    list_of_urls.append(urls)
                print(list_of_urls)
if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()

