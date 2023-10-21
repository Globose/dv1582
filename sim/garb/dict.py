
class Obj:
    def __init__(self):
        "init"

lst = []
o = Obj()
lst.append(o)
d = {}
d["0x22A"] = lst.pop()

print("hallo", d.pop("0x22A"))
print("hallo", d.get("s"))
print("hallo", d.get("022A"))
print(d)

li = [1,2,3,4,5,6]
for i, x in enumerate(li):
    print((i,x))