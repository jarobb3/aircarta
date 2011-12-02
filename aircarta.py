import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
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
        
class Stores(webapp.RequestHandler):  
    def get(self):
        zipcode = self.request.get('zipcode')
        #extrapolate to city using usps zipcode lookup
        
        if len(zipcode) == 0:
            stores = []
        else:
            stores = facade.getstoresbyzip(zipcode)
        
        template_values = {
           'stores' : stores,
           'zipcode' : zipcode
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/stores.html')
        self.response.out.write(template.render(path, template_values))
        
class Products(webapp.RequestHandler):
    def get(self):
        storeid = self.request.get('storeId')
        storename = self.request.get('storename')
        query = self.request.get('q')
        
        products = facade.findproductinstore(storeid,query)
        
        template_values = {
           'products' : products,
           'storename' : storename,
           'q' : query
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/products.html')
        self.response.out.write(template.render(path, template_values))
        
    
          
application = webapp.WSGIApplication(
                                        [('/', testing),
                                         ('/stores', Stores),
                                         ('/products', Products)]
                                    ,debug=True)

def main():
    run_wsgi_app(application)
    
if __name__ == "__main__":
    main()