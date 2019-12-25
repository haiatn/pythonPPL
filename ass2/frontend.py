import kivy
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

from ass2 import mybackend as db


class popUpC(FloatLayout):
    recommendations = ObjectProperty(None)



class MyGrid(GridLayout):
    start = ObjectProperty(None)
    time = ObjectProperty(None)
    amount = ObjectProperty(None)

    def recommaendMeFunc(self):
        currDB=db.Database()
        userStart=self.start.text
        userTime=self.time.text
        userAmount=self.amount.text
        self.start.text=""
        self.time.text=""
        self.amount.text=""
        error=db.checkUserInput(userStart,userTime,userAmount)
        if error==None:
            resultList=currDB.getRecommendations(userStart,userTime, userAmount)
            if len(resultList)==0:
                popUpContent = popUpC()
                popUpContent.recommendations.text = "we could not find in our database any results for you"
                window = Popup(title="Error - No Results", content=popUpContent, size_hint=(None, None),
                               size=(500, 500))
                window.open()
            else:
                popUpContent = popUpC()
                popUpContent.recommendations.text = self.resultToText(resultList)
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

    def resultToText(self,resultList):
        ans="hey, we have just the location for you, just choose:\n"
        for result in resultList:
            ans=ans+(result[0]+"  (score:"+str(result[1])[:4]+")\n")
        return ans



class MyApp(App):
    def __init__(self,**kwargs):
        super(MyApp,self).__init__(**kwargs)


    def build(self):
        return MyGrid()


if __name__=="__main__":
    MyApp().run()

