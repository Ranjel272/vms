from fastapi import APIRouter, HTTPException, Request
import database
import logging

# Initialize Logger
logger = logging.getLogger(__name__)

# Initialize Router
router = APIRouter()

# Webhook to receive IMS order data using GET method
@router.get("/webhook/new-order")
async def webhook_new_order(request: Request):
    try:
        # Extract data from query parameters sent by IMS
        productID = request.query_params.get('productID')
        productName = request.query_params.get('productName')
        productDescription = request.query_params.get('productDescription')
        size = request.query_params.get('size')
        color = request.query_params.get('color')
        category = request.query_params.get('category')
        quantity = request.query_params.get('quantity')
        vendorID = request.query_params.get('vendorID')
        orderDate = request.query_params.get('orderDate')
        expectedDate = request.query_params.get('expectedDate')

        # Log received parameters for debugging
        logger.info(f"Received parameters: {request.query_params}")

        # Validate the required data
        if not productID or not productName or not productDescription or not size or not color:
            raise HTTPException(status_code=400, detail="Missing required query parameters")

        # Insert data into the purchaseOrders table in VMS
        conn = await database.get_db_connection()
        cursor = await conn.cursor()

        # Insert the new order into the database
        await cursor.execute(
            '''
            INSERT INTO purchaseOrders (orderDate, orderStatus, vendorID)
            VALUES (?, ?, ?);
            ''',
            (orderDate, "Pending", vendorID)
        )
        orderID = cursor.lastrowid  # Get the last inserted orderID
        
        # Insert order details into purchaseOrderDetails table
        await cursor.execute(
            '''
            INSERT INTO purchaseOrderDetails (orderID, productID, orderQuantity, expectedDate)
            VALUES (?, ?, ?, ?);
            ''',
            (orderID, productID, quantity, expectedDate)
        )

        # Commit the transaction and close the connection
        await conn.commit()
        await conn.close()

        return {"message": "Purchase order received and processed successfully", "orderID": orderID}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")
