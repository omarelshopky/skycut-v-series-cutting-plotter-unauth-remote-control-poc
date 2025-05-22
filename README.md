# Skycut V Series Cutting Plotter Unauthenticated Remote Control

Discovered by Omar Elshopky, Jan 2024.

## Description

Insufficient Authentication vulnerability in the Wi-Fi interface in Skycut V Series Cutting Plotter Firmware v22.0223 and Hardware v7.1202K allows remote attackers to execute arbitrary control commands leading to physical harm and denial of operations via GCODE instructions sent to an unprotected TCP port 8080.

https://github.com/user-attachments/assets/b7bc4240-25eb-4e71-b5f7-ef23006dc1be
> View on YouTube via https://youtu.be/ajSA0nFml2A

<br>


| Field | Content |
|-------|---------|
| **Vendor** | Skycut (https://skycutcutter.com/) |
| **Product** | Skycut V Series Cutting Plotter (Tested on V24_V48) |
| **Authentication Required** | None |
| **Privileges Required** | None |
| **User Interaction** | None |
| **Vector** | Wi-Fi within ~20 meters and can be extended using decent Wi-Fi adapter like Alfa! |


## Full Technical Write-up

- [Wireless Weapons: Turning Skycut Plotters into Physical Dangers](https://medium.com/@omarelshopky/wireless-weapons-turning-skycut-plotters-into-physical-dangers-9f29e0cd357a)


## Summary

Skycut cutter plotter machines (e.g., model V24) contain multiple security vulnerabilities in their network implementation:

- The devices expose a built-in Wi-Fi access point with:
  - Predictable SSID naming convention (starts with CUTTER)
  - Hardcoded default password (12345678)
  - No functionality to modify credentials or disable the wireless access point

- The control interface:
  - Listens on TCP port 8080 without requiring authentication
  - Accepts direct GCODE-like instructions without verification
  - Lacks transport encryption for command transmission

By capturing and analyzing network traffic between the official control software (or previously available mobile app) and the device, attackers can determine the command protocol structure and directly issue control instructions to the machine without user authorization.


## Impact

An attacker within Wi-Fi range (approximately 20 meters) can:

- Connect to the machine's wireless network using the default credentials
- Send unauthorized control commands directly to the device via TCP port 8080
- Take complete operational control of the cutting mechanism
- Create safety hazards by activating cutting operations while operators are handling materials
- Disrupt manufacturing processes by sending malformed commands
- Damage equipment or materials through deliberate manipulation of cutting parameters

The vulnerability allows for complete remote control of the physical device without any user interaction or notification, presenting both safety and operational risks.


## Requirements

- Python 3
- Attacker must be in Wi-Fi range (~20m) of the machine


## Usage

```bash
python exploit.py
```

The script will:
1. Scan for open "CUTTER" Wi-Fi networks
2. Connect automatically using the default password
3. Detect active devices on the network
4. Allow selection of a target
5. Send control commands or files to the machine


## Mitigation

No official security fix is currently available from the manufacturer for these vulnerabilities.

**Workaround:**

During research, a method was discovered to disable the Wi-Fi access point:

1. In the machine's network configuration menu, attempt to connect to any Wi-Fi network
2. Enter arbitrary password credentials
3. Allow the connection attempt to fail
4. The device will disable its access point functionality, and this state persists even through power cycles

For detailed step-by-step instructions on implementing this workaround, refer to the complete vulnerability write-up.

**Protective Measures:**

Users should also implement these additional security precautions:

- Operate these devices only in controlled, non-public environments
- Power off the machine completely when not actively in use
- Request security patches from the manufacturer to address these design flaws


## Disclosure Timeline

- 2024-01-15: Initial vulnerability discovery and technical confirmation completed
- 2024-01-17: Formal notification sent to vendor through official communication channels
- 2025-04-21: Notified vendor that disclosure period had significantly exceeded standard 90-day responsible disclosure timeframe (by 12 additional months) and announced intention to publish vulnerability details absent response
- 2025-05-22: Public disclosure of exploit, technical walkthrough, and complete vulnerability details

## References
- https://medium.com/@omarelshopky/wireless-weapons-turning-skycut-plotters-into-physical-dangers-9f29e0cd357a
- https://youtu.be/ajSA0nFml2A

## Disclaimer

This vulnerability disclosure is provided for informational and educational purposes only. The information contained in this document is intended to help users protect their Skycut cutting plotter devices from potential security threats.

The author does not encourage or condone any malicious use of the information presented herein. Users should only apply this knowledge to secure their own equipment or systems they have explicit permission to test.

The author is not responsible for any damages or misuse resulting from the application of this information. All testing and mitigation should be performed with caution and appropriate authorization.
