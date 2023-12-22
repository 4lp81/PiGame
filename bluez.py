from bluetooth import *
import requests

# Replace this URL with your backend endpoint
BACKEND_URL = "http://xxx.xx.xx.xx:8080/AustRiddle_Server-1.0-SNAPSHOT/api/game/"
GAMEID1 = "http://xxx.xx.xx.xx:8080/AustRiddle_Server-1.0-SNAPSHOT/api/game/6560a511414e841c83929239"
GAMEID2 = "http://xxx.xx.xx.xx:8080/AustRiddle_Server-1.0-SNAPSHOT/api/game/6560a511414e841c83929239"
GAMEINFO = "http://xxx.xx.xx.xx:8080/AustRiddle_Server-1.0-SNAPSHOT/api/game/availableGames"
POST_PLAYER = "http://xxx.xx.xx.xx:8080/AustRiddle_Server-1.0-SNAPSHOT/api/player/TestId"
PUZZLE = "http://xxx.xx.xx.xx:8080/AustRiddle_Server-1.0-SNAPSHOT/api/puzzle/6560a4e9414e841c83929236"
RANKING = "http://xxx.xx.xx.xx:8080/AustRiddle_Server-1.0-SNAPSHOT/api/ranking"


def sendRequestToBackend(url, client_socket):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad responses (4xx, 5xx)
        print("Backend request successful")

        if response.headers.get('content-type', '').startswith('image'):
            # If the response is an image, send it in chunks
            client_socket.send(b"IMAGE_START\n")  # Signal the start of the image

            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    client_socket.send(chunk)

            client_socket.send(b"\nIMAGE_END")  # Signal the end of the image
        else:
            # If the response is not an image, send the JSON response
            client_socket.send(response.text.encode('utf-8'))

    except requests.RequestException as e:
        print(f"Backend request failed: {e}")

def sendToBackend(json_data):
    try:
        # Senden der POST-Anfrage mit den empfangenen JSON-Daten
        response = requests.post(POST_PLAYER + "recordGamePlayed", json=json_data)

        # Überprüfen Sie die Antwort des Servers
        if response.status_code == 200:
            print("Erfolgreich gesendet!")
        elif response.status_code == 400:
            print(f"Fehlerhafte Anfrage: {response.text}")
        elif response.status_code == 500:
            print(f"Interner Serverfehler: {response.text}")
        else:
            print(f"Unerwartete Antwort: {response.status_code} - {response.text}")

    except requests.RequestException as e:
        print(f"Fehler bei der Anfrage: {e}")

server_sock = BluetoothSocket(RFCOMM)
server_sock.bind(("", 1))
server_sock.listen(1)


port = server_sock.getsockname()[1]

uuid = "00001101-0000-1000-8000-00805F9B34FB"  # SPP (Serial Port Profile) UUID

advertise_service(server_sock, "MyService", service_id=uuid, service_classes=[uuid, SERIAL_PORT_CLASS], profiles=[SERIAL_PORT_PROFILE])

print(f"Waiting for connection on RFCOMM channel {port}")

try:
    client_sock, client_info = server_sock.accept()
    print(f"Accepted connection from {client_info}")

    while True:
        data = client_sock.recv(1024)
        if not data:
            break  # Break the loop if no data is received
        print(f"Received data from the phone: {data}")

        # Process the received data
        if data.startswith(b"getGameInfo"):
            # Trigger the backend request with GAMEINFO URL
            sendRequestToBackend(GAMEINFO, client_sock)
        elif  data.startswith(b"gameId"):
            # Trigger the backend request with GAMEID1 URL
            sendRequestToBackend(GAMEID1, client_sock)   
        elif data.startswith(b"getPuzzle"):
            # Trigger the backend request with GAMEID1 URL
            sendRequestToBackend(PUZZLE, client_sock)        
        elif data.strip() == "Post":  
            # Check if the stripped data is not empty
            # Assume the received data is JSON and send it to the backend
            try:
                received_json_data = json.loads(data)
                sendJsonToBackend(received_json_data)
            except json.JSONDecodeError as e:
                print(f"Fehler beim Dekodieren der empfangenen JSON-Daten: {e}")
        

except BluetoothError as e:
    print(f"Error: {e}")

finally:
    client_sock.close()
    server_sock.close()
