#Clipboard_monitor
#A module to monitor for clipboard changes
#By: Damien Lindley
#20th April 2017

from win32clipboard import *
from logHandler import log

class clipboard_monitor(object):
	def __init__(self):
		log.debug("Initialising clipboard monitor.")
		self.get_clipboard()

	def get_clipboard(self):
		log.debug("Enumerating clipboard data...")
		__clipboard_data=self.enumerate_clipboard()

	def enumerate_clipboard(self):
		data={}
		log.debug("Opening the clipboard for enumeration.")
		OpenClipboard(None)
		format=0
		while True:
			try:
				format=EnumClipboardFormats(format)
				log.debug("Retrieving clipboard format: %d"%format)
				if format==0: break
				pos=str(format)
				log.debug("Retrieving data for format %s"%pos)
				data[pos]=GetClipboardData(format)
				log.debug("Data retrieved: %r"%data[pos])
			except:
				log.debug("Cannot retrieve value. Moving on.")
				continue
		log.debug("Closing clipboard.")
		CloseClipboard()
		return data

	def valid_data(self):
		return self.enumerate_clipboard()!={}

	def changed(self):
		if self.enumerate_clipboard()==self.__clipboard_data: return False
		log.debug("Clipboard data has changed. Updating cached data...")
		self.__clipboard_data=self.enumerate_clipboard()
		return True

	__clipboard_data={}
