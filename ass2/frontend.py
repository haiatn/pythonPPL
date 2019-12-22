import kivy
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import  TextInput
from ass2 import mybackend as db
class MyGrid(GridLayout):
    start = ObjectProperty(None)
    time = ObjectProperty(None)
    amount = ObjectProperty(None)
    def recommaendMeFunc(self):
        resultList=db.getRecommendations(self.start, self.time, self.amount)
        print(resultList)



class MyApp(App):
    def __init__(self,**kwargs):
        super(MyApp,self).__init__(**kwargs)


    def build(self):
        return MyGrid()


if __name__=="__main__":
    MyApp().run()

