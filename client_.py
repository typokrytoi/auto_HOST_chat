import socket
import threading
import sys
import os
import time
import json

PORT = 9090
running = True
nickname = ""
client = None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_input():
    try:
        return sys.stdin.readline().strip()
    except:
        return ""

def print_prompt():
    sys.stdout.write(f"{nickname}> ")
    sys.stdout.flush()

def discover_server():
    try:
        test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test.settimeout(0.5)
        test.connect(('127.0.0.1', PORT))
        test.close()
        return '127.0.0.1'
    except:
        pass
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        base_ip = '.'.join(local_ip.split('.')[:-1])
        print("🔍 Сканирование сети...")
        
        for i in range(1, 255):
            try:
                test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test.settimeout(0.05)
                test.connect((f"{base_ip}.{i}", PORT))
                test.close()
                return f"{base_ip}.{i}"
            except:
                continue
    except:
        pass
    
    return None

def receive_messages():
    global running, nickname
    while running:
        try:
            data = client.recv(4096).decode('utf-8')
            if data:
                try:
                    message_data = json.loads(data)
                    msg_type = message_data.get('type', 'message')
                    msg_text = message_data.get('message', '')
                    msg_nick = message_data.get('nickname', '')
                    
                    sys.stdout.write("\r" + " " * 80 + "\r")
                    sys.stdout.flush()
                    
                    if msg_type == 'system':
                        print(f"🔔 {msg_text}")
                    else:
                        print(f"{msg_nick}: {msg_text}")
                    
                    print_prompt()
                    sys.stdout.flush()
                except:
                    sys.stdout.write("\r" + " " * 80 + "\r")
                    sys.stdout.flush()
                    print(f">>> {data}")
                    print_prompt()
                    sys.stdout.flush()
        except:
            running = False
            break

def send_messages():
    global running, nickname
    while running:
        try:
            message = get_terminal_input()
            if message:
                if message == '/exit':
                    running = False
                    break
                elif message == '/clear':
                    clear_screen()
                    print(f"Добро пожаловать, {nickname}!")
                    print("-" * 30)
                    print_prompt()
                else:
                    try:
                        client.send(json.dumps({
                            'type': 'message',
                            'message': message,
                            'nickname': nickname
                        }).encode('utf-8'))
                        print_prompt()
                    except:
                        client.send(message.encode('utf-8'))
                        print_prompt()
        except:
            running = False
            break

def main():
    global client, running, nickname
    
    clear_screen()
    print("═" * 50)
    print("             ЧАТ КЛИЕНТ")
    print("═" * 50)
    
    print("🔍 Поиск сервера...")
    server_ip = discover_server()
    
    if not server_ip:
        print("❌ Сервер не найден!")
        print("\nПроверь:")
        print("1. Сервер запущен")
        print("2. Телефон и компьютер в одной сети")
        print("3. Брандмауэр не блокирует")
        input("\nНажми Enter для выхода...")
        return
    
    print(f"✅ Сервер найден: {server_ip}")
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((server_ip, PORT))
        print("🔄 Подключение...")
        
        response = client.recv(1024).decode('utf-8')
        if response == "NICK":
            nickname = input("Твой ник: ").strip()
            if not nickname:
                nickname = f"User_{hash(client) % 1000:03d}"
            
            client.send(json.dumps({
                'nickname': nickname
            }).encode('utf-8'))
            
            clear_screen()
            print(f"✅ Добро пожаловать, {nickname}!")
            print("-" * 30)
            
            threading.Thread(target=receive_messages, daemon=True).start()
            
            print_prompt()
            send_messages()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        input("\nНажми Enter для выхода...")
    finally:
        if client:
            client.close()
        os._exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Выход...")
        os._exit(0)
