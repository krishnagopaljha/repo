# Port Reset Tool

A Python utility to identify and terminate processes using specific ports. This tool supports resetting single ports, multiple ports, and ranges of ports across Windows and Unix-based systems.

## Features
- **Single Port**: Reset a single port.
- **Multiple Ports**: Reset multiple ports using comma-separated input.
- **Port Range**: Reset a range of ports (e.g., `8000-8010`).
- **Mixed Input**: Supports combinations of ports and ranges (e.g., `8000,8005-8010,9000`).

## Prerequisites
- Python 3.x
- Administrator privileges (to terminate processes)

## How to Use
1. Clone or download the repository.
2. Run the script:
   ```bash
   python portfixer.py
