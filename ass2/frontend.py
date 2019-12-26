import kivy
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from ass2 import mybackend as db

'''
this class holds the gui for the application for biking route we built. 
We provide here the structure needed for kivy app and the graphic design
lays in the my.kv file. The logical database manipulations are in the backend file.
'''



'''
this class is for the pop-up for the results.
'''
class popUpC(FloatLayout):
    recommendations = ObjectProperty(None)

'''
this class is for the graphic architecture of the results
'''
class MyGrid(GridLayout):
    start = ObjectProperty(None)
    time = ObjectProperty(None)
    amount = ObjectProperty(None)
    '''
    :return void. but opens pop-up for user in graphic interface with results or error details
    '''
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


    '''
    :return void. but changes the text-field values for the values stated here 
    '''
    def exampleValueFunc(self):
        self.start.text="Oakland ave"
        self.time.text="5"
        self.amount.text="5"


    '''
    :param resultList- is a list of tupples. each tupple is (location,locationScore)
    :return string that changed the tupple into text that can be shown in the pop-op
    will of the information needed
    '''
    def resultToText(self,resultList):
        ans="hey, we have just the location for you, just choose:\n"
        for result in resultList:
            ans=ans+(result[0]+"  (score:"+str(result[1])[:4]+")\n")
        return ans


'''
 a class that must be present to run the kivy app
'''
class MyApp(App):
    def __init__(self,**kwargs):
        super(MyApp,self).__init__(**kwargs)

    '''
    function that builds the app on the grid class we created
    '''
    def build(self):
        return MyGrid()


if __name__=="__main__":
    MyApp().run()

