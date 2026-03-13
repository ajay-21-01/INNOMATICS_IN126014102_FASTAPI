from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

products = [
    {"id": 1, "name": "Laptop", "price": 75000, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Mouse", "price": 500, "category": "Accessories", "in_stock": True},
    {"id": 3, "name": "Keyboard", "price": 1500, "category": "Accessories", "in_stock": True},
    {"id": 4, "name": "Monitor", "price": 12000, "category": "Electronics", "in_stock": False},
    {"id": 5, "name": "Laptop Stand", "price": 1200, "category": "Accessories", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 4500, "category": "Accessories", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 2500, "category": "Electronics", "in_stock": True}
]

@app.get("/")
def home():
    return {"message": "Welcome to the Product API!"}

@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

@app.get("/category/{category_name}")
def get_products_by_category(category_name: str):
    filtered = [p for p in products if p["category"] == category_name]
    return {"products": filtered, "total": len(filtered)}

@app.get("/products/instock")
def instock():
    filtered = [p for p in products if p["in_stock"]]
    return {"products": filtered, "total": len(filtered)}

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

@app.get("/products/search/{keyword}")
def search(keyword: str):
    word = keyword.lower()
    filtered = [p for p in products if word in p["name"].lower()]
    if filtered:
        return {"products": filtered, "total": len(filtered)}
    return {"message": "No products found matching the keyword."}

@app.get("/products/deals")
def deals():
    max_price = max(products, key=lambda p: p["price"])
    min_price = min(products, key=lambda p: p["price"])
    return {"most_expensive": max_price, "cheapest": min_price}

def filter_products_logic(category=None, min_price=None, max_price=None, in_stock=None):
    results = products
    if category is not None:
        results = [p for p in results if p["category"] == category]
    if min_price is not None:
        results = [p for p in results if p["price"] >= min_price]
    if max_price is not None:
        results = [p for p in results if p["price"] <= max_price]
    if in_stock is not None:
        results = [p for p in results if p["in_stock"] == in_stock]
    return results

@app.get("/products/filter")
def filter_products(
    category: str = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None),
    in_stock: bool = Query(None)
):
    result = filter_products_logic(category, min_price, max_price, in_stock)
    return {"filtered_products": result, "count": len(result)}

@app.get("/products/{id}/price")
def get_price(id: int):
    product = next((p for p in products if p["id"] == id), None)
    if not product:
        return {"error": f"Product {id} not found"}
    return {"id": id, "price": product["price"]}

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(None, max_length=300)

feedback_storage = []

@app.post("/feedback")
def feedback(feedback: CustomerFeedback):
    product = next((p for p in products if p["id"] == feedback.product_id), None)
    if not product:
        return {"error": f"product {feedback.product_id} not found"}
    feedback_data = feedback.dict()
    feedback_storage.append(feedback_data)
    return {"message": "Feedback submitted successfully", "feedback": feedback_data}

@app.get("/products/summary")
def products_summary():
    total_products = len(products)
    in_stock_count = sum(1 for p in products if p["in_stock"])
    out_of_stock_count = sum(1 for p in products if not p["in_stock"])
    most_expensive_product = max(products, key=lambda p: p["price"])
    cheapest_product = min(products, key=lambda p: p["price"])
    most_expensive = {"name": most_expensive_product["name"], "price": most_expensive_product["price"]}
    cheapest = {"name": cheapest_product["name"], "price": cheapest_product["price"]}
    categories = list(set(p["category"] for p in products))
    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": most_expensive,
        "cheapest": cheapest,
        "categories": categories
    }

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: list[OrderItem] = Field(..., min_length=1)

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed = []
    failed = []
    grand_total = 0
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
            continue
        if not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
            continue
        subtotal = product["price"] * item.quantity
        grand_total += subtotal
        confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})
    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)
    delivery_address: str = Field(..., min_length=5)

orders = []
order_counter = 1

@app.post("/orders")
def place_order(order_data: OrderRequest):
    global order_counter
    product = next((p for p in products if p["id"] == order_data.product_id), None)
    if not product:
        return {"error": "Product not found"}
    if not product["in_stock"]:
        return {"error": f"{product['name']} is out of stock"}
    total_price = product["price"] * order_data.quantity
    order = {
        "order_id": order_counter,
        "customer_name": order_data.customer_name,
        "product": product["name"],
        "quantity": order_data.quantity,
        "delivery_address": order_data.delivery_address,
        "total_price": total_price,
        "status": "pending"
    }
    orders.append(order)
    order_counter += 1
    return {"message": "Order placed successfully", "order": order}

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if not order:
        return {"error": "Order not found"}
    return order

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if not order:
        return {"error": "Order not found"}
    order["status"] = "confirmed"
    return {"message": "Order confirmed", "order": order}

