from fastapi import FastAPI
from routers.auth import router as auth_router, create_admin_user
from routers.vendor import router as vendor_router  # Vendor routes
from routers.products import router as products_router  # Products routes
#from routers.productVariant import router as productVariants_router
#from routers.purchaseorder import router as purchaseorder_router  # Purchase order routes
from routers.orderdetails import router as orderdetails_router  # Order details routes
import uvicorn 
# Initialize the FastAPI application
app = FastAPI()

# Include the authentication router
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Include the vendor router
app.include_router(vendor_router, prefix="/vendors", tags=["Vendor Management"])

# Include the product router
app.include_router(products_router, prefix="/products", tags=["Product Management"])

#app.include_router(productVariants_router, prefix="/productVariants", tags=["Variants"])

# Include the purchase order router
# app.include_router(purchaseorder_router, prefix="/purchaseorder", tags=["Purchase Order Management"])

# Include the order details router
app.include_router(orderdetails_router, prefix="/orderdetails", tags=["Order Details Management"])

# Ensure the default admin user exists on application startup
@app.on_event("startup")
async def ensure_admin_user():
    """
    Startup event to create the default admin user if it doesn't exist.
    """
    await create_admin_user()

if __name__ == "__main__":
    uvicorn.run("main:app", port=8001, host='127.0.0.1',
                reload=True)