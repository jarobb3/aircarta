from google.appengine.ext import db

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
    quantity = db.IntegerProperty(default=1)
    baseprice = db.FloatProperty(default=0.0)
    totalprice = db.FloatProperty(default=0.0)
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
    created = db.DateTimeProperty(auto_now_add=True)
    submitted = db.DateTimeProperty()
    fulfilled = db.DateTimeProperty()
    subtotal = db.FloatProperty(default=0.0)
    tax = db.FloatProperty(default=0.0)
    service = db.FloatProperty(default=0.0)
    total = db.FloatProperty(default=0.0)
    
def alllists():
    return GroceryList.all()
    
def listkey(username):
    return db.Key.from_path('User', username)

def getlistsforuser(userkey):
    query = db.Query(GroceryList)
    query.ancestor(userkey)
    query.order('-created')
    
    return query.run()

def getlistsforuseratstore(userkey,storekey):
    query = db.Query(GroceryList)
    query.ancestor(userkey)
    query.filter('store = ', storekey)
    query.order('-created')
    
    return query.fetch(10)

def deleteuserlists(userkey):
    query = db.Query(GroceryList)
    query.ancestor(userkey)
    
    results = query.run()
    count = 0
    for item in results:
        count+=1
        item.delete()
        
    return count

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