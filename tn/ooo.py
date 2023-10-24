import json

class Person:
    def __init__(self, name, year, address):
        self.name = name
        self.birthyear = year
        self.address = address

    def __str__(self):
        return "{},{}\n{}".format(
            self.name,
            self.birthyear,
            self.address)

    def to_dict(self):
        return dict(
            name=self.name,
            birthyear=self.birthyear,
            address=self.address)

    @staticmethod
    def refactor(data):
        return Person(
            data["name"],
            data["birthyear"],
            data["address"])

class Register:
    def __init__(self):
        self.record = []

    def __str__(self):
        outstr = ""
        for rec in self.record:
            outstr += str(rec)
            outstr += "\n\n"

        return outstr

    def addPerson(self, file):
        self.record.append(file)

    def to_dict(self):
        reclst = []
        for rec in self.record:
            reclst.append(rec.to_dict())

        return dict(record=reclst)

    @staticmethod
    def refactor(data):
        addr = Register()
        for rec in data["record"]:
            addr.addPerson(Person.refactor(rec))
        return addr

if __name__ == "__main__":
    rec = Register()
    rec.addPerson(Person("Torfrej Persdotter", 1980, "Almgatan 10"))
    rec.addPerson(Person("Bohenrika Svensson", 1948, "Baker Street 221B"))
    rec.addPerson(Person("Halvdan Lenbakt", 1999, "Paradisäppelvägen 111"))

    print (rec)

    # Create JSON data
    data = rec.to_dict()
    jsondata = json.dumps(data)
    print(jsondata,"\n")

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

    read_file = None
    with open('data.json', 'r') as f:
        read_file = json.load(f)

    print(read_file)

    # Read from JSON data
    data_read = json.loads(jsondata)
    rec_read = Register.refactor(data_read)
    print(rec_read)

    # read from file
    red_file = Register.refactor(read_file)
    print("file:")
    print(red_file)