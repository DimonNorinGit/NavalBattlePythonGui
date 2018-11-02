
from kivy.uix.label import Label 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from enums import CellState
from kivy.clock import Clock





from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
#отправлять событие изменение при передвижении коробля всем другим
# т к они зависят от взаимного расположения

#root = Builder.load_file("preparefield.kv")

class Colors():
	occupied = 1
	free = -1
	occupied_clr = [1 , 0 , 0 , 1];
	free_clr = [1 , 1 , 1 , 1];
	ship_color =  [0.1 , 0.9 , 0.4 ,  1]
	ship_collide = [1,0.4,0,1]

class PrepareScreen(Screen):
	events_callback = ObjectProperty(None)
	def __init__(self , **kvargs):
		super(PrepareScreen , self).__init__(**kvargs)
		self.name = "prepare_screen"
		self.prepare = Builder.load_file("preparefield.kv")
		self.prepare.events_callback = self.events_callback
		self.add_widget(self.prepare)

	def clean(self):
		self.prepare.set_default()

class Prepare(Widget):

	def __init__(self , **kvargs):
		super(Prepare , self).__init__(**kvargs)
		self.events_callback = None
		self.set_default()
	


	def set_default(self):
		try:
			self.remove_widget(self.field)
			self.remove_widget(self.ship_set)
		except:
			pass

		self.field = PraparationField()
		self.field.pos = (0,100)
		self.field.size = (500,500)
		self.add_widget(self.field)

		self.is_correct = 0

		n = 10
		m = 10
		a = [0] * n
		for i in range(n):
		    a[i] = [0] * m

		self.field_states = a

		self.ship_set = ShipSet()
		self.ship_set.pos = (500,100)
		self.ship_set.size = (500,100)
		self.ship_set.create_ships(self	.field)
		self.add_widget(self.ship_set)
		Clock.schedule_interval(self.ship_set.recheck_ship_pos , 1/600)



	def check_rules(self):
		check_arrange = 0

		for cell in self.field.children:				
				if cell._state == CellState.ship:
					check_arrange+=1
			
		if check_arrange != 20:
			return False

		self.data = ""
		top_x = 0
		top_y = 0
		bot_x = 0
		bot_y = 0

		for ship in self.ship_set.children:
			if ship.collide:
				return False
			top_x = int(ship.pos[0]//50)
			bot_y = int(9 - (ship.pos[1] - 100)//50)
			bot_x = int(top_x + (ship.size[0]//50) - 1)
			top_y = int((bot_y - (ship.size[1]//50 - 1)))
			self.data+=(chr(top_x) + chr(top_y) + chr(bot_x) + chr(bot_y))

		return True
			



class FieldCell(Button):
	def __init__(self , **kwargs):
		super(FieldCell , self).__init__(**kwargs)
		self._state = CellState.clear
		self.ship = None
		self.ships_collide = 0
		self.uses = 0
	
	def change_color(self , clr_type):
		self.uses+=clr_type
		if self.uses:
			self.background_color = Colors.occupied_clr
		else:
			self.background_color = Colors.free_clr
		


class PraparationField(Widget):
	def __init__(self , **kwargs):
		super(PraparationField , self).__init__(**kwargs)
		for y_pos in range(0,10):
			for x_pos in range(0,10):
				cell  = FieldCell(pos=(50 * y_pos , 100 + 50 * x_pos) ,\
				size=(50 , 50))
				cell.name = str(y_pos) + str(x_pos)
				cell.text = cell.name
				self.add_widget(cell)



class Ship(Button):
	def __init__(self , **kwargs):
		super(Ship , self).__init__(**kwargs)
		self.occupied_cells = []
		self.collide = False
		#self.bind(on_touch_up=PraparationField.find_ship_pos)
		self.counter = 0
	

	def on_touch_down(self, touch):
		if self.collide_point(touch.x , touch.y):
			self.background_color = Colors.ship_color
			self.collide = False
			if len(self.occupied_cells):
				for cell in self.occupied_cells:
					if cell.ship != None and\
					cell.ship is not self:
						cell.change_color(Colors.free)
						continue
					cell.change_color(Colors.free)
					if cell._state == CellState.ship:
						cell.ships_collide-=1

					if cell.ships_collide <= 0:
						cell._state = CellState.clear
						cell.ship = None
						cell._state = 0
				self.occupied_cells.clear()


			if touch.is_double_tap:
				if self.pos[0] + self.size[1] <= 800 and\
					self.pos[1] + self.size[0] <= 600:
					self.size = (self.size[1] , self.size[0])
					self.cell_count[0] , self.cell_count[1]\
					= self.cell_count[1] , self.cell_count[0]
			else:
				touch.grab(self)
				self.touch_dot = touch.pos

			return True

	def on_touch_move(self, touch):
		if touch.grab_current is self:

			new_x = self.pos[0] + touch.pos[0] - self.touch_dot[0]
			new_y = self.pos[1] + touch.pos[1] - self.touch_dot[1]
			self.touch_dot = touch.pos
			if new_x >=0 and new_x + self.size[0] <= 800\
				and new_y + self.size[1] <= 600 and new_y >=100:
				self.pos  = (new_x , new_y)
	

	def recheck(self):
		if len(self.occupied_cells) == 0:
			return
		self.background_color = Colors.ship_color
		self.collide = False
		for cell in self.occupied_cells:
			if cell.background_color == Colors.free_clr:
				cell.change_color(Colors.occupied)
			#if cell.state 
			if cell._state == CellState.ship\
				and cell.ship is not self:
				self.background_color = Colors.ship_collide
				self.collide = True
				return



	def recheck_cells(self):
		cells = cells = [x for x in reversed(self.field.children)]
		cell_diffx = self.pos[0] // 50
		cell_diffy = self.pos[1] // 50

		x_bloks = self.cell_count[0]
		y_bloks = self.cell_count[1]
		
		for x_range in range(-1 , x_bloks + 1):
			for y_range in range(-1 , y_bloks + 1):
				diff_x = (cell_diffx + x_range) * 10
				diff_y = (cell_diffy + y_range - 2)
				diff = int(diff_x + diff_y)
				if diff_x >= 0 and diff_y >=0 and diff_y < 10\
					and diff < 100:
					cell = cells[diff]
					cell.change_color(Colors.occupied)
					self.occupied_cells.append(cell)

					if cell._state == CellState.ship:
						self.background_color = Colors.ship_collide
						self.iscollide = True
					else:	
						if x_range > -1 and x_range < x_bloks\
							and y_range > -1 and y_range < y_bloks:
							cell._state = CellState.ship
							cell.ship = self
							cell.ships_collide+=1


		
	def on_touch_up(self, touch):
		self.counter+=1
		if (touch.is_double_tap or touch.grab_current\
			is self) and self.pos[0] <= 500 - self.size[0]/2:

			touch.ungrab(self)
			self.recheck_cells()
			x = self.pos[0]
			y = self.pos[1]
			cell_diffx = x // 50
			cell_diffy = y // 50
			self.pos[0] = cell_diffx * 50
			self.pos[1] = cell_diffy * 50

					
			

class ShipSet(Widget):
	def __init__(self , **kwargs):
		super(ShipSet ,  self ).__init__(**kwargs)
		self.ship_set = [[4,1],[3,2],[2,3],[1,4]]
		self.pos_diff = 50;

	def recheck_ship_pos(self , instanse):
		for ship in self.children:
			ship.recheck()

	'''def set_defualt_pos(self):
		self.pos_diff = 50
		for ship in reversed(self.children):
				self.def_pos = (500 , 600 - self.pos_diff)
				ship.pos = self.def_pos
				self.pos_diff+=50'''
			
	def create_ships(self , field):
		for ship_decks in self.ship_set:
			for count in range(0, ship_decks[1]):
				ship = Ship()
				ship.field = field
				ship.background_color = Colors.ship_color
				self.def_pos = (500, 600 - self.pos_diff)
				ship.pos = self.def_pos
				ship.cell_count = [ship_decks[0] , 1] 
				ship.size = (50 * ship_decks[0]  , 50)

				self.add_widget(ship)
				self.pos_diff+=50


