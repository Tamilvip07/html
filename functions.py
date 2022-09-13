from aiohttp import web
from bs4 import BeautifulSoup
from requests import get, post


def handle(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return web.Response(
                text=open("templates/error.html", "r+").read(), content_type="text/html"
            )

    return wrapper


@handle
def phone_info(q: str) -> list:
    headers = {
        "authority": "www.findandtrace.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "max-age=0",
        "origin": "https://www.findandtrace.com",
        "referer": "https://www.2embed.to/",
        "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    }

    data = {
        "mobilenumber": q,
        "submit": "Trace",
    }

    response = post(
        "https://www.findandtrace.com/trace-mobile-number-location",
        headers=headers,
        data=data,
    )

    soup = BeautifulSoup(response.text, "html.parser")
    basic = soup.find("div", {"id": "order_review"})
    if not basic:
        return "Invalid Number/Not Found"
    if not basic.find_all("tr"):
        return "Invalid Number/Not Found"

    data = {}
    for i in basic.find_all("tr"):
        data[i.find("th").text.strip().replace(":", "")] = i.find("td").text.strip()
    next = basic.findNext("div", {"id": "order_review"})
    for i in next.find_all("tr"):
        data[i.find("th").text.strip().replace(":", "")] = i.find("td").text.strip()
    tc_name, tc_carrier = search_phonenumber(q)
    fmt = [
        data["Mobile Phone"],
        data["Telecoms Circle / State"],
        data["Original Network (First Alloted)"],
        data["Service Type / Signal"],
        data["Connection Status"],
        data[f'+91 {data["Mobile Phone"]} - SIM card distributed at'],
        data["Owner / Name of the caller"],
        data["Address / Current GPS Location"],
        data["Last Login Location (Facebook / Google Map / Twitter / Instagram )"],
        data["Last Live location"],
        data["Number of Search History"],
        data["Latest Search Places "],
        data["Telecom Circle Capital "],
        data["Main Language in the telecoms circle "],
        data["Unique search request Ref "],
        tc_name,
        tc_carrier,
    ]
    return fmt


@handle
def search_phonenumber(phno: str) -> list:

    params = {
        "q": phno,
        "countryCode": "+91",
        "type": "4",
        "locAddr": "",
        "placement": "SEARCHRESULTS,HISTORY,DETAILS",
        "encoding": "json",
    }
    headers = {
        "content-type": "application/json; charset=UTF-8",
        "accept-encoding": "gzip",
        "user-agent": "Truecaller/11.75.5 (Android;10)",
        "clientsecret": "lvc22mp3l1sfv6ujg83rd17btt",
        "authorization": "Bearer "
        + "a2i0C--ZjHrjP-gk3zNq11u1KMCWm9I17jsqJ5HHQXbmtmIhx5_vhbIbG6VNirFJ",
    }
    req = get(
        "https://search5-noneu.truecaller.com/v2/search",
        headers=headers,
        params=params,
        timeout=10,
    )
    if req.status_code == 429:
        x = {"errorCode": 429, "errorMessage": "too many requests.", "data": None}
        return x
    elif req.json().get("status"):
        x = {
            "errorCode": 401,
            "errorMessage": "Your previous login was expired.",
            "data": None,
        }
        return x
    else:
        return (
            req.json()["data"][0]["name"],
            req.json()["data"][0]["phones"][0]["carrier"],
        )
