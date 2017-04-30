#Clipspeak
#An addon to monitor and speak messages relating to clipboard operations.
#By: Damien Lindley
#19th April 2017

import globalPluginHandler
import ui
import api
import clipboard_monitor

from controlTypes import *

#Constants

#Clipboard content: What are we working with?
cc_none=0
cc_text=1
cc_read_only_text=2
cc_file=3
cc_list=4
cc_other=5

#Clipboard mode: What are we doing?
cm_none=0
cm_cut=1
cm_copy=2
cm_paste=3

#Not strictly clipboard, but...
cm_undo=4
cm_select_all=5

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	#Script functions.

	def script_cut(self, gesture):
		gesture.send()
		self.speak_appropriate_message(cm_cut)

	def script_copy(self, gesture):
		gesture.send()
		self.speak_appropriate_message(cm_copy)

	def script_paste(self, gesture):
		gesture.send()
		if not self.__clipboard.valid_data(): return
		self.speak_appropriate_message(cm_paste)

	def script_undo(self, gesture):
		gesture.send()
		self.speak_appropriate_message(cm_undo)

	def script_select_all(self, gesture):
		gesture.send()
		self.speak_appropriate_message(cm_select_all)

	#Internal functions: Examines our environment so we can speak the appropriate message.

	def speak_appropriate_message(self, cm_flag):
		cc_flag=self.examine_focus()

		#Todo: If we can validate whether or not a control can work with the clipboard, we can return an invalid message here.
		if cc_flag==cc_none: return

		#Pick a word suitable to the content.
		word=_("text")
		if cc_flag==cc_file: word=_("file")
		if cc_flag==cc_list: word=_("item")

		#Validate and speak.
		if cm_flag==cm_undo and self.can_undo(cc_flag): ui.message(_("Undo"))
		if cm_flag==cm_select_all and self.can_select(cc_flag): ui.message(_("Select All"))
		if cm_flag==cm_cut and self.can_cut(cc_flag):
			if not self.__clipboard.changed():
				ui.message(_("No change."))
				return
			ui.message(_("Cut %s to clipboard"%word))
		if cm_flag==cm_copy and self.can_copy(cc_flag):
			if not self.__clipboard.changed():
				ui.message(_("No change."))
				return
			ui.message(_("Copy %s to clipboard"%word))
		if cm_flag==cm_paste and self.can_paste(cc_flag): ui.message(_("Pasted %s from clipboard"%word))

	def examine_focus(self):
		focus=api.getFocusObject()

		#Skip Mozilla windows, as they have their own handlers.
		if focus.windowClassName=="MozillaWindowClass": return cc_none

		#Check for an explorer/file browser window.
		#Todo: Is this an accurate method?
		if focus.windowClassName=="DirectUIHWND": return cc_file

		#Check for a list item.
		if focus.role==ROLE_LISTITEM: return cc_list

		#If we're looking at text...
		if focus.role==ROLE_EDITABLETEXT or focus.role==ROLE_DOCUMENT:

			#Retrieve the states in case we're read-only.
			states=focus.states
			for state in states:
				if state==STATE_READONLY: return cc_read_only_text

			#Otherwise, we're just an ordinary text field.
			return cc_text

		#Comboboxes
		if focus.role==ROLE_COMBOBOX:

			#Again, we need to evaluate states to make sure we're editable.
			states=focus.states
			for state in states:
				if state==STATE_EDITABLE: return cc_text

		#Todo: Other control types we need to check?
		return cc_none

	#Validation functions: In case we need to extend the script to allow more control/window types etc.
	#Todo: Can we check a control to see if it enables these operations? For instance whether a list enables copy or a text field allows select all?

	def can_undo(self, cc_flag):
		if cc_flag==cc_read_only_text: return False
		return True

	def can_select(self, cc_flag):
		return True

	def can_cut(self, cc_flag):
		if cc_flag==cc_read_only_text: return False

		#Todo: Validate the control and make sure there is something that could potentially be cut.
		return True

	def can_copy(self, cc_flag):

		#Todo: Validate the control and make sure there is something that could potentially be copied.
		return True

	def can_paste(self, cc_flag):
		if cc_flag==cc_read_only_text: return False

		#Todo: Validate the clipboard and make sure there is something to paste.
		return True

	#Define an object of type clipboard_monitor that will keep track of the clipboard for us.
	__clipboard=clipboard_monitor.clipboard_monitor()

	#Define the gestures. These are extensions to common Windows shortcuts and so shouldn't be changed.

	__gestures={
		"kb:Control+A": "select_all",
			"kb:Control+Z": "undo",
		"kb:Control+X": "cut",
		"kb:Control+C": "copy",
		"kb:Control+V": "paste",
}
