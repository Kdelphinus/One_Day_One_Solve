from intra import ic

response = ic.get("users", params={"filter[login]": "jiyeolee"})
loc = response.json()
print(loc)
