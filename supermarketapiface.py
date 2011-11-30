import google.appengine.api.urlfetch as urlfetch
import urllib

apikey = 'ec4f187ef5'
baseurl = 'http://www.SupermarketAPI.com/api.asmx/'

def getstoresbyzip(zipcode):
    apifunction = 'StoresByZip'
    base = baseurl + apifunction
    
    params = {'apikey': apikey, 'zipcode' : zipcode }
    url = __addparameters( base, params )
    
    response = urlfetch.fetch(url)
    return response

def getstoresbycity(city,state):
    apifunction = 'StoresByCityState'
    base = baseurl + apifunction
    
    city = urllib.quote(city)
    params = { 'apikey' : apikey, 'selectedcity' : city, 'selectedstate' : state }
    url = __addparameters( base, params )
    
    response = urlfetch.fetch(url)
    return response

def getstoresbyname(storename):
    apifunction = 'ReturnStoresByName'
    base = baseurl + apifunction
    
    params = { 'apikey' : apikey, 'storename' : storename }
    url = __addparameters( base, params )
    
    response = urlfetch.fetch(url)
    return response

def searchbyproductname(productname):
    apifunction = 'SearchByProductName'
    base = baseurl + apifunction
    
    params = { 'apikey' : apikey, 'itemname' : productname }
    url = __addparameters( base, params )
    
    response = urlfetch.fetch(url)
    return response

def findproductinstore(productname,storeid):
    apifunction = 'SearchForItem'
    base = baseurl + apifunction
    
    params = { 'apikey' : apikey, 'storeid' : storeid, 'itemname' : productname}
    url = __addparameters( base, params )
    
    response = urlfetch.fetch(url)
    return response

def getproduct(productid):
    apifunction = 'SearchByItemID'
    base = baseurl +apifunction
    
    params = { 'apikey' : apikey, 'itemid' : productid }
    url= __addparameters( base, params )
    
    response = urlfetch.fetch(url)
    return response
    
def __addparameters(baseurl, params):
    url = baseurl+'?'
    for k,v in params.iteritems():
        url += k+'='+v+'&'
    url = url.rstrip('&')
    
    return url