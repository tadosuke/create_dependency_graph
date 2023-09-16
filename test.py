class MyClassA:

    def __init__(self):
        self._a = 0
        self._b = 0

    def func_a(self):
        self.a = 1

    def func_b(self):
        self.b = 1


class MyClassB:

    def __init__(self):
        self._cls_a = MyClassA()

    def func_a(self):
        self._cls_a.func_a()