from kivy.app import App

from kivy.uix.screenmanager import ScreenManager , Screen, SlideTransition, SwapTransition 


from startmenu import StartMenu
from gametype import GameTypeMenu

from preparefield import PrepareScreen
from programdata import Core

import sys 

import socket



from kivy.config import Config
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')	


class Program(App):


	def __init__(self,  **kvargs):
		super(Program, self).__init__(**kvargs) 
		#self.start_menu = StartMenu
		#self.preparefield = PrepareField





	def build(self):

		self.screen_manager = ScreenManager()

		self.start_menu = StartMenu(events_callback=self.events_program)

		self.type_menu = GameTypeMenu(events_callback=self.events_program)

		self.prepare_screen = PrepareScreen(events_callback=self.events_program)


		self.screen_manager.add_widget(self.start_menu)
		self.screen_manager.add_widget(self.type_menu)
		self.screen_manager.add_widget(self.prepare_screen)


		#game type variables
		self.isTwoPlayers = False
		self.isFirstArranged = False

		return self.screen_manager






	def events_program(self , *args):
		print(*args)

		if len(args) == 2:
			screen , event = args
		else:
			screen , event , data = args


		


		if screen == Core.StartMenu:
			if event == Core.start_menu.play:
				self.screen_manager.current = "type_menu"
			elif event == Core.start_menu.tools:
				pass
			else:
				sys.exit(0)

		elif screen == Core.TypeMenu:

			if event == Core.type_menu.PvsP  :
				self.screen_manager.current = "prepare_screen"
				self.isTwoPlayers = True
			elif event == Core.type_menu.PvsObot:
				pass
			elif event == Core.type_menu.PvsRbot:
				pass
			elif event == Core.type_menu.ObotvsRbot:
				pass

			elif event == Core.type_menu.Back:
				self.isTwoPlayers = False
				self.screen_manager.current = "start_menu"
				
		elif screen == Core.PScreen:
			if event == Core.p_field.arrange:

				if not self.isFirstArranged:
					self.isFirstArranged = True
					self.prepare_screen.clean()
				else:
					#some work with server
					#change_screen to game_screen
					pass

			elif event == Core.p_field.back:
				if self.isTwoPlayers:
					if self.isFirstArranged:
						pass
					else:
						self.screen_manager.current = "gametype"
						self.prepare_screen.cleen()

				else:
					self.screen_manager.current = "gametype"
					self.prepare_screen.cleen()














if __name__ == "__main__":
	Program().run()