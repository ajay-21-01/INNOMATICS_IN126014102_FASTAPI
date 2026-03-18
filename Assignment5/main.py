from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

products   = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Accessories", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False}
    ,    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}

]

##. day4

@app.put("/products/discount")
def discount(category: str, discount_percent: int):

    updated = []

    for p in products:
        if p["category"].lower() == category.lower():

            new_price = int(p["price"] * (1 - discount_percent / 100))
            p["price"] = new_price

            updated.append({
                "name": p["name"],
                "new_price": new_price
            })

    if not updated:
        return {"message": "No products found in this category"}

    return {
        "updated_count": len(updated),
        "products": updated
    }

## above
@app.get("/products/audit")
def audit():

    total_products = len(products)

    in_stock_products = [p for p in products if p["in_stock"]]
    in_stock_count = len(in_stock_products)

    out_of_stock_names = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive_product = max(products, key=lambda p: p["price"])

    most_expensive = {
        "name": most_expensive_product["name"],
        "price": most_expensive_product["price"]
    }

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": most_expensive
    }

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

# @app.get("/products/search/{keyword}")
# def search(keyword: str):
#     word = keyword.lower()
#     filtered = [p for p in products if word in p["name"].lower()]
#     if filtered:
#         return {"products": filtered, "total": len(filtered)}
#     return {"message": "No products found matching the keyword."}

@app.get("/products/search")
def search_products(keyword: str):
    word = keyword.lower()
    filtered = [p for p in products if word in p["name"].lower()]

    if not filtered:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(filtered),
        "products": filtered
    }


@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):

    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    reverse = True if order == "desc" else False

    sorted_products = sorted(products, key=lambda p: p[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }


@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):

    start = (page - 1) * limit
    end = start + limit

    total_products = len(products)
    total_pages = (total_products + limit - 1) // limit

    paginated = products[start:end]

    return {
        "page": page,
        "limit": limit,
        "total_products": total_products,
        "total_pages": total_pages,
        "products": paginated
    }



@app.get("/orders/search")
def search_orders(customer_name: str):

    keyword = customer_name.lower()

    filtered = [
        o for o in orders
        if keyword in o["customer_name"].lower()
    ]

    if not filtered:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(filtered),
        "orders": filtered
    }

@app.get("/products/sort-by-category")
def sort_by_category():

    sorted_products = sorted(
        products,
        key=lambda p: (p["category"], p["price"])
    )

    return {
        "products": sorted_products
    }

@app.get("/products/browse")
def browse_products(
    keyword: str = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):

    result = products

    # 🔍 Step 1: Filter
    if keyword:
        word = keyword.lower()
        result = [p for p in result if word in p["name"].lower()]

    # ↕️ Step 2: Sort
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda p: p[sort_by], reverse=reverse)

    # 📄 Step 3: Pagination
    total = len(result)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    paginated = result[start:end]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": total_pages,
        "products": paginated
    }

@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):

    start = (page - 1) * limit
    end = start + limit

    total = len(orders)
    total_pages = (total + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_orders": total,
        "total_pages": total_pages,
        "orders": orders[start:end]
    }


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

################################################################################################################

class NewProduct(BaseModel):
    name: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    in_stock: bool = True


@app.post("/products", status_code=201)
def add_product(new_product: NewProduct):

    existing_names = [p["name"].lower() for p in products]

    if new_product.name.lower() in existing_names:
        return {"error": "Product with this name already exists"}

    next_id = max(p["id"] for p in products) + 1

    product = {
        "id": next_id,
        "name": new_product.name,
        "price": new_product.price,
        "category": new_product.category,
        "in_stock": new_product.in_stock
    }

    products.append(product)

    return {"message": "Product added", "product": product}

@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    in_stock: bool = Query(None),
    price: int = Query(None)
):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        return {"error": "Product not found"}

    if in_stock is not None:
        product["in_stock"] = in_stock

    if price is not None:
        product["price"] = price

    return {"message": "Product updated", "product": product}

@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        return {"error": "Product not found"}

    products.remove(product)

    return {"message": f"Product '{product['name']}' deleted"}

@app.put("/products/discount")
def discount(category: str, discount_percent: int):

    updated = []

    for p in products:
        if p["category"].lower() == category.lower():

            new_price = int(p["price"] * (1 - discount_percent / 100))
            p["price"] = new_price

            updated.append({
                "name": p["name"],
                "new_price": new_price
            })

    if not updated:
        return {"message": "No products found in this category"}

    return {
        "updated_count": len(updated),
        "products": updated
    }

cart = []
from fastapi import HTTPException

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):

    product = next((p for p in products if p["id"] == product_id), None)

    # Product not found
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Out of stock
    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    # Check if product already exists in cart
    existing_item = next((item for item in cart if item["product_id"] == product_id), None)

    if existing_item:
        existing_item["quantity"] += quantity
        existing_item["subtotal"] = existing_item["quantity"] * existing_item["unit_price"]

        return {
            "message": "Cart updated",
            "cart_item": existing_item
        }

    # Otherwise add new item
    cart_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }
#hi

@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }

class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str

# @app.post("/cart/checkout")
# def checkout_cart(data: CheckoutRequest):

#     global order_counter

#     if not cart:
#         raise HTTPException(status_code=400, detail="CART_EMPTY")

#     placed_orders = []
#     grand_total = 0

#     for item in cart:

#         order = {
#             "order_id": order_counter,
#             "customer_name": data.customer_name,
#             "product": item["product_name"],
#             "quantity": item["quantity"],
#             "delivery_address": data.delivery_address,
#             "total_price": item["subtotal"],
#             "status": "confirmed"
#         }

#         orders.append(order)
#         placed_orders.append(order)

#         grand_total += item["subtotal"]
#         order_counter += 1

#     cart.clear()

#     return {
#         "orders_placed": placed_orders,
#         "grand_total": grand_total
#     }

@app.post("/cart/checkout")#1
def checkout_cart(data: CheckoutRequest):

    global order_counter

    # BONUS REQUIREMENT
    if not cart:
        raise HTTPException(status_code=400, detail="CART_EMPTY")

    placed_orders = []
    grand_total = 0

    for item in cart:

        order = {
            "order_id": order_counter,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "delivery_address": data.delivery_address,
            "total_price": item["subtotal"],
            "status": "confirmed"
        }

        orders.append(order)
        placed_orders.append(order)

        grand_total += item["subtotal"]
        order_counter += 1

    cart.clear()

    return {
        "orders_placed": placed_orders,
        "grand_total": grand_total
    }

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    item = next((c for c in cart if c["product_id"] == product_id), None)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not in cart")

    cart.remove(item)

    return {
        "message": f"{item['product_name']} removed from cart"
    }