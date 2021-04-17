def cdd(a):
    if a==0:
        return

    print("HELLO\n")
    a = a-1
    cdd(a)

def area(a, b):
    print("Area of Rectangle: \n")
    print(a*b)

if 2<3:
    print("aa\n")
    if 3<4:
        print("q\n")
i = 5
while i>0:
    print(i)
    i = i-1
print("Enter the number of times you want to print hello recursively\n")
a = float(input())
cdd(a)
print("\n")
print("Calculate the area of a rectangle\n")
print("Enter length and breadth of a rectangle\n")
b = float(input())
c = float(input())
area(b, c)
