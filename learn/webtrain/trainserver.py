import web
import json
import os

urls = (
    '/json/(.*)', 'main',
    '/hello', 'hello'
)
safename = os.path.join(os.path.dirname(__file__), "webtraindata.json")
app = web.application(urls, globals())
with open(safename, "r") as fh:
    safe = json.load(fh)


class main:
    def POST(self, data):
        data = json.loads(web.data())
        # print "data: ", data
        for key in data:
            if key not in safe:
                safe[key] = {}
            safe[key].update(data[key])
        with open(safename, "w") as fh:
            json.dump(safe, fh, indent=4)
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
