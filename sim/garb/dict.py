
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
