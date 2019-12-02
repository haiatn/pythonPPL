import math


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

    # 1.5
    def __eq__(self, other):
        if type(other) == type(self):
            if other[0] == self.re and other[1] == self.im:
                return True
            else:
                return False
        else:
            return False

    # 1.6 - calculate and return the result of adding to the complex number the other given value
    def __add__(self, other):
        if type(other) == type(self):
            return ComplexNum(self.re + other.re, self.im + other.im)

    # 1.7 - return the negative of the complex number
    def __neg__(self):
        return ComplexNum(-1 * self.re, -1 * self.im)

    # 1.7 -
    def __sub__(self, other):
        # I need to check other's type and follow accordingly (?)
        return other.__add__(self.__neg())

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


# tests
z = ComplexNum(1, 2)
print(z.re)
print(z.im)
print(z)
print(z + ComplexNum(1, -3))
print(z.conjugate())
print(-z)
print(z.abs())
print(z+2)
