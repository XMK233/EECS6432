import requests
r = requests.get("http://192.168.56.105/dataop/SelectUsers?recordsCnt=50")
print(r.elapsed.microseconds)

