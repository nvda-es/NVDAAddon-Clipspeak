# Clipspeak
# An addon to monitor and speak messages relating to clipboard operations
# By: Damien Lindley
# Created: 19th April 2017

# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import globalPluginHandler
import ui
import api
import inputCore
import scriptHandler

from logHandler import log
from controlTypes import *

import clipboard_monitor

# Constants:

# Clipboard content: What are we working with?
cc_none=0
cc_text=1
cc_read_only_text=2
cc_file=3
cc_list=4
cc_other=5

# Clipboard mode: What are we doing?
cm_none=0
cm_cut=1
cm_copy=2
cm_paste=3

# Not strictly clipboard, but...
cm_undo=4
cm_redo=5
cm_select_all=6

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	# Script functions:

	def script_cut(self, gesture):
		if self.process_input(gesture): return
		self.speak_appropriate_message(cm_cut)

	# Translators: Documentation for cut script.
	script_cut.__doc__=_("Cut selected item to clipboard, if appropriate.")

	def script_copy(self, gesture):
		if self.process_input(gesture): return
		self.speak_appropriate_message(cm_copy)

	# Translators: Documentation for copy script.
	script_copy.__doc__=_("Copy selected item to clipboard, if appropriate.")

	def script_paste(self, gesture):
		if self.process_input(gesture): return
		if not self.__clipboard.valid_data(): return
		self.speak_appropriate_message(cm_paste)

	# Translators: Documentation for paste script.
	script_paste.__doc__=_("Paste item from clipboard, if appropriate.")

	def script_undo(self, gesture):
		if self.process_input(gesture): return
		self.speak_appropriate_message(cm_undo)

	# Translators: Documentation for undo script.
	script_undo.__doc__=_("Undo operation.""")

	def script_redo(self, gesture):
		if self.process_input(gesture): return
		self.speak_appropriate_message(cm_redo)

	# Translators: Documentation for redo script.
	script_redo.__doc__=_("Redo operation.")

	def script_select_all(self, gesture):
		if self.process_input(gesture): return
		self.speak_appropriate_message(cm_select_all)

	# Translators: Documentation for select_all script.
	script_select_all.__doc__=_("Select all.")

	# Internal functions: Examines our environment so we can speak the appropriate message.

	def process_input(self, gesture):
		gesture.send()
		scripts=[]
		maps=[inputCore.manager.userGestureMap, inputCore.manager.localeGestureMap]
		for map in maps:
			for identifier in gesture.identifiers:
				scripts.extend(map.getScriptsForGesture(identifier))
		focus=api.getFocusObject()
		tree=focus.treeInterceptor
		if tree and tree.isReady:
			func=scriptHandler._getObjScript(tree, gesture, scripts)
			if func and (not tree.passThrough or getattr(func,"ignoreTreeInterceptorPassThrough",False)):
				func(tree)
				return True
		return False

	def speak_appropriate_message(self, cm_flag):
		cc_flag=self.examine_focus()

		# Todo: If we can validate whether or not a control can work with the clipboard, we can return an invalid message here.
		log.debug("Finding appropriate message for clipboard content type: %r"%cc_flag)
		if cc_flag==cc_none: return

		# Pick a word suitable to the content.

		# Translators: A single word representing text.
		word=_("text")

		if cc_flag==cc_file:

			# Translators: A single word representing a file.
			word=_("file")

		if cc_flag==cc_list:

			# Translators: A single word representing an item in a list.
			word=_("item")

		# Validate and speak.
		log.debug("Validating clipboard mode: %r"%cm_flag)

		if cm_flag==cm_undo and self.can_undo(cc_flag):

			# Translators: Message to speak when undoing.
			ui.message(_("Undo"))

		if cm_flag==cm_redo and self.can_redo(cc_flag):

			# Translators: A message spoken when redoing a previously undone operation.
			ui.message(_("Redo"))

		if cm_flag==cm_select_all and self.can_select(cc_flag):

			# Translators: A message to speak when selecting or highlighting all content.
			ui.message(_("Select All"))

		if cm_flag==cm_cut and self.can_cut(cc_flag):

			# Translators: A message to speak when cutting an item to the clipboard.
			ui.message(_("Cut %s")%word)

		if cm_flag==cm_copy and self.can_copy(cc_flag):
			if not self.__clipboard.changed():

				# Translators: A message spoken when no change has been detected on the clipboard.
				ui.message(_("No change."))
				return

			# Translators: A message spoken when copying to the clipboard.
			ui.message(_("Copy %s")%word)

		if cm_flag==cm_paste and self.can_paste(cc_flag):

			# Translators: A message spoken when pasting to the clipboard.
			ui.message(_("Pasted %s")%word)

	def examine_focus(self):
		focus=api.getFocusObject()
		if not focus: return cc_none
		log.debug("Examining focus object: %r"%focus)

		# Retrieve the control's states.
		states=focus.states

		# Check for an explorer/file browser window.
		# Todo: Is this an accurate method?
		if focus.windowClassName=="DirectUIHWND": return cc_file

		# Check for a list item.
		if focus.role==ROLE_LISTITEM: return cc_list

		# Check if we're looking at text.
		if STATE_EDITABLE in states:
			if STATE_READONLY in states: return cc_read_only_text

			# Otherwise, we're just an ordinary text field.
			log.debug("Field seems to be editable.")
			return cc_text

		# Todo: Other control types we need to check?
		log.debug("Control type would not suggest clipboard operations.")
		return cc_none

	# Validation functions: In case we need to extend the script to allow more control/window types etc.
	# Todo: Can we check a control to see if it enables these operations? For instance whether a list enables copy or a text field allows select all?

	def can_undo(self, cc_flag):
		if cc_flag==cc_read_only_text: return False
		return True

	def can_redo(self, cc_flag):
		if cc_flag==cc_read_only_text: return False
		return True

	def can_select(self, cc_flag):
		return True

	def can_cut(self, cc_flag):
		if cc_flag==cc_read_only_text: return False

		# Todo: Validate the control and make sure there is something that could potentially be cut.
		return True

	def can_copy(self, cc_flag):

		# Todo: Validate the control and make sure there is something that could potentially be copied.
		return True

	def can_paste(self, cc_flag):
		if cc_flag==cc_read_only_text: return False

		# Todo: Validate the clipboard and make sure there is something to paste.
		return True

	# Define an object of type clipboard_monitor that will keep track of the clipboard for us.
	__clipboard=clipboard_monitor.clipboard_monitor()

	# Translators: Category displayed in Input Gestures configuration.
	scriptCategory=_("Clipboard")

	# Define the default gestures.

	__gestures={
		"kb:Control+A": "select_all",
			"kb:Control+Z": "undo",
			"kb:Control+Y": "redo",
		"kb:Control+X": "cut",
		"kb:Control+C": "copy",
		"kb:Control+V": "paste",
	}


