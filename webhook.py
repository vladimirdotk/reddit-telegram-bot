import ssl
from aiohttp import web

class WebHook():
    def __init__(self, telebot, bot, token, ssl_cert, ssl_priv):
        self.telebot = telebot
        self.bot = bot
        self.token = token
        self.ssl_cert = ssl_cert
        self.ssl_priv = ssl_priv

        self._init_router()
        self._init_context()
    
    def _init_router(self):
        self.app = web.Application()
        self.app.router.add_post(f'/{self.token}/', self.handle)
    
    def _init_context(self):
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.context.load_cert_chain(self.ssl_cert, self.ssl_priv)
    
    async def handle(self, request):
        if request.match_info.get('token') == self.bot.token:
            request_body_dict = await request.json()
            update = self.telebot.types.Update.de_json(request_body_dict)
            self.bot.process_new_updates([update])
            return web.Response()
        else:
            return web.Response(status=403)

    def run(self, host, port):
        web.run_app(
            self.app,
            host=host,
            port=port,
            ssl_context=self.context)

