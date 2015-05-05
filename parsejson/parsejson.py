import json
f = open("ok", "r")
obj = json.loads(f.read())
f.close()

print obj.keys()

print len(obj["data"])

