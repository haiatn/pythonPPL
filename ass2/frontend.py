import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import  TextInput

class MyGrid(GridLayout):
    pass

class MyApp(App):
    def __init__(self,**kwargs):
        super(MyApp,self).__init__(**kwargs)

    def build(self):
        return MyGrid()
if __name__=="__main__":
    MyApp().run()

