from google.appengine.ext import db
import locale


class Store(db.Model):
    storeid = db.StringProperty()
    storename = db.StringProperty()
    storeaddress = db.StringProperty()
    
def getstore(storeid):
    storekey = db.Key.from_path('Store', storeid)
    return db.get(storekey)

class Product(db.Model):
    productid = db.StringProperty()
    productname = db.StringProperty()
    category = db.StringProperty()
    image = db.StringProperty()
    quantity = db.IntegerProperty()
    baseprice = db.FloatProperty()
    totalprice = db.FloatProperty()
    isTaxable = db.BooleanProperty()
    
def productkey(username,listid,productid):
    return db.Key.from_path('User', username, 'GroceryList', listid, 'Product', productid)

def getproductsoflist(listkey):
    query = db.Query(Product)
    query.ancestor(listkey)
    
    return query.fetch(50)

def getproductinlist(productkey):
    return db.get(productkey)


class User(db.Model):
    userobj = db.UserProperty()
    store = db.ReferenceProperty(Store)
    zipcode = db.StringProperty()
    city = db.StringProperty()
    state = db.StringProperty()
    createddate = db.DateTimeProperty(auto_now_add=True)
    logindate = db.DateTimeProperty(auto_now=True)

def getuser(username):
    key = userkey(username)
    return db.get(key)

def userkey(username):
    return db.Key.from_path('User', username)


class GroceryList(db.Model):
    store = db.ReferenceProperty(Store)
    createddate = db.DateTimeProperty(auto_now_add=True)
    fulfilled = db.DateTimeProperty()
    subtotal = db.FloatProperty()
    tax = db.FloatProperty()
    service = db.FloatProperty()
    total = db.FloatProperty()
    
def listkey(username):
    return db.Key.from_path('User', username)

def getlistsforuser(userkey):
    query = db.Query(GroceryList)
    query.ancestor(userkey)
    
    return query.fetch(10)

def getlist(listkey):
    return db.get(listkey)

def listtotals(products, taxrate):
    subtotal = 0
    tax = 0
    
    for product in products:
        subtotal += product.totalprice
        tax += product.totalprice * taxrate * product.isTaxable
        
    subtotal = round(subtotal,2)
    tax = round(tax,2)
    total = subtotal + tax
    return subtotal, tax, total

def calcservice(subtotal):
    return round(0.05*subtotal,2)