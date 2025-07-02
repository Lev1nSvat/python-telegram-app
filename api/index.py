import asyncio
import json
import os

from pyrogram import Client
from pyrogram.errors import FloodWait, UserNotMutualContact, PeerIdInvalid, UserIsBot, RPCError

from http.server import BaseHTTPRequestHandler, HTTPServer


API_ID = 27247073
API_HASH = "7513d681fa4f62c7ee0bb9fefe19377c"
PHONE_NUMBER = "+79063667570"
SESSION_NAME = "tdlib_group_creator_session"

client = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE_NUMBER,
    session_string="AgGfweEAVc-zM-n0R7W5ty5QnaN4WokuGx3Nig8UanjVq57Bj1HieQbHJK99m-B5KSqcEOf6Qv0ty27dlSmB87b_t99TktR6ct-O3zCEduMDpAuzLcWyiUpO4TrWaiSdAAe5-Oz29LXbIGKX5I-q9YBhNPL9jwjWeIntaFF0YsqukGHYkTorZiX0farSCTa0fypMNeEF8IcbiWJEDDwyI6tpDluryaoKOLqWPqX8mf5z9wgQ4yEp9AjQPJBBbQsKwIm3-xkO6L5VCglsTUT8RH9uiMEDF_9nDnTyKcWYorm4Is3GSWdH83qg0doGmql7vPSZmKiA2d-h2uCZHvh-gGULLv1wRQAAAAB28DzqAA",
    in_memory=True # Set to True if you don't want to save sessions to disk
)

