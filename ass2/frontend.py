import kivy
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

from ass2 import mybackend as db


class popUpC(FloatLayout):
    recommendations = ObjectProperty(None)


def checkUserInput(userStart, userTime, userAmount):
    if userStart=="" or userStart==None:
        return "you did not insert your starting point"
    if userTime=="" or userTime==None:
        return "you did not insert the time you want to spend"
    if userAmount == "" or userAmount == None:
        return "you did not insert the number of wanted location recommendations"
    try:
        userTime=int(userTime)
    except ValueError:
        return "please enter spending time in minutes by numbers only"
    try:
        userAmount=int(userAmount)
    except ValueError:
        return "please enter the number for location recommendation amount"

    if(userTime<1):
        return "we don't offer locations for this riding time"
    if (userAmount < 1):
        return "the number of locations is invalid"
    return None
class MyGrid(GridLayout):
    start = ObjectProperty(None)
    time = ObjectProperty(None)
    amount = ObjectProperty(None)

    def recommaendMeFunc(self):
        currDB=db.Database()
        userStart=self.start.text
        userTime=self.time.text
        userAmount=self.amount.text
        error=checkUserInput(userStart,userTime,userAmount)
        if error==None:
            resultList=currDB.getRecommendations(userStart,userTime, userAmount)
            if len(resultList):
                popUpContent = popUpC()
                popUpContent.recommendations.text = "we could not find in our database any results for you"
                window = Popup(title="Error - No Results", content=popUpContent, size_hint=(None, None),
                               size=(500, 500))
                window.open()
            popUpContent = popUpC()
            popUpContent.recommendations.text = str(resultList)
            window = Popup(title="results", content=popUpContent, size_hint=(None, None), size=(500, 500))
            window.open()
        else:
            popUpContent = popUpC()
            popUpContent.recommendations.text = error
            window = Popup(title="Error - Wrong Input", content=popUpContent, size_hint=(None, None), size=(500, 500))
            window.open()



    def exampleValueFunc(self):
        self.start.text="Oakland ave"
        self.time.text="5"
        self.amount.text="5"



class MyApp(App):
    def __init__(self,**kwargs):
        super(MyApp,self).__init__(**kwargs)


    def build(self):
        return MyGrid()


if __name__=="__main__":
    MyApp().run()

