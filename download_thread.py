#!/usr/bin/python
# -*- coding: utf-8 -*- 
# 
#Copyright (C) 2009 sp00b, sebnapi
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 3 of the License,
#or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
###

import threading
from time import time, sleep
from copy import copy
import urllib

class Status(object):
    """ Saves all status information
    """
    def __init__(self, id, status_queue):
        self.status_queue = status_queue
        self.id = id
        self.total_kb = 0
        self.downloaded_kb = 0
        self.rate = 0
        self.expected_time = 0
        self.filename = None
        self.url = None
        self.type = None
        self.start = time()
        self.last_status = time()
    
    def __call__(self, blocks_read, block_size, total_size):
        self.total_kb = total_size / 1024
        self.downloaded_kb = (blocks_read * block_size) / 1024
        elapsed_time = time() - self.start
        if elapsed_time != 0:
            self.rate = self.downloaded_kb / elapsed_time
            if self.rate != 0:
                self.expected_time = self.downloaded_kb / self.rate
        if self.last_status+0.2 < time():
            self.status_queue.put(copy(self))
            self.last_status = time()
    
    #def set_total_kb(total_kb):
        #self.total_kb = total_kb
        
    #def set_downloaded_kb(downloaded_kb):
        #self.downloaded_kb = downloaded_kb
        
    #def set_rate(rate):
        #self.rate = rate
        
    #def set_expected_time(expected_time):
        #self.expected_time = expected_time

class Download_Thread(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.setDaemon(1)
        self.shutdown = False
        self.parent = parent
        self.start()
        
    def run(self):
        while (not self.shutdown):
            if not self.parent.download_queue.empty():
                py_load_file = self.parent.download_queue.get()
            self.download(py_load_file)
        if self.shutdown:
            sleep(1)
            self.parent.remove_thread(self)

    def download(self, py_load_file):
        url = py_load_file.url
        type, params = py_load_file.plugin.get_file_url(url)
        status = Status(py_load_file.id, self.parent.status_queue)
        #missing wenn datei nicht auf server vorhanden
        #if type=="check":
            #return params
        #if type in 'missing':
            #self.status = "missing"
            #print "Datei auf Server nicht vorhanden: " + params
            ##im logger eintragen das datei auf server nicht vorhanden ist
            #warning("Datei auf Server nicht voblocks_readrhanden: " + url)
        if type in 'download':
            status.type = "downloading"
            #startet downloader
            status.url, status.filename = params
            urllib.urlretrieve(status.url, py_load_file.download_folder + "/" + status.filename, status)
            self.shutdown = True
