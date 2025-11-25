from typing import Optional, List
from fastapi import FastAPI, HTTPException, status, Request, Query
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from datetime import datetime, timezone

app = FastAPI()

# In-memory product store for demo
products = []

CATEGORIES = ["อาหาร", "เครื่องดื่ม", "ของใช้", "เสื้อผ้า"]


# Product model for request validation
class Product(BaseModel):
    name: str
    sku: str
    price: float
    stock: int
    category: str

# Redirect root ("/") to /docs
@app.get("/")
def root():
    return RedirectResponse(url="/docs")


def validate_product(data):
    errors = []
    # Name must not be empty
    if not data.get("name") or not str(data["name"]).strip():
        errors.append("ชื่อสินค้าต้องไม่ว่าง")
    # SKU must not be empty, at least 3 letters, and unique
    sku = data.get("sku", "")
    if not sku or len(sku) < 3:
        errors.append("รหัสสินค้าต้องมีอย่างน้อย 3 ตัวอักษร")
    elif any(p['sku'] == sku for p in products):
        errors.append("รหัสสินค้าห้ามซ้ำกับสินค้าเดิม")
    # Price must be > 0
    try:
        price = float(data.get("price", 0))
        if price <= 0:
            errors.append("ราคาต้องมากกว่า 0")
    except Exception:
        errors.append("ราคาต้องมากกว่า 0")
    # Stock must be >= 0
    try:
        stock = int(data.get("stock", -1))
        if stock < 0:
            errors.append("จำนวนคงเหลือต้องไม่ติดลบ")
    except Exception:
        errors.append("จำนวนคงเหลือต้องไม่ติดลบ")
    # Category must be valid
    if data.get("category") not in CATEGORIES:
        errors.append(f"หมวดหมู่ต้องเป็นหนึ่งใน {CATEGORIES}")
    return errors


# 1 Product Creation Endpoint

@app.post("/api/products", status_code=201)
async def add_product(product: Product, request: Request):
    data = product.dict()
    errors = validate_product(data)
    if errors:
        return JSONResponse(status_code=400, content={"errors": errors})
    # Assign id and createdAt
    new_id = len(products) + 1
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    product_out = {
        "id": new_id,
        **data,
        "createdAt": created_at
    }
    products.append(product_out)
    return product_out


# 2 Product Listing Endpoint

@app.get("/api/products")
async def get_products(category: Optional[str] = Query(None)):
    if category:
        filtered = [p for p in products if p["category"] == category]
        return filtered
    return products



class SellRequest(BaseModel):
    productId: int
    quantity: int


# 3 Product Selling Endpoint

@app.post("/api/products/sell")
async def sell_product(sell: SellRequest):
    # Find product by id
    product = next((p for p in products if p.get("id") == sell.productId), None)
    if not product:
        return JSONResponse(status_code=404, content={"error": "ไม่พบสินค้า"})
    if sell.quantity <= 0:
        return JSONResponse(status_code=400, content={"error": "จำนวนสินค้าต้องมากกว่า 0"})
    if product["stock"] < sell.quantity:
        return JSONResponse(status_code=400, content={"error": "จำนวนสินค้าในสต็อกไม่เพียงพอ"})
    product["stock"] -= sell.quantity
    return {"message": "ขายสินค้าสำเร็จ", "product": product}


# 4 Product Search Endpoint

@app.get("/api/products/search")
async def search_products(keyword: str = Query(..., min_length=1)):
    keyword_lower = keyword.lower()
    results = [
        p for p in products
        if keyword_lower in p["name"].lower() or keyword_lower in p["sku"].lower()
    ]
    return results



# 5 Bulk Price Update Endpoint

class BulkPriceUpdateItem(BaseModel):
    productId: int
    newPrice: float

class BulkPriceUpdateRequest(BaseModel):
    updates: List[BulkPriceUpdateItem] = Field(..., min_items=1)

@app.put("/api/products/bulk-price-update")
async def bulk_price_update(request: BulkPriceUpdateRequest):
    updated_count = 0
    for item in request.updates:
        product = next((p for p in products if p.get("id") == item.productId), None)
        if product and item.newPrice > 0:
            product["price"] = item.newPrice
            updated_count += 1
    return {
        "updated": updated_count,
        "total": len(request.updates)
    }