"""Only for test the getTiles.py """
file = open("output.txt", "r")

for x in file:
    x = x[:-1]
    print(x)
