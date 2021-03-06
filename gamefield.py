from kivy.uix.label import Label 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from enums import CellState
from kivy.clock import Clock

from programdata import Core

import socket

from kivy.graphics import Color, Rectangle

from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder



field_delay = 1

class Colors():
	broken_cell = [0.2 ,0.1 , 0.2 , 0.7]
	broken_ship = [1 , 0 , 0 , 1] 
	default_cell = [0 , 0.2 , 1 , 1]
	ship_color = [0.5 , 0.5 , 0.5 , 1]

class GameFieldScreen(Screen):
	events_callback = ObjectProperty(None)
	def __init__(self , **kvargs):
		super(GameFieldScreen , self).__init__(**kvargs)
		self.name = "game_screen"
		self.left_player = None
		self.right_player = None

		self.data_socket = None
		self.isGameEnd = False

		#self.data_socket = socket.socket()
		#self.data_socket.connect(('localhost' , Core.client.port))
		#self.data_socket.send(bytes( msg, encoding = 'utf-8'))
		#sdata_sender.connect()


		#self.game_field = Builder.load_file("gamefield.kv")
		#self.game_field.events_callback = self.events_callback
		#self.add_widget(self.game_field)


	def create_field(self , player_type ,  field_states , diff):
		isActiveField = True
		if player_type != "h":
			isActiveField = False
		

		field = GameField(self, isActiveField)

		field.events_callback = self.events_callback

		#field.bind(field_events=self.field_events)

		for two_bytes in range(diff , diff + 20):
			x = field_states[2 * two_bytes]
			y = field_states[2 * two_bytes + 1]
			cell = field.game_cells.children[99 -((9-y) * 10) - x]
			#cell.background_color = Colors.ship_color
			cell._state = CellState.ship
		return field






	def define_fields(self , field_states):

		#В зависимости от режима создавать поле из лэйблов
		#отдельный класс-DisabledGameField
		self.left_field = self.create_field(self.right_player , field_states , 0)
		
		self.right_field = self.create_field(self.left_player , field_states , 20)

		self.current_player = self.right_player
		self.previos_player = self.left_player

		self.current_field = self.left_field
		self.previos_field = self.right_field

		

		self.add_widget(self.left_field)


	def send_data_to_server(self , data):
			try:
				self.data_socket = socket.socket()
				self.data_socket.connect(('localhost' , Core.client.port))
				self.data_socket.send(bytes( data , encoding = 'utf-8'))
			except ConnectionRefusedError:
				print("Connectio Error")


	def recive_data_from_server(self):
		data = self.data_socket.recv(34)#game_state + ship_typ + cell_count + cells*2(x,y)
		self.data_socket.close()
		return data

	def do_event(self , data):
		game_state = chr(data[0])
		ship_state = chr(data[1])

		cells_count = data[5]
		shot_x = data[3]
		shot_y = data[4]
		

		self.current_field.set_cell((shot_x , shot_y) , ship_state)
		
		if game_state == "e":
			self.isGameEnd = True

		if cells_count != 0:
			self.current_field.fill_cells(data[6:6 + cells_count * 2])
		print(ship_state)

		if ship_state != "m":#miss
			return True

		return False

	def change_field(self , instanse=0):
		self.remove_widget(self.current_field)
		self.add_widget(self.previos_field)

		self.previos_player , self.current_player =\
		self.current_player , self.previos_player

		self.previos_field , self.current_field =\
		self.current_field , self.previos_field

		if self.previos_player != "b":
			self.previos_field.isActive = True



	def field_events(self , event="bot"):
		if event == "end":
			pass

		isExtraShot = False
		
		if event == "start" and self.current_player != "b":
			return
		event = str(event)
		self.send_data_to_server(event)#continue game

		print("recive start")
		data = self.recive_data_from_server()
		print("recive")
		isExtraShot = self.do_event(data)


		if self.isGameEnd:
			self.events_callback(Core.GameField , Core.game_field.end_battle)
		else:
			if self.current_player == "h" and not isExtraShot:
				if self.previos_player == "b":
					Clock.schedule_once(self.field_events , field_delay*2)
				Clock.schedule_once(self.change_field , field_delay)

			elif self.current_player == "b":
				if isExtraShot:
					Clock.schedule_once(self.field_events , field_delay)
				else:
					if self.previos_player == "b":
						Clock.schedule_once(self.field_events , field_delay*2)
					Clock.schedule_once(self.change_field , field_delay)



'''class DisableCell(Label):
	def __init__(self , **kwargs):
		super(DisableCell , self).__init__(**kwargs)
		self._state = CellState.clear
		self.background_color = ObjectProperty()
		#self.on_background_color(Colors.default_cell)


	def on_background_color(self , value):
		with self.canvas:
			x_color = self.size[0] - 1
			y_color = self.size[1] - 1
			Color(*value)
			Rectangle(pos=self.pos, size=(x_color, y_color))'''



class GameField(Widget):
	def __init__(self , root_screen ,  isActive , **kvargs):
		self.events_callback = ObjectProperty(None)
		
		self.size = 800,600

		'''endButton = Button(text="End Battle" , size=(400,100),pos=(0,0))
		endButton.bind(on_release=self.events_callback(Core.GameField , Core.game_field.end_battle))
		self.add_widget(endButton)'''

		super(GameField , self).__init__(**kvargs)
		self.game_cells = GameCells(root_screen , self)
		self.isActive = isActive

		self.game_cells.pos = (0,100)
		self.game_cells.size = (500,500)
		self.add_widget(self.game_cells)

	def set_cell(self , shot , ship_state):
		x = shot[0]
		y = shot[1]
		cell = self.game_cells.children[99 -((9-y) * 10) - x]
		if ship_state == "m":# промах
			cell._state = CellState.used
			cell.background_color = Colors.broken_cell
			#change color
		else:
			cell_state = CellState.hit
			cell.background_color = Colors.broken_ship
			#change color

	def fill_cells(self , cells_pos):
		for s in cells_pos:
			print(s,end=" ")

		for two_bytes in range(0 , len(cells_pos)//2):
			x = cells_pos[2 * two_bytes]
			y = cells_pos[2 * two_bytes + 1]
			cell = self.game_cells.children[99 -((9-y) * 10) - x]
			cell.background_color = Colors.broken_cell
			cell._state = CellState.used


	


	'''def server_events(self , event_data):
		#game_state + ship_type + cell_count + cells

		if event_data == 0:
			pass
			#change_field

		game_state = event_data[0]

		if game_state == Core.game_states.continue_game:
			cell_count = event_data[2]

			if cell_count == 0:
				pass
			else:
				self.fill_cells(event_data[3:cell_count + 4])
				self.field_events(Core.game.change_field)

			#ship_type = event_data[1]
			#some work with ship_type->decrease counter
		else:
			print("End")
			self.field_events(Core.game.end)
			#end

		#change_field'''




class FieldCell(Button):
	def __init__(self , **kwargs):
		super(FieldCell , self).__init__(**kwargs)
		self._state = CellState.clear
		self.root_screen = None
		self.isActive = True

	def on_touch_down(self, touch):
		if self.collide_point(touch.x , touch.y)\
			and self.root.isActive:

			pos_x = int(self.pos[0]//50)
			pos_y = int(9 - (self.pos[1] - 100)//50)
			cell_pos = ""
			if self._state == CellState.clear:
				cell_pos = chr(pos_x) + chr(pos_y)
				self.root.isActive = False
			elif self._state == CellState.ship:
				cell_pos = chr(pos_x) + chr(pos_y)
			else:
				pass

			self._state = CellState.used

			if cell_pos != '':
				self.root_screen.field_events(cell_pos)

			return True

	

class GameCells(Widget):
	def __init__(self , root_screen , root , **kwargs):
		super(GameCells , self).__init__(**kwargs)
		for y_pos in range(0,10):
			for x_pos in range(0,10):
				cell  = FieldCell(pos=(50 * x_pos , 100 + 50 * y_pos) ,\
				size=(50 , 50))

				cell.root = root

				cell.background_color = Colors.default_cell

				cell.name = str(x_pos) + str(y_pos)
				cell.text = cell.name
				cell.root_screen = root_screen

				#cell.bind(server_events1=self.server_events2)
				self.add_widget(cell)
	