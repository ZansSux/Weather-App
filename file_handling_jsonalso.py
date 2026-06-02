import json
data = '{"name": "Sam", "age" :20}'
print(data)
jss = json.loads(data)
print(jss["name"])
with open ("test.json", "r") as file:
    data1 = json.load(file)
    print(data1)
    
dictt = {
    "name" : "Amy",
    "age" : 20
}

data2 = json.dumps(dictt)
print(data2)

a = input("Change?")
if a == 'y':
    with open("test.json","w") as file:
        json.dump(dictt, file, indent=4)