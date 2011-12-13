import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.api import mail
from google.appengine.api import users

from django.utils.html import strip_tags

import supermarketapiface as facade
import models

class Login(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        
        if user:
            self.redirect('/stores')
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
class Logout(webapp.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/'))

class testing(webapp.RequestHandler):
    def get(self):
        mail.send_mail(sender="Example.com Support <support@example.com>",
              to="Albert Johnson <Albert.Johnson@example.com>",
              subject="Your account has been approved",
              body="""
                Dear Albert:
                
                Your example.com account has been approved.  You can now visit
                http://www.example.com/ and sign in using your Google Account to
                access new features.
                
                Please let us know if you have any questions.
                
                The example.com Team
                """)
        #print message.to
        #message.send()
        #zipcode = self.request.get('zip')
        #citystate = facade.ziptocitystate(zipcode)
        #x = facade.getstoresbycity(citystate[0],citystate[1])
        
        #self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        #self.response.headers.add_header("Access-Control-Allow-Credentials", "true");
        #self.response.headers['Content-Type'] = 'application/json'
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
        
        
        #self.response.out.write(x)
        
class Stores(webapp.RequestHandler):  
    def get(self):
        user = users.get_current_user()
        zipcode = self.request.get('zipcode')
        #extrapolate to city using usps zipcode lookup
        
        if len(zipcode) == 0:
            stores = []
        else:
            citystate = facade.ziptocitystate(zipcode)
            stores = facade.getstoresbycity(citystate[0],citystate[1])
        
        template_values = {
           'stores' : stores,
           'zipcode' : zipcode,
           'user' : user
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
        user = users.get_current_user()
        message = ''
        
        if action == 'add':
            itemaddedname = self.request.get('item')
            message = itemaddedname + ' has been added to your list...'
        elif action == 'clear':
            models.clearproducts()
            message = 'list cleared...'
        elif action == 'del':
            itemid = int(self.request.get('item'))
            products = models.getproducts('list')
            for product in products:
                if product.itemid == itemid:
                    message = product.name + ' has been removed from your list...'
                    product.delete()
                    break
        elif action == 'sent':
            message = 'your list has been sent. thanks!'
            
        listname = "list"
        products = models.getproducts(listname)
        storename = self.request.get('storename') or memcache.get(key='storename')
        
        #count = 0
        #for p in products:
            #count = count + 1
        
        #print count
        #return
        template_values = {
           'products' : products,
           'listname' : listname,
           'storename': storename,
           'message' : message,
           'user' : user
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
        self.response.out.write(template.render(path, template_values))
        

class Grocerylist(webapp.RequestHandler):
    def get(self):    
        listname = "list"
        user = users.get_current_user()
        key = models.productkey(listname)
        p = models.Product(parent=key)
        
        p.user = user
        p.itemid = int(self.request.get('itemid'))
        p.name = self.request.get('itemname')
        p.category = self.request.get('category')
        p.image = self.request.get('itemimage')
        p.quantity = 1
        
        p.put()
        
        self.redirect('/list?act=add&item='+p.name)
        
class Message(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        listname = self.request.get('listname')
        products = models.getproducts(listname)
        storename = self.request.get('storename') or memcache.get(key='storename')
       
        
        template_values = {
           'products' : products,
           'storename' : storename,
           'user' : user
        }
        
        sender = user.email()
        subject = "New Cart Order!"
        to = "AirCart Fulfillment <aircarty@gmail.com>"
        
        intro = """   
            Yo,
            
            We just got a new order! Here's the user's list --
        """
        
        path = os.path.join(os.path.dirname(__file__), 'templates/email.html')
        productlist = template.render(path,template_values)        
        
        signature = """
            Hugs,<br />
            AircartApp
            """
        
        html_content = intro+productlist+signature
        text_content = strip_tags(html_content)
        
        message = mail.EmailMessage()
        message.sender = sender
        message.subject = subject
        message.to = to
        message.body = text_content
        message.html = html_content
        
        #self.response.headers['Content-Type'] = 'text/html'
        
        #print message.body
        #self.response.out.write(message.body)            
        message.send()
        
        self.redirect('/list?act=sent')
    
          
application = webapp.WSGIApplication(
                                        [('/', Login),
                                         ('/logout', Logout),
                                         ('/test', testing),
                                         ('/stores', Stores),
                                         ('/products', Products),
                                         ('/add', Grocerylist),
                                         ('/list', List),
                                         ('/send', Message)]
                                    ,debug=True)

def main():
    run_wsgi_app(application)
    
if __name__ == "__main__":
    main()