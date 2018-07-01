# -*- coding: utf-8 -*-
import json
import datetime
import web
from web import form
from forms import *
from mainform import mainform

store_filename = "store.json"
store = json.load(open(store_filename))

render = web.template.render('templates/', base='layout')
urls = ('/', 'index',
        '/session/(\d+)/(.*)', 'session',
        '/save/(\d+)/(.*)', 'save')
app = web.application(urls, globals())

renderdict = {
    12: render.lesson12,
    43: render.lesson43,
}
formdict = {
    12: lesson12,
    43: lesson43,
}


class index(object):

    def get_sessions(self, tform):
        for item in tform.inputs:
            if not isinstance(item, web.form.Dropdown):
                continue
            store_location = store.get(item.name, {})
            session = ["new"] + sorted(store_location.keys(), reverse=True)
            item.args = session

    def GET(self):
        tform = mainform()
        self.get_sessions(tform)
        return render.index(tform)

    def POST(self):
        tform = mainform()
        self.get_sessions(tform)
        return render.index(tform)


class session(object):
    def POST(self, location, session):
        print "session:post: location={!r}, session={!r}".format(location, session)
        print web.data()
        tform = formdict[int(location)]()
        if session == "new":
            session = datetime.datetime.now().isoformat()
            print "get new session for lesson {}".format(location)
        else:
            print "get session {} for location {}".format(session, location)
            for item in tform.inputs:
                item.set_value(store[location][session][item.name])
        tform.valid = True
        return renderdict[int(location)](tform, session)


class save(object):
    def POST(self, location, session):
        print "save:post: location={!r}, session={!r}".format(location, session)
        print web.data()
        tform = formdict[int(location)]()
        tform.validates()
        print "saving {!r}, session {!r}".format(location, session)
        store_location = store.get(location, {})
        store[location] = store_location
        store_session = store[location].get(session, {})
        for item in tform.inputs:
            store_session[item.name] = item.value
        store[location][session] = store_session
        json.dump(store, open(store_filename, 'w'), indent=4)
        return renderdict[int(location)](tform, session)


if __name__ == "__main__":
    web.internalerror = web.debugerror
    #print dir(myform()) 
    #print help(form.AttributeList) 
    #print form.AttributeList
    app.run()