async def create_group_from_json_request(json_data_str: str):
    """
    Receives a JSON string, parses it, and attempts to create a Telegram group chat.
    Args:
        json_data_str (str): A JSON string containing 'title' and either 'user_ids'
                             (list of integers) or 'phone_numbers' (list of strings).
                             Example with user_ids: '{"title": "My New Awesome Group", "user_ids": [123456789, 987654321]}'
                             Example with phone_numbers: '{"title": "My Phone Group", "phone_numbers": ["+12345678900", "+19876543210"]}'
                             Example with both: '{"title": "Mixed Group", "user_ids": [12345], "phone_numbers": ["+1234"]}'
    """
    print("--- Processing group creation request ---")

    try:
        # Parse the incoming JSON data
        request_data = json.loads(json_data_str)
        group_title = request_data.get("title")
        user_ids_to_add_string = request_data.get("user_ids", "")
        user_ids_to_add = [number.strip() for number in user_ids_to_add_string.split(',')]
        phone_numbers_to_add_string = request_data.get("phone_numbers", "")
        phone_numbers_to_add = [number.strip() for number in phone_numbers_to_add_string.split(',')]

        if not group_title:
            print("Error: Invalid JSON format. 'title' is required.")
            return {"status": "error", "message": "Invalid request payload: 'title' missing."}

        if not user_ids_to_add and not phone_numbers_to_add:
            print("Error: Invalid JSON format. Either 'user_ids' or 'phone_numbers' must be provided.")
            return {"status": "error", "message": "Invalid request payload: 'user_ids' or 'phone_numbers' missing."}

        if user_ids_to_add and not isinstance(user_ids_to_add, list):
            print("Error: 'user_ids' must be a list of integers.")
            return {"status": "error", "message": "Invalid 'user_ids' format."}

        if phone_numbers_to_add and not isinstance(phone_numbers_to_add, list):
            print("Error: 'phone_numbers' must be a list of strings.")
            return {"status": "error", "message": "Invalid 'phone_numbers' format."}

        print(f"Request received: Title='{group_title}', User IDs={user_ids_to_add}, Phone Numbers={phone_numbers_to_add}")

        # Start the Pyrogram client
        print("Starting Pyrogram client...")
        await client.start()
        print("Pyrogram client started.")

        # This list will now store the raw user IDs (int) and phone numbers (str)
        # instead of Pyrogram User objects, to avoid the "Error binding parameter 1: type 'User' is not supported"
        # The create_group method can handle these primitive types directly.
        users_to_add_to_group_call = []

        # Process user IDs
        if user_ids_to_add:
            print(f"Validating {len(user_ids_to_add)} user IDs...")
            for user_id in user_ids_to_add:
                try:
                    # Attempt to get user info, mainly for logging and bot check.
                    # The actual user_id (int) will be added to the list for create_group.
                    user = await client.get_users(user_id)
                    if user.is_bot:
                        print(f"Warning: User ID {user_id} is a bot and cannot be added to a basic group by this method.")
                        continue
                    users_to_add_to_group_call.append(user_id) # Add the ID directly
                    print(f"User by ID {user_id} found: {user.first_name}")
                except UserNotMutualContact:
                    print(f"Warning: User ID {user_id} is not a mutual contact. Will attempt to add by ID anyway.")
                    users_to_add_to_group_call.append(user_id) # Still try to add the ID
                except PeerIdInvalid:
                    print(f"Error: User ID {user_id} is invalid or does not exist.")
                except RPCError as e:
                    print(f"Error getting user {user_id}: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred while fetching user {user_id}: {e}")

        # Process phone numbers
        if phone_numbers_to_add:
            print(f"Validating {len(phone_numbers_to_add)} phone numbers...")
            for phone_number in phone_numbers_to_add:
                try:
                    # Attempt to get user info, mainly for logging and bot check.
                    # The actual phone_number (str) will be added to the list for create_group.
                    user = await client.get_users(phone_number)
                    if user.is_bot:
                        print(f"Warning: Phone number {phone_number} corresponds to a bot and cannot be added.")
                        continue
                    users_to_add_to_group_call.append(phone_number) # Add the phone number directly
                    print(f"User by phone {phone_number} found: {user.first_name} (ID: {user.id})")
                except UserNotMutualContact:
                    print(f"Warning: User with phone {phone_number} is not a mutual contact. Will attempt to add by phone anyway.")
                    users_to_add_to_group_call.append(phone_number) # Still try to add the phone number
                except PeerIdInvalid:
                    print(f"Error: Phone number {phone_number} is invalid or does not exist.")
                except RPCError as e:
                    print(f"Error getting user by phone {phone_number}: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred while fetching user by phone {phone_number}: {e}")

        if not users_to_add_to_group_call:
            print("Error: No valid users found from provided IDs or phone numbers to create the group with.")
            return {"status": "error", "message": "No valid users to add to the group."}

        # Create the group chat
        print(f"Attempting to create group '{group_title}' with {len(users_to_add_to_group_call)} participants...")
        try:
            # Pyrogram's create_group function can directly accept a list of user IDs (int) or phone numbers (str).
            # By passing only these primitive types, we avoid potential binding issues with complex User objects.
            new_group = await client.create_group(
                title=group_title,
                users=users_to_add_to_group_call # Pass the list of raw IDs/phone numbers
            )
            print(f"Group '{new_group.title}' (ID: {new_group.id}) created successfully!")
            return {
                "status": "success",
                "message": "Group created successfully!",
                "group_id": new_group.id,
                "group_title": new_group.title
            }
        except FloodWait as e:
            print(f"Flood wait error: You are making too many requests. Please wait {e.value} seconds.")
            return {"status": "error", "message": f"Too many requests. Please wait {e.value} seconds."}
        except UserIsBot:
            print("Error: Cannot add a bot to a basic group via this method.")
            return {"status": "error", "message": "Cannot add a bot to a basic group."}
        except Exception as e:
            print(f"Failed to create group: {e}")
            return {"status": "error", "message": f"Failed to create group: {e}"}

    except json.JSONDecodeError:
        print("Error: Invalid JSON data received.")
        return {"status": "error", "message": "Invalid JSON format."}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}
    finally:
        # Stop the Pyrogram client
        if client.is_connected:
            print("Stopping Pyrogram client...")
            await client.stop()
            print("Pyrogram client stopped.")


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        content_length = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_length)
        print("body of a request:")
        print(post_body)
        asyncio.run(create_group_from_json_request(post_body))


#async def main():
    # Call the function that processes the request

    #result = await create_group_from_json_request(sample_json_request)
    #print("\n--- Result ---")
    #print(json.dumps(result, indent=4))


#if __name__ == "__main__":
    # Ensure a proper event loop is running for async operations
 #   try:
  #      asyncio.run(main())
 #   except KeyboardInterrupt:
  #      print("Operation cancelled by user.")
 #   except Exception as e:
 #       print(f"An error occurred during main execution: {e}")
