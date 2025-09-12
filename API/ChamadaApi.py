import http.client

conn = http.client.HTTPSConnection("realtor-api-data.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "2034bfbdc5msh984bddbf35aff92p1839cdjsn5f8d8d94530f",
    'x-rapidapi-host': "realtor-api-data.p.rapidapi.com"
}

conn.request("GET", "/detail/school?id=0717323601", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))