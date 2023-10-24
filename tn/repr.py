import json

class Varelse:
    new_id = 1

    def __init__(self,id = None, parent_id:int=0):
        if id is None:
            self.id = Varelse.new_id
            Varelse.new_id += 1
        else:
            self.id = id
        self.parent_id = parent_id

    def equals(self, other: 'Varelse') -> bool:
        return False
    
    def get_tuple(self) -> tuple[int, int, int, int, int]:
        return (self.id, self.parent_id)
    
    @staticmethod
    def refactor(data):
        return Varelse(data["id"],data["parentId"])

    def to_dict(self):
        return dict(id=self.id, parentId=self.parent_id)

class Population:
    def __init__(self, varelser=None, removed=None) -> None:
        if varelser is None:
            self._varelser = []
        else:
            self._varelser = varelser
        if removed is None:
            self._removed =  []
        else:
            self._removed=removed

    def add_removed(self, varelse:Varelse):
        """Adds varelse to removed list"""
        self._removed.append(varelse)

    def add_varelse(self, varelse: Varelse):
        """Adds a Varelse at the end of the population, 
        given its genotyp is unique"""
        assert type(varelse) == Varelse
        v:Varelse
        for v in self._varelser:
            if v.equals(varelse):
                return
        if varelse in self._removed:
            self._removed.remove(varelse)
        self._varelser.append(varelse)

    def get_varelse(self) -> Varelse:
        """Returns the first Varelse in the Population"""
        assert len(self) > 0
        var = self._varelser.pop(0)
        self._removed.append(var)
        return var
    
    def __len__(self) -> int:
        """Returns the size of the population"""
        return len(self._varelser)
    
    def to_dict(self) -> str:
        var_list = [v.to_dict() for v in self._varelser]
        rem_list = [v.to_dict() for v in self._removed]
        return dict(pop=var_list, rem=rem_list)

    @staticmethod
    def refactor(data):
        p = Population()
        for var in data["pop"]:
            p.add_varelse(Varelse.refactor(var))
        for var in data["rem"]:
            p.add_removed(Varelse.refactor(var))
        return p



if __name__ == '__main__':
    p = Population()
    v1 = Varelse()
    v2 = Varelse(None, 1)
    v3 = Varelse(None, 1)
    v4 = Varelse(None, 2)
    p.add_varelse(v1)
    p.add_varelse(v2)
    p.add_varelse(v3)
    p.add_varelse(v4)
    p.get_varelse()

    data = p.to_dict()
    jsondata = json.dumps(data)
    print(jsondata,"\n")

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

    read_file = None
    with open('data.json', 'r') as f:
        read_file = json.load(f)

    print(read_file)

    data_read = json.loads(jsondata)
    p_json = Population.refactor(data_read)
    p_file = Population.refactor(read_file)
    
    # read from file
    print()
    print(p_file.to_dict())
    print()
    print(p_json.to_dict())
