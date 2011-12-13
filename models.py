from google.appengine.ext import db

class Product(db.Model):
    user = db.UserProperty()
    itemid = db.IntegerProperty()
    name = db.StringProperty()
    category = db.StringProperty()
    image = db.LinkProperty()
    quantity = db.IntegerProperty()
    
def productkey(listname):
    return db.Key.from_path('Grocerylist',listname)

def getproducts(listname):
    products = db.GqlQuery("SELECT * "
                           "FROM Product "
                           "WHERE ANCESTOR IS :1 ",
                           productkey(listname))
    return products

def getproduct(listname,itemid):
    product = db.GqlQuery("SELECT * "
                          "FROM Product "
                          "WHERE itemid = :1 "
                          "AND ANCESTOR IS :2 ",
                          itemid,
                          listname)
    return product
    
def clearproducts():
    db.delete(Product.all())
    
def delproducts():
    db.GqlQuery("DELETE "
                "FROM Product "
                "WHERE")