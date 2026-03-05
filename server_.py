import socket
import threading
import json

HOST = '0.0.0.0'
PORT = 9090

clients = {}
nicknames = {}

def broadcast(message, sender=None):
    for client_socket in clients:
        if client_socket != sender:
            try:
                client_socket.send(json.dumps(message).encode('utf-8'))
            except:
                del clients[client_socket]
                del nicknames[client_socket]

def handle_client(client_socket, address):
    try:
        client_socket.send("NICK".encode('utf-8'))
        data = client_socket.recv(1024).decode('utf-8')
        nickname_data = json.loads(data)
        nickname = nickname_data['nickname']
        
        clients[client_socket] = address
        nicknames[client_socket] = nickname
        
        broadcast({
            'type': 'system',
            'message': f"{nickname} присоединился к чату"
        })
        
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
                
            message_data = json.loads(data.decode('utf-8'))
            broadcast({
                'type': 'message',
                'message': message_data['message'],
                'nickname': nickname
            }, client_socket)
                
    except:
        pass
    finally:
        if client_socket in clients:
            nickname = nicknames[client_socket]
            del clients[client_socket]
            del nicknames[client_socket]
            broadcast({
                'type': 'system',
                'message': f"{nickname} покинул чат"
            })
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"Сервер запущен")
    print(f"IP для подключения: {local_ip}")
    print("Ожидание клиентов...")
    
    while True:
        client_socket, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, address))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_server()
