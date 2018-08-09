import web
import json
        
urls = (
    '/(.*)', 'hello'
)
safename = "webtraindata.json"
app = web.application(urls, globals())
with open(safename, "r") as fh:   
    safe = json.load(fh)

class hello:        
    def POST(self, data):
        data = json.loads(web.data())
        print "data: ", data
        safe.update(data)
        with open(safename, "w") as fh:   
            json.dump(safe, fh)             
        web.header('Access-Control-Allow-Origin', '*')
        return json.dumps(safe)


if __name__ == "__main__":
    web.internalerror = web.debugerror
    #print dir(myform()) 
    #print help(form.AttributeList) 
    #print form.AttributeList
    app.run()