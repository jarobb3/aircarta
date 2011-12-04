import xml.dom.minidom as minidom

def parsestores(xml):
    dom = minidom.parseString(xml) 
    storearr = []
    
    stores = getstores(dom)
    for store in stores:
        storearr.append(parsestore(store))
        
    return storearr

def parsestore(store):
    storeobj = {}
    for node in store.childNodes:
        if node.nodeType == node.ELEMENT_NODE:
            storeobj[node.nodeName] = getText(node.firstChild)

    return storeobj

def parseproducts(xml):
    dom = minidom.parseString(xml)
    productsarr = []
    
    products = getproducts(dom)
    for product in products:
        productsarr.append(parseproduct(product))
        
    return productsarr

def parseproduct(product):
    productobj = {}
    for node in product.childNodes:
        if node.nodeType == node.ELEMENT_NODE:
            productobj[node.nodeName] = getText(node.firstChild)
            
    return productobj

def getstores(storesdom):
    return storesdom.getElementsByTagName('Store')

def getproducts(productsdom):
    return productsdom.getElementsByTagName('Product')

def getText(el):
    if el == None:
        return ""
    return el.data
    