import web
import json

urls = (
    '/(.*)', 'main'
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


if __name__ == "__main__":
    web.internalerror = web.debugerror
    app.run()
