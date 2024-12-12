from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime
import database
from routers.auth import get_current_active_user

router = APIRouter(dependencies=[Depends(get_current_active_user)])

# Pydantic Models for Order and Details
class PurchaseOrder(BaseModel):
    orderID: int
    orderDate: datetime
    orderStatus: str
    statusDate: datetime
    vendorID: int

class PurchaseOrderDetail(BaseModel):
    orderDetailID: int
    orderID: int
    orderQuantity: int
    expectedDate: datetime
    actualDate: datetime = None
    productID: int

class OrderWithDetails(BaseModel):
    order: PurchaseOrder
    details: list[PurchaseOrderDetail]

# Endpoint to get purchase order with its details
@router.get("/orders/{order_id}", response_model=OrderWithDetails)
async def get_order_with_details(order_id: int):
    conn = await database.get_db_connection()
    try:
        async with conn.cursor() as cursor:
            # Fetch the purchase order data
            await cursor.execute(
                '''
                SELECT orderID, orderDate, orderStatus, statusDate, vendorID
                FROM purchaseOrders
                WHERE orderID = ?;
                ''',
                (order_id,),
            )
            order_row = await cursor.fetchone()
            if not order_row:
                raise HTTPException(status_code=404, detail="Purchase order not found")

            order = dict(zip([column[0] for column in cursor.description], order_row))

            # Fetch the details for the order
            await cursor.execute(
                '''
                SELECT orderDetailID, orderID, orderQuantity, expectedDate, actualDate, productID
                FROM purchaseOrderDetails
                WHERE orderID = ?;
                ''',
                (order_id,),
            )
            details_rows = await cursor.fetchall()
            details = [
                dict(zip([column[0] for column in cursor.description], row))
                for row in details_rows
            ]

            return {
                "order": order,
                "details": details,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

# Webhook to receive IMS notifications (example: when a new order is created in IMS)
@router.post("/webhook/new-order")
async def webhook_new_order(request: Request):
    try:
        payload = await request.json()

        # Log the incoming payload (you can modify this to just log or process without storing)
        print(f"Received webhook data: {payload}")

        # Optionally, you can log or perform actions based on this data
        # But since you're not inserting into your DB, we don't need to save it.
        
        # Just return a confirmation message.
        return {"message": "Webhook received and processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")
