import asyncio

async def my_async_function():
    """
    An example asynchronous function.
    In a real application, this might perform I/O, database queries,
    or other long-running operations.
    """
    await asyncio.sleep(0.1)  # Simulate some asynchronous work
    return "This is the result of the async function."

async def handler(request):
    """
    Vercel serverless function entry point.
    """
    if request.method == 'POST':
        try:
            # Run the asynchronous function
            result = await my_async_function()

            # Create a Vercel response object
            response_body = "Async function executed successfully."
            response_headers = {
                "Content-Type": "text/plain",
                "X-Async-Result": result  # Return the result in a custom header
            }
            return response_body, 200, response_headers
        except Exception as e:
            return f"Error: {str(e)}", 500, {"Content-Type": "text/plain"}
    else:
        return "Method Not Allowed", 405, {"Content-Type": "text/plain"}
