import logging
import jinja2
from aiohttp import web
import aiohttp_jinja2
from functions import phone_info, handle
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.WARNING,
)


routes = web.RouteTableDef()


@routes.get('/')
async def hello_world(request) -> web.Response:
    return web.Response(text=open("templates/main.html", "r+").read(), content_type="text/html")


@routes.post('/info')
@aiohttp_jinja2.template('response.html')
async def verify_number(request) -> web.Response:
    try:
        get_no: str = await request.post()
        number: str = get_no["phone"]
        info_ = phone_info(number)
        render = {"Phone": info_[0], "Name" : info_[15], "State": info_[1], "Telecomcircle": info_[16], "Operator": info_[
            3], "Service": info_[4], "Simcard": info_[5], "Telecomcapital": info_[13], "Lastsearch": info_[1]}
        return render
    except Exception as e:
        return web.Response(text="Invalid Number/Not Found", content_type="text/html")

if __name__ == "__main__":
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("./templates"))
    app.add_routes(routes)
    web.run_app(app, port=8080)
