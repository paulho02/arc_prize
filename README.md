
## Remote worker _macbook_

1. Mount Mac hard drive as a network drive in Windows Explorer: <br>
    Enter `\\<ipaddress>\` in the address bar and, when prompted, enter your username and password.
2. SSH access: <br>
   ```bash
   ssh <remote-username>@<ipaddress>
   ```
   Enter your password when prompted.

3. Navigate to the project folder and activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Start the program in the background:
   ```bash
   nohup python new_main.py > logs/output.log 2>&1 &  
   ```
5. Find the running process:
   ```bash 
   ps aux | grep new_main.py
   ```
6. Stop the process:
   ```bash
   kill <PID>
   ```