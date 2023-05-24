from fastapi import FastAPI,HTTPException,Query
from odmantic import AIOEngine, Model
from pydantic import BaseModel
from typing import List
from bson import ObjectId

app = FastAPI()

# MongoDB connection URI
mongo_uri = "mongodb+srv://summerSmasher:ss123123@cluster0.aguydlr.mongodb.net/?retryWrites=true&w=majority"

# Create an instance of the ODMANTIC AIOEngine
from pymongo import MongoClient
from odmantic import SyncEngine
client = MongoClient(mongo_uri)
engine = SyncEngine(client=client, database="pens")

# Product model
class InventoryProduct(Model):
    product_name: str
    variant: str
    sku: str
    price: float
    qty: int
    description: str

@app.get("/") 
async def root():
    return {"hi this is my USC summer smasher coding assignment page! Hope you like it!(◍•ᴗ•◍)"}


# Add new product
@app.post("/v1/CZeroPens/products")
async def create_product(product: InventoryProduct):
    created_product = engine.save(product)
    return created_product

# Get all products
@app.get("/v1/CZeroPens/products")
async def get_all_products():
    products = engine.find(InventoryProduct)
    
    # Convert the results to a list
    results_list = list(products)
    return results_list 

#Update Product
@app.put("/v1/CZeroPens/products/{product_id}")
async def update_product(product_id: str, updated_product: InventoryProduct):
    # Check if the product exists
    existing_product = engine.find_one(InventoryProduct, InventoryProduct.id == ObjectId(product_id))
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update the product fields with the provided values
    existing_product.product_name = updated_product.product_name
    existing_product.variant = updated_product.variant
    existing_product.sku = updated_product.sku
    existing_product.price = updated_product.price
    existing_product.qty = updated_product.qty
    existing_product.description = updated_product.description

    # Save the updated product to the database
    updated_product = engine.save(existing_product)

    return existing_product

# Remove a product
@app.delete("/v1/CZeroPens/products/{product_id}")
async def delete_product(product_id: str):
    deleted_product = engine.find_one(InventoryProduct, InventoryProduct.id == ObjectId(product_id))
    if not deleted_product:
        raise HTTPException(status_code=404, detail="Product not found")
    engine.delete(deleted_product)
    return {"message": "Product deleted successfully"}

# Buy Products (Shopping Cart)
@app.post("/v1/CZeroPens/buy")
async def buy_products(products: List[dict]):
    total_price = 0

    for product in products:
        product_id = product.get("_id")
        quantity = product.get("qty")

        # Check if the product exists
        existing_product = engine.find_one(InventoryProduct, InventoryProduct.id == ObjectId(product_id))
        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Check if the product has sufficient quantity
        if existing_product.qty < quantity:
            raise HTTPException(status_code=400, detail="Insufficient product quantity")

        # Calculate the total price based on the product price and quantity
        product_price = existing_product.price
        total_price += product_price * quantity

        # Update the product quantity
        existing_product.qty -= quantity
        engine.save(existing_product)

    return {"total_price": total_price}

#Global Search
@app.get("/v1/CZeroPens/products/search")
async def search_products(query: str = Query(...)):
    # Perform a case-insensitive search on all fields using a regex pattern
    pattern = f".*{query}.*"
    search_results = engine.find(InventoryProduct, {
        "$or": [
            {field: {"$regex": pattern, "$options": "i"}} for field in InventoryProduct.__fields__.keys()
        ]
    })

    # Convert the search results to a list
    search_results_list = list(search_results)

    return search_results_list