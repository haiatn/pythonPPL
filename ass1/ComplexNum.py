

class ComplexNum:
    #1.1
    def __init__(self,re,im):
        self.number=(re,im)
    #1.3
    def tu_tuple(self):
        return self.number
    #1.5
    def __eq__(self, other):
        if type(other)==type(self):
            if other[0]==self[0] and other[1]==self[1]:
                return True
            else:
                return False
        else:
            return False
    #1.7
    def __neg__(self):
        return (-1*self.number[0],-1*self.number[1])

    def __sub__(self, other):
        #I need to check other's type and follow accordingly (?)
        return other.__add__(self.__neg())
    #1.9
    def conjugate(self):
        return (self.number[0],self.number[1] *-1)