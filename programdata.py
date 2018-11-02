
class Core():
	StartMenu = 1
	TypeMenu = 2
	PScreen = 3
	GameField = 4

	class game():
		end = 1
		change_field = 2

	class game_states():
		continue_game = 1
		end_game = 2
		#left_win = 1
		#right_win = 2


	class type_menu():
		PvsP = 1
		PvsObot = 2
		PvsRbot = 3
		ObotvsRbot = 4
		Back = 5
	class start_menu():
		play = 1
		tools = 2
		exit = 3
	class p_field():
		arrange = 1
		botarrange = 2
		back = 3

	class game_type():
		PvsP = "hh"
		PvsObot = "ho"
		PvsRbot = "hr"
		ObotvsRbot = "or"
	class game_field():
		end_battle = 1
		
	class client():
		port = 9090


