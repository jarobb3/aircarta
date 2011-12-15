from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from google.appengine.api import users

from django.utils.html import strip_tags

import supermarketapiface as facade
import models
import os
import urllib

class Login(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        
        if user:
            username = user.nickname()
            u = models.getuser(username)
            if u and u.userobj:
                if u.store:
                    self.redirect('/list')
                    return
                else:
                    self.redirect('/stores/search')
                    return
            else:
                #create user object if there's none in the database
                newuser = models.User(key_name=username)
                newuser.userobj = user
                newuser.put()
                self.redirect('/stores/search')
                return
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
class Logout(webapp.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/login'))
    
class StoreSearch(webapp.RequestHandler):
    def get(self):
        #search for stores and template
        user = users.get_current_user()
        zipcode = self.request.get('zipcode')
        stores = []
        
        city = ""
        state = ""
        if len(zipcode) != 0:
            citystate = facade.ziptocitystate(zipcode)
            stores = facade.getstoresbycity(citystate[0], citystate[1])
            city = citystate[0]
            state = citystate[1]
        
        template_values = {
            'stores' : stores,
            'zipcode' : zipcode,
            'city' : city,
            'state' : state,
            'user' : user
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/stores.html')
        self.response.out.write(template.render(path, template_values))
        
        
class StoreSelection(webapp.RequestHandler):
    def get(self):
        #save user's store preference to user object
        storeid = self.request.get('storeid')
        storename = self.request.get('storename')
        storeaddress = self.request.get('storeaddress')
        
        store = models.getstore(storeid)
        if not store:
            #store does not exist in the database, add it
            newstore = models.Store(key_name=storeid)
            newstore.storeid = storeid
            newstore.storename = storename
            newstore.storeaddress = storeaddress
            
            newstore.put()
            store = newstore
            
        user = users.get_current_user()
        zipcode = self.request.get('zipcode')
        citystate = facade.ziptocitystate(zipcode)
        city = citystate[0]
        state = citystate[1]
        
        u = models.getuser(user.nickname())
        u.store = store
        u.zipcode = zipcode
        u.city = city
        u.state = state
        
        u.put()
        
        self.redirect('/list')
    
class List(webapp.RequestHandler):
    def get(self):
        message = self.request.get('message')
        if message == 'add':
            itemname = self.request.get('item')
            message = urllib.unquote(itemname) + ' has been added to your list.'
        elif message == 'delete':
            itemname = self.request.get('item')
            message = urllib.unquote(itemname) + ' has been removed from your list.'
        elif message == 'update':
            itemname = self.request.get('item')
            message = 'The quantity of ' + urllib.unquote(itemname) + ' has been updated.'
        elif message == 'send':
            message = 'Your order has been sent! You have 24 hours to update your order before it\'s set in stone.'
        else:
            message = ""
        
        user = users.get_current_user()
        username = user.nickname()
        u = models.getuser(username)
        
        if not u.store:
            self.redirect('/stores/select')
            return
        
        lists = models.getlistsforuser(u.key())
        if len(lists) == 0:
            #user has no lists yet, create their first one
            
            userkey = models.userkey(username)
            newlist = models.GroceryList(parent=userkey)
            
            newlist.store = u.store
            newlist.fulfilled = False
            
            newlist.put()
            thelist = newlist
        else:
            #open most recent list; either at the beginning or end
            thelist = lists[len(lists) - 1]
        
        products = models.getproductsoflist(thelist.key())
        totals = models.listtotals(products,.085)
        
        thelist.subtotal = totals[0]
        thelist.tax = totals[1]
        thelist.total = totals[2]
        
        thelist.put()
        
        template_values = {
           'products' : products,
           'user' : u,
           'list' : thelist,
           'message' : message
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
        self.response.out.write(template.render(path, template_values))
    
class ProductSearch(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        username = user.nickname()
        u = models.getuser(username)
        
        query = self.request.get('q')
        listkey = self.request.get('listkey')
        
        results = []
        if query:
            results = facade.findproductinstore(u.store.storeid, query)

        template_values = {
           'products' : results,
           'q' : query,
           'listkey' : listkey
        }  
              
        path = os.path.join(os.path.dirname(__file__), 'templates/products.html')
        self.response.out.write(template.render(path, template_values))
    
class ProductAdd(webapp.RequestHandler):
    def get(self):
        listkey = self.request.get('listkey')
        thelist = models.getlist(listkey)
        
        productid = self.request.get('itemid')
        productname = self.request.get('itemname')
        category = self.request.get('category')
        image = self.request.get('image')
        
        product = models.Product(parent=thelist.key(), key_name=productid)
        product.productid = productid
        product.productname = productname
        product.category = category
        product.image = image
        product.quantity = 1
        product.baseprice = facade.randomprice()
        product.totalprice = product.baseprice * product.quantity
        product.isTaxable = facade.isTaxable(category)
        
        product.put()
        
        self.redirect('/list?message=add&item=' + urllib.quote_plus(product.productname))
    
class ProductDelete(webapp.RequestHandler):
    def get(self):
        listkey = self.request.get('listkey')
        thelist = models.getlist(listkey)
        
        productid = self.request.get('productid')
        userkeypath = thelist.parent_key().id_or_name()
        listkeypath = thelist.key().id_or_name()
        productkey = models.productkey(userkeypath, listkeypath, productid)
        
        product = models.getproductinlist(productkey)
        
        product.delete()
        
        self.redirect('/list?message=delete&item=' + urllib.quote_plus(product.productname))

class ProductUpdate(webapp.RequestHandler):
    def get(self):
        listkey = self.request.get('listkey')
        
        thelist = models.getlist(listkey)
        
        productid = self.request.get('productid')
        userkeypath = thelist.parent_key().id_or_name()
        listkeypath = thelist.key().id_or_name()
        productkey = models.productkey(userkeypath, listkeypath, productid)
        
        product = models.getproductinlist(productkey)
        
        operation = self.request.get('oper')
        if operation == 'plus':
            product.quantity += 1
        elif operation == 'minus':
            product.quantity -= 1
        else:
            pass
        
        product.totalprice = product.baseprice * product.quantity
        
        product.put()
        
        self.redirect('/list?message=update&item=' + urllib.quote_plus(product.productname))
        
class Checkout(webapp.RequestHandler):
    def get(self):
        #show a list of the user's order
        #show subtotal, tax, service charge, and total
        #Go Back, Pay with: [Google Checkout] [Paypal]
        #send email after this step
        pass
    
class Schedule(webapp.RequestHandler):
    def get(self):
        pass
    
class Email(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        username = user.nickname()
        u = models.getuser(username)
        
        listkey = self.request.get('listkey')
        thelist = models.getlist(listkey)
        products = models.getproductsoflist(thelist.key())
        
        thelist.service = models.calcservice(thelist.subtotal)
        thelist.total = thelist.subtotal + thelist.tax + thelist.service
        thelist.put()
        
        template_values = {
           'products' : products,
           'store' : u.store,
           'user' : u,
           'list' : thelist
        }
        
        intro = """
            Yo,
            
            We just got a new order! Here's the info -- <br />
        
        """
        
        path = os.path.join(os.path.dirname(__file__), 'templates/email.html')
        productlist = template.render(path, template_values)
        
        signature = """
            Hugs, <br />
            AircartApp
        """
        
        html_content = intro + productlist + signature
        text_content = strip_tags(html_content)
        
        message = mail.EmailMessage()
        message.sender = user.email()
        message.subject = "New AirCart Order!"
        message.to = "AirCart FulFillment <aircart@gmail.com>"
        message.body = text_content
        message.html = html_content
        message.send()
        
        self.redirect('/list?message=send')

    
application = webapp.WSGIApplication(
                                        [('/', Login),
                                         ('/login', Login),
                                         ('/logout', Logout),
                                         ('/stores/search', StoreSearch),
                                         ('/stores/select', StoreSelection),
                                         ('/list', List),
                                         ('/products/search', ProductSearch),
                                         ('/products/add', ProductAdd),
                                         ('/products/delete', ProductDelete),
                                         ('/products/update', ProductUpdate),
                                         ('/list/checkout', Checkout),
                                         ('/list/schedule', Schedule),
                                         ('/send', Email)]
                                    , debug=True)

def main():
    run_wsgi_app(application)
    
if __name__ == "__main__":
    main()
