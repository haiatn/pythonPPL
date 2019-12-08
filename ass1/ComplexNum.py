import math

from functools import reduce

'''
 this class represent a complex number which is a real number which can have an imaginary part
'''
class ComplexNum:
    # 1.1 - constructor for the complex number
    # re - real part of the complex number
    # im - imaginary part of the complex number
    def __init__(self, re, im):
        self.number = (re, im)

    # 1.2 - returns the real part of the complex number
    @property
    def re(self):
        return self.number[0]

    # 1.2 - returns the imaginary part of the complex number
    @property
    def im(self):
        return self.number[1]

    # 1.3 - return tuple representation for the complex number
    def tu_tuple(self):
        return self.number

    # 1.4 - return string representation for the complex number
    def __repr__(self):
        if self.im < 0:
            sign = "-"
            im = str(self.im)[1:]
        else:
            sign = "+"
            im = str(self.im)
        return str(self.re) + " " + sign + " " + im + "i"

    # 1.5 - return whether two objects are logically same
    def __eq__(self, other):
        if type(other) == type(self):
            if other.re == self.re and other.im == self.im:
                return True
            else:
                return False
        else:
            return False

    # 1.6 - calculate and return the result of adding to the complex number the other given value
    def __add__(self, other):
        if type(other) != ComplexNum:
            raise TypeError("Complex addition only defined for Complex Numbers")
        if type(other) == type(self):
            return ComplexNum(self.re + other.re, self.im + other.im)

    # 1.7 - return the negative of the complex number
    def __neg__(self):
        return ComplexNum(-1 * self.re, -1 * self.im)

    # 1.7 - calculate and return the result of subtracting the complex number from the other given value
    def __sub__(self, other):
        if type(other) != ComplexNum:
            raise TypeError("Complex subtracting only defined for Complex Numbers")
        return self.__add__(other.__neg__())

    # 1.8 - calculate and return the multiplication of two complex numbers
    def __mul__(self, other):
        if type(other) != ComplexNum:
            raise TypeError("Complex multiplication only defined for Complex Numbers")
        return ComplexNum(self.re * other.re - self.im * other.im,
                          self.re * other.im + self.im * other.re)

    # 1.9 - return the conjugate for the complex number
    def conjugate(self):
        return ComplexNum(self.re, self.im * -1)

    # 1.10 - return the abs of the complex number
    def abs(self):
        mul = self * self.conjugate()
        return math.sqrt(mul.re + mul.im)


# 2.1 - return true if object1 is an instance of classInfo
def isInstancePPL(object1,classInfo):
    return (type(classInfo) is type) and (type(object1) is not type) and (object1.__class__ is classInfo or classInfo in object1.__class__.__bases__)

# 2.2 - return the number of hirarchy level between object1 class and classInfo
def numInstancePPL(object1, classInfo):
    parentClassList = list(object1.__class__.__bases__)
    if parentClassList.__len__() == 0 or parentClassList[0] is object:
        return 0
    elif type(object1) is classInfo:
        return 1
    else:
        # for base in parentClassList:
            return 1 + numSubclassPPL(parentClassList[0], classInfo)

# 2.3 - return true if class1 inherits classInfo
def isSubclassPPL(class1,classInfo):
    return (type(classInfo) is type) and (type(class1) is type) and (classInfo in class1.__bases__ or class1 == classInfo)

# 2.4 - return the number of hirarchy level between class1 and classInfo
def numSubclassPPL(class1,classInfo):
    parentClassList = list(class1.__bases__)
    if class1 is classInfo:
        return 1
    elif parentClassList.__len__() == 0 or parentClassList[0] is object:
        return 0
    else:
        # for base in parentClassList:
            return 1 + numSubclassPPL(parentClassList[0], classInfo)

# 3.1 - return number of object in list which statisfy func1 condition
def count_if(lst, func):
    return list(map(func, lst)).count(True)

# 3.2 - return if the condition func2 is true for calculating func1 on each list item
def for_all(lst, func1, func2):
    lstAfterFunc1 = list(map(func1, lst))
    return count_if(lstAfterFunc1, func2) == lstAfterFunc1.__len__()

# 3.3 - return if the condition func2 is true for calculating func1 on all list items
def for_all_red(lst, func1, func2):
    return func2(reduce(func1,lst))

# 3.4 - return if exists n items in the list who statisfy func1
def there_exists(lst, n, func1):
    return count_if(lst, func1) >= n



