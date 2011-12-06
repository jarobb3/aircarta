import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

import supermarketapiface as facade
import models

class testing(webapp.RequestHandler):
    def get(self):
        zipcode = self.request.get('zip')
        citystate = facade.ziptocitystate(zipcode)
        x = facade.getstoresbycity(citystate[0],citystate[1])
        
        #self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        #self.response.headers.add_header("Access-Control-Allow-Credentials", "true");
        self.response.headers['Content-Type'] = 'application/json'
        #self.response.headers['Content-Type'] = 'text/xml'
        
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
        
        self.response.out.write(x)
        
class Stores(webapp.RequestHandler):  
    def get(self):
        zipcode = self.request.get('zipcode')
        #extrapolate to city using usps zipcode lookup
        
        if len(zipcode) == 0:
            stores = []
        else:
            citystate = facade.ziptocitystate(zipcode)
            stores = facade.getstoresbycity(citystate[0],citystate[1])
        
        template_values = {
           'stores' : stores,
           'zipcode' : zipcode
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/stores.html')
        self.response.out.write(template.render(path, template_values))
        
class Products(webapp.RequestHandler):
    def get(self):
        storeid = self.request.get('storeId') or memcache.get(key='storeid')
        storename = self.request.get('storename') or memcache.get(key='storename')
        
        if not storeid or not storename:
            self.redirect('stores')
            return
        
        memcache.add(key='storeid',value=storeid)
        memcache.add(key='storename',value=storename)
        
        query = self.request.get('q')
        
        if len(query) == 0:
            products = []
        else:
            products = facade.findproductinstore(storeid,query)
        
        template_values = {
           'products' : products,
           'storename' : storename,
           'storeid' : storeid,
           'q' : query
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/products.html')
        self.response.out.write(template.render(path, template_values))
        
class List(webapp.RequestHandler):
    def get(self):
        action = self.request.get('act')
        if action == 'clear':
            models.clearproducts()
            
        products = models.getproducts()
        
        #count = 0
        #for p in products:
            #count = count + 1
        
        #print count
        #return
        template_values = {
           'products' : products
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
        self.response.out.write(template.render(path, template_values))
        

class Grocerylist(webapp.RequestHandler):
    def get(self):    
        listname = "list"
        key = models.productkey(listname)
        p = models.Product(parent=key)
        
        p.itemid = int(self.request.get('itemid'))
        p.name = self.request.get('itemname')
        p.category = self.request.get('category')
        p.image = self.request.get('itemimage')
        
        p.put()
        
        self.redirect('/list')
        
    
          
application = webapp.WSGIApplication(
                                        [('/', testing),
                                         ('/stores', Stores),
                                         ('/products', Products),
                                         ('/add',Grocerylist),
                                         ('/list', List)]
                                    ,debug=True)

def main():
    run_wsgi_app(application)
    
if __name__ == "__main__":
    main()