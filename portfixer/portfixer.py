import os
import socket
import subprocess
import re

def display_logo():
    logo = r"""
 _____           _   ______ _               
|  __ \         | | |  ____(_)              
| |__) |__  _ __| |_| |__   ___  _____ _ __ 
|  ___/ _ \| '__| __|  __| | \ \/ / _ \ '__|
| |  | (_) | |  | |_| |    | |>  <  __/ |   
|_|   \___/|_|   \__|_|    |_/_/\_\___|_|   

|--------------------------------------------------------------------|
| Created By: Krishna Gopal Jha                                      |
| Checkout my LinkedIn: https://www.linkedin.com/in/krishnagopaljha/ |
| Lookup at my insta: https://instagram.com/theindianpsych           |
|--------------------------------------------------------------------|
"""
    print(logo)

def parse_ports(input_ports):
    ports = set()
    parts = input_ports.split(",")
    for part in parts:
        part = part.strip()
        if "-" in part:  # Range of ports
            start, end = map(int, part.split("-"))
            ports.update(range(start, end + 1))
        elif part.isdigit():  # Single port
            ports.add(int(part))
    return sorted(ports)

def terminate_process(port):
    try:
        # Check if the port is in use
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                print(f"Port {port} is not in use.")
                return False
        
        print(f"Port {port} is in use. Attempting to reset...")

        # Find process using the port
        command = f"lsof -i :{port}" if os.name != "nt" else f"netstat -ano | findstr :{port}"
        process = subprocess.run(command, shell=True, text=True, capture_output=True)

        if process.returncode != 0 or not process.stdout:
            print(f"Unable to identify the process on port {port}. Check permissions.")
            return False

        if os.name != "nt":  # Unix-based systems
            lines = process.stdout.strip().split("\n")
            for line in lines[1:]:  # Skip the header
                pid = line.split()[1]  # The second column is PID
                print(f"Terminating process with PID {pid} using port {port}...")
                os.kill(int(pid), 9)
        else:  # Windows systems
            lines = process.stdout.strip().split("\n")
            for line in lines:
                parts = line.split()
                pid = parts[-1]  # The last column is PID
                print(f"Terminating process with PID {pid} using port {port}...")
                subprocess.run(f"taskkill /F /PID {pid}", shell=True)

        print(f"Port {port} has been reset successfully.")
        return True
    except Exception as e:
        print(f"An error occurred while resetting port {port}: {e}")
        return False

def reset_ports(input_ports):
    ports = parse_ports(input_ports)
    print(f"Parsed ports: {ports}")
    for port in ports:
        terminate_process(port)

if __name__ == "__main__":
    display_logo()
    print("Select Input Option:")
    print("1. Single Port")
    print("2. Multiple Ports (comma-separated)")
    print("3. Range of Ports (e.g., 8000-8010)")
    print("4. Mixed Input (e.g., 8000,8005-8010,9000-9010)")

    input_option = input("\nEnter your choice: ").strip()
    input_ports = input("Enter the port(s): ").strip()
    reset_ports(input_ports)
