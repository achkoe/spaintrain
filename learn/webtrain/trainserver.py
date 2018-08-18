import web
import json

urls = (
    '/json/(.*)', 'main',
    '/hello', 'hello'
)
safename = "webtraindata.json"
app = web.application(urls, globals())
with open(safename, "r") as fh:
    safe = json.load(fh)


class main:
    def POST(self, data):
        data = json.loads(web.data())
        # print "data: ", data
        safe.update(data)
        with open(safename, "w") as fh:
            json.dump(safe, fh)
        web.header('Access-Control-Allow-Origin', '*')
        return json.dumps(safe)

class hello:
    def POST(self):
        return "Hello post"

    def GET(self):
        return "Hello get"

if __name__ == "__main__":
    web.internalerror = web.debugerror
    app.run()