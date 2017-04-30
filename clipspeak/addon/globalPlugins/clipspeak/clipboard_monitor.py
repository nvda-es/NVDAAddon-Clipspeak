#Clipboard_monitor
#A module to monitor for clipboard changes
#By: Damien Lindley
#20th April 2017

from win32clipboard import *

class clipboard_monitor(object):
	def __init__(self):
		self.get_clipboard()

	def get_clipboard(self):
		__clipboard_data=self.enumerate_clipboard()

	def enumerate_clipboard(self):
		data={}
		OpenClipboard(None)
		format=0
		while True:
			format=EnumClipboardFormats(format)
			if format==0: break
			pos=str(format)
			data[pos]=GetClipboardData(format)
		CloseClipboard()
		return data

	def valid_data(self):
		return self.enumerate_clipboard()!={}

	def changed(self):
		if self.enumerate_clipboard()==self.__clipboard_data: return False
		self.__clipboard_data=self.enumerate_clipboard()
		return True

	__clipboard_data={}