def testQ1():
    # tests
    z = ComplexNum(1, 2)
    print(z.re) #1
    print(z.im) #2
    print(z) #1 + 2i
    print(z + ComplexNum(1, -3)) #2 - 1i
    print(z.conjugate()) # 1 - 2i
    print(-z) #-1 - 2i
    print(z.abs()) #sqrt(5)
    try:
        print(z+2) # some kind of fail
    except TypeError:
        print("ERROR!!!")

    z2 = ComplexNum(3, 1)
    print(z2.re) #3
    print(z2.im) #1
    print(z2) #3 + 1i
    print(z+z2) #4 + 3i
    print(z-z2) #-2 +1i
    #print(2-z2) #some kind of fail (we did not neede to actually implement)
    try:
        print(z2-3) #some kind of fail
    except TypeError:
        print("ERROR!!!")
    try:
        print(z2-3.0) #some kind of fail
    except TypeError:
        print("ERROR!!!")
    print(z.conjugate()+z2) #4 - 1i
    print(z2*z) #1 + 7i
    print((z2*z).abs()) # sqrt(50)
    print(z2.tu_tuple()) # (3,1)
    print(z.__eq__(z2)) #false
    print(z==z2) #false
    print(z2==z) #false
    print((z-z)==(z2-z2)) #true
    print(z2.__eq__(2)) #false
    print(z2.__eq__(2.0)) #false
    print(ComplexNum(0,0)) # 0 + 0i
    print(type(z)==type(z2)) #true (we did not neede to actually implement, I just made sure
    try:
        print(z2*3) #raise error
    except TypeError:
        print("ERROR!!!")
    #print(2*z2) #some kind of error (we did not neede to actually implement)

def testQ2():
    class X:
        pass
    class Y(X):
        pass
    x=X()
    y=Y()

    print(isInstancePPL(x,X)) #True
    print(isInstancePPL(x, Y)) #False
    print(isInstancePPL(y, X)) #True
    print(isInstancePPL(y, Y)) #True

    # print(numSubclassPPL(y, type(x)))  # 2
    # print(numSubclassPPL(y, Y))  # 1
    # print(numSubclassPPL(x, type(y)))  # 0 if im correct

    print(numInstancePPL(y,Y))
    print(numInstancePPL(y,X))
    print(isSubclassPPL(x.__class__, X)) #True
    print(isSubclassPPL(X, X)) # True
    print(isSubclassPPL(X, Y)) #False
    print(isSubclassPPL(Y, X)) #True
    print(numSubclassPPL(Y, X))  # 2
    # print(isSubclassPPL(Y, type(y))) #True
    print(isSubclassPPL(Y, Y)) # True
    print(numSubclassPPL(Y, Y))  # 1

    print(isSubclassPPL(type(x), X)) # True
    print(isSubclassPPL(type(x), Y)) # False
    print(isSubclassPPL(type(y), X)) # True
    print(isSubclassPPL(type(y), Y)) # True

    print(isSubclassPPL(x.__class__, X)) # True
    print(isSubclassPPL(x.__class__, Y)) # False
    print(isSubclassPPL(y.__class__, X)) # True
    print(isSubclassPPL(y.__class__, Y)) # True

    print(numSubclassPPL(Y,type(x))) #2
    print(numSubclassPPL(y.__class__, Y)) #1

    class Z(Y):
        pass
    z = Z()
    print(isInstancePPL(x, Z)) #False
    print(isInstancePPL(y, Z)) #False
    print(isInstancePPL(z, X)) #True TODO
    print(isInstancePPL(z, Y)) #True

    print(numInstancePPL(z,X)) # 3
    print(numInstancePPL(x,Z)) # 0

    print(isSubclassPPL(X, Z)) #False
    print(isSubclassPPL(Y, Z)) #False
    print(isSubclassPPL(Z, X)) #True TODO

    print(numSubclassPPL(X,Z)) # 0
    print(numSubclassPPL(Z, X)) # 3

def testQ3():
    print(count_if([1, 0, 8], lambda x: x > 2)) #1
    print(count_if([1, 1, 8], lambda x: x == 1))  # 2

    print(for_all([1, 0, 8], lambda x: x * 2, lambda x: x > 0))  # False
    print(for_all([1, 1, 8], lambda x: x, lambda x: x > 0))  # True

    print(for_all_red([1, 0, 8], lambda x,y: x * y, lambda x: x > 0))  # False
    print(for_all_red([1, 1, 8], lambda x,y: x * y, lambda x: x > 7))  # True

    print(there_exists([1, 0, 8], 2, lambda x:x>-1)) #True
    print(there_exists([1, 0, 8], 2, lambda x:x>5)) #False
    print(there_exists([1, 0, 8], 2, lambda x:x>=1)) #True


testQ2()

