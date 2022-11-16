


def my_function():
    global x
    print(x)
    x = 2 * x


x = 5
my_function()
my_function()