import http.client


def chamada_api():
    conn = http.client.HTTPSConnection("realtor-api-data.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "2034bfbdc5msh984bddbf35aff92p1839cdjsn5f8d8d94530f",
        'x-rapidapi-host': "realtor-api-data.p.rapidapi.com"
    }
    conn.request("GET", "/detail/school?id=0717323601", headers=headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")


def chamada_api_status():
    """Retorna o status HTTP da requisição para uso em testes."""
    conn = http.client.HTTPSConnection("realtor-api-data.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "2034bfbdc5msh984bddbf35aff92p1839cdjsn5f8d8d94530f",
        'x-rapidapi-host': "realtor-api-data.p.rapidapi.com"
    }
    conn.request("GET", "/detail/school?id=0717323601", headers=headers)
    res = conn.getresponse()
    return res.status