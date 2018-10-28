from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder 

root = Builder.load_file("startmenu.kv")

class StartMenu(AnchorLayout , Screen):
	events_callback = ObjectProperty(None)
