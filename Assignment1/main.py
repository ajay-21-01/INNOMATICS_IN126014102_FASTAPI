from fastapi import FastAPI, Query
app= FastAPI()

products = [
    {"id": 1, "name": "Laptop", "price": 75000, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Mouse", "price": 500, "category": "Accessories", "in_stock": True},
    {"id": 3, "name": "Keyboard", "price": 1500, "category": "Accessories", "in_stock": True},
    {"id": 4, "name": "Monitor", "price": 12000, "category": "Electronics", "in_stock": False},

    # New products added
    {"id": 5, "name": "Laptop Stand", "price": 1200, "category": "Accessories", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 4500, "category": "Accessories", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 2500, "category": "Electronics", "in_stock": True},

    # {"id": 8, "name": "Notebook", "price": 12000, "category": "Book", "in_stock": True}
]

@app.get("/")
def home():
    return {"message": "Welcome to the Product API!"}

@app.get('/products')
def get_products():
    return {"products": products, "total": len(products)}


@app.get('/category/{category_name}')
def get_producs_by_category(category_name: str):
    filtered = [product for product in products if product['category'] == category_name]
    return {"products" : filtered , "total":len(filtered)}


@app.get('/products/instock')
def instock():
    filtered = [product for product in products if product['in_stock'] == True]
    return {"products" : filtered , "total":len(filtered)}

@app.get("/store/summary")
def store_summary():

    total_products = len(products)

    in_stock = sum(1 for p in products if p["in_stock"])
    out_of_stock = sum(1 for p in products if not p["in_stock"])

    categories = list(set(p["category"] for p in products))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": in_stock,
        "out_of_stock": out_of_stock,
        "categories": categories
    }


@app.get('/products/search/{keyword}')
def search(keyword: str):
    word = keyword.lower()
    filtered = [product for product in products if word in product['name'].lower() ]
    if filtered:
        return {"products" : filtered , "total":len(filtered)}
    else:
        return {"message": "No products found matching the keyword."}
    
#bonus 
@app.get('/products/deals')
def deals():
    max_price ,max_id= 0,None
    min_price ,min_id= 0,None
    for i in products:
        if i['price'] > max_price:
            max_price = i['price']
            max_id = i['id']
        if min_price == 0 or i['price'] < min_price:
            min_price = i['price']
            min_id = i['id']
    return {"most_expensive": next((p for p in products if p['id'] == max_id),None), "cheapest" : next((p for p in products if p['id']==min_id),None)}
    