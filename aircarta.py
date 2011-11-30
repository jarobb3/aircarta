from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import supermarketapiface as facade

class testing(webapp.RequestHandler):
    def get(self):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header("Access-Control-Allow-Credentials", "true");
        #self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Content-Type'] = 'text/xml'
        
        #zipcode = self.request.get('zip')
        #stores = facade.getstoresbyzip(zipcode)
        
        #city = 'San Francisco'
        #state = 'CA'
        #stores = facade.getstoresbycity(city,state)
        
        #storename = 'Safeway'
        #stores = facade.getstoresbyname(storename)
        
        #self.response.out.write(stores.content)
        
        #productname = 'milk'
        #items = facade.searchbyproductname(productname)
        
        #productname = 'milk'
        #storeid = 'e6k3fjw75k'
        #items = facade.findproductinstore(productname,storeid)
        
        #productid = '29467'
        #items = facade.getproduct(productid)
        
        #self.response.out.write(items.content)
        
        
application = webapp.WSGIApplication(
                                        [('/', testing)]
                                    ,debug=True)

def main():
    run_wsgi_app(application)
    
if __name__ == "__main__":
    main()