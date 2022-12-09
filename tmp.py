from intra import ic

response = ic.get("users", params={"filter[login]": "jaekkang"})
loc = response.json()
print(loc)
