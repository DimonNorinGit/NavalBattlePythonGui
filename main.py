from kivy.app import App

from kivy.uix.screenmanager import ScreenManager , Screen, SlideTransition, SwapTransition 


from startmenu import StartMenu
from gametype import GameTypeMenu

from preparefield import PrepareScreen
from programdata import Core

from gamefield import GameFieldScreen

import sys 

import socket



#ord() and chr()

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

		self.screen_manager.add_widget(self.start_menu)
		self.screen_manager.add_widget(self.type_menu)
		self.init_game()

		#game type variables
		self.isTwoPlayers = False
		self.isFirstArranged = False
		self.message_data = None

		return self.screen_manager


	def end_game(self):
		self.screen_manager.remove_widget(self.prepare_screen)
		self.screen_manager.remove_widget(self.game_screen)


	def init_game(self):
		self.prepare_screen = PrepareScreen(events_callback=self.events_program)
		self.game_screen = GameFieldScreen(events_callback=self.events_program)

		self.screen_manager.add_widget(self.prepare_screen)
		self.screen_manager.add_widget(self.game_screen)

	def send_data_to_server(self):
		try:
			msg = self.message_data
			self.data_socket = socket.socket()
			self.data_socket.connect(('localhost' , Core.client.port))
			self.data_socket.send(bytes( msg, encoding = 'utf-8'))
			
			self.message_data = None

		except ConnectionRefusedError:
			print("Connectio Error")


	def recive_data_from_server(self):
		data = self.data_socket.recv(80)# 2 * cell_count - all = ship cells
		self.data_socket.close()
		return data

	def events_program(self , *args):

		if len(args) == 2:
			screen , event = args
		else:
			screen , event , data = args
			for s in data:
				print(str(ord(s)),end=" ")
			
				
		#data - string of ships coordinates
		


		if screen == Core.StartMenu:
			if event == Core.start_menu.play:
				self.screen_manager.current = "type_menu"
				self.message_data = "s"
				self.send_data_to_server()#start prepare_stage
			elif event == Core.start_menu.tools:
				pass
			else:
				self.message_data = "e"
				self.send_data_to_server()
				sys.exit(0)


		elif screen == Core.TypeMenu:

			if event == Core.type_menu.PvsP:
				self.message_data = Core.game_type.PvsP
				self.isTwoPlayers = True
				self.screen_manager.current = "prepare_screen"
				self.game_screen.left_player = "h"
				self.game_screen.right_player = "h"

			elif event == Core.type_menu.PvsObot:
				self.message_data = Core.game_type.PvsObot
				self.screen_manager.current = "prepare_screen"
				self.game_screen.left_player = "h"
				self.game_screen.right_player = "b"


			elif event == Core.type_menu.PvsRbot:
				self.screen_manager.current = "prepare_screen"
				self.message_data = Core.game_type.PvsRbot
				self.game_screen.left_player = "h"
				self.game_screen.right_player = "b"

			elif event == Core.type_menu.ObotvsRbot:
				self.message_data = Core.game_type.ObotvsRbot
				self.events_program(Core.PScreen , Core.p_field.botarrange)
				self.game_screen.left_player = "b"
				self.game_screen.right_player = "b"
				
			elif event == Core.type_menu.Back:
				self.isTwoPlayers = False
				self.screen_manager.current = "start_menu"
				

		elif screen == Core.PScreen:
			if event == Core.p_field.arrange:
				if self.isTwoPlayers:
					if not self.isFirstArranged:
						self.isFirstArranged = True
						self.message_data+=data
						self.prepare_screen.clean()
					else:
						self.message_data+=data
						self.send_data_to_server()
						#recive data
						#game_screen.define
						field_states = self.recive_data_from_server()
						self.game_screen.define_fields(field_states)
						self.screen_manager.current = "game_screen"
						self.game_screen.field_events("start")

				else:
					self.message_data+=data
					self.send_data_to_server()
					field_states = self.recive_data_from_server()
					for s in field_states:
						print(s)
					self.game_screen.define_fields(field_states)

					#recive data
					#game_screen.define
					self.screen_manager.current = "game_screen"
					self.game_screen.field_events("start")


			elif event == Core.p_field.botarrange:
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


		elif screen == Core.GameField:
			if event == Core.game_field.end_battle:
				#show winner(screen)
				self.screen_manager.current = "start_menu"
				self.end_game()
				self.init_game()
				












'''	if not self.isFirstArranged:
					self.isFirstArranged = True
					#work with server
					if self.isTwoPlayers:
						self.prepare_screen.clean()
						#data+
					else:
						#data+
						#send
						#go to gamefield
				else:
					#it is mean there is two players
					#some work with server
					#change_screen to game_screen
					pass'''



if __name__ == "__main__":
	Program().run()