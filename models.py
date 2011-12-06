from google.appengine.ext import db

class Product(db.Model):
    itemid = db.IntegerProperty()
    name = db.StringProperty()
    category = db.StringProperty()
    image = db.LinkProperty()
    
def productkey(listname):
    return db.Key.from_path('Grocerylist',listname)

def getproducts():
    products = db.GqlQuery("SELECT * "
                           "FROM Product "
                           "WHERE ANCESTOR IS :1 ",
                           productkey("list"))
    return products

def clearproducts():
    db.delete(Product.all())