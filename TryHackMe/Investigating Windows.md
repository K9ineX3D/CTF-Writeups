## Investigating Windows
A windows machine has been hacked, its your job to go investigate this windows machine and find clues to what the hacker might have done.\
**Start the machine, it'll open in split view or you can login via rdp also.**

### ● Whats the version and year of the windows machine?

For the answer, open the settings of the machine, go to System, then navigate to the About section, and you'll find the answer there.

**Ans: Windows server 2016**

### ● Which user logged in last?

I used PowerShell to find this with the command:
```bash
Get-LocalUser | Select-Object Name,LastLogon | Sort-Object LastLogon -Descending
```
Line breakdown:\
● Get-LocalUser = Gets all local user accounts.\
● Select-Object Name,LastLogon = Shows only username and last login time.\
● Sort-Object LastLogon -Descending = Sorts by most recent login first.\
There are several methods for finding this but this method is usually the most reliable and gives you clean, sorted results.

**Ans: Administrator**

### ● When did John log onto the system last?

From the previous command output, you'll get this answer too —look at user John.

**Ans: 03/02/2019 5:48:32 PM**

### ● What IP does the system connect to when it first starts?

For finding this we have to look in the registry, open regedit and go to this location:
```bash
HKEY_LOCAL_MACHINE > SOFTWARE > Microsoft > Windows > CurrentVersion > Run
```
Once you reach that location look at UpdateSvc field and you'll get the ip it connects.\
**To find the IP the system connects to at startup, we check the Windows Registry Run key where startup programs are configured. The UpdateSvc entry contains the hardcoded IP address that the system is programmed to connect to during boot**

**Ans: 10.34.2.3**

### ● What two accounts had administrative privileges (other than the Administrator user)?

**Solution Approach:**\
To identify users with administrative privileges, we need to check which accounts belong to the local Administrators group. In Windows, administrative privileges are granted through group membership rather than individual user settings.\
In CMD:
```bash:
net localgroup administrators
```
● net localgroup = Shows members of local groups\
● administrators = The built-in group that grants admin privileges\
● Lists all accounts with administrative access

**Ans: Guest, Jenny**

### ● Whats the name of the scheduled task that is malicous?

**Solution Approach:**\
Windows scheduled tasks can be used by attackers for persistence and privilege escalation. We need to enumerate all scheduled tasks and identify suspicious ones based on their properties, locations, or behaviors.\
In powershell:
```bash
Get-ScheduledTask | Where-Object {$_.TaskPath -eq "\"}
```
**Command breakdown:**\
● Get-ScheduledTask = Gets all scheduled tasks\
● Where-Object {$_.TaskPath -eq "\"} = Filters tasks located directly in root directory\
● $_.TaskPath -eq "\" = Shows only tasks in the root path (not in subdirectories)

**The Logic Behind This Approach:**\
Legitimate Windows tasks are organized in subdirectories like:\
● \Microsoft\Windows\UpdateOrchestrator\ \
● \Microsoft\Windows\WindowsUpdate\ \
● \Microsoft\Office\

Malicious tasks are often placed in the root directory (\) because:
1. Easier to create - no need to navigate subdirectories
2. Less obvious - hidden among system tasks
3. Quick access - attackers prefer simple paths
4. Persistence - root level tasks are less likely to be accidentally deleted

**Ans: Clean file system**

### ● What file was the task trying to run daily?

**Solution Approach:**\
Now that we've identified the malicious scheduled task using the root directory filter, we need to examine its Actions property to see what file it executes.\
In CMD:
```bash
schtasks /query /tn "[TASK_NAME]" /fo LIST /v
```
● schtasks = Scheduled task utility\
● /query = Show information (don't modify)\
● /tn "[TASK_NAME]" = Target specific task name\
● /fo LIST = Format as detailed list\
● /v = Verbose (show all details)

**Ans: nc.ps1**

### ● What port did this file listen locally for?

This answer can be found with the previous answer. Look again at the details of the tasks.

**Ans: 1348**

### ● When did Jenny last logon?

To find this we can use 2nd and 3rd question approach.\
In Powershell:
```bash
Get-LocalUser | Select-Object Name,LastLogon | Sort-Object LastLogon -Descending
```
You'll find Jenny's login field is empty, which means the user never logged in.

**Ans: never**

### ● At what date did the compromise take place?

**Solution Approach:**\
To determine when the system was compromised, we need to look at timestamps of malicious artifacts we've already identified. The compromise date is typically when the malicious components were first created or executed.\
If you go to C: folder and look at the suspicious folder, you'll get the creation date. That's the compromise date.

**Ans: 03/02/2019**

### ● During the compromise, at what time did Windows first assign special privileges to a new logon?

**Solution Approach:\
We need to check Event Logs for Event ID 4672 which records when special privileges are assigned to a new logon. This happens when someone logs in with elevated/administrative rights.**

Using Event Viewer GUI Method:\
● Step 1: Open Event Viewer

Click Start Menu → Event Viewer

● Step 2: Create Custom View

Click "Create Custom View" on the right panel

● Step 3: Set Date/Time Range

Click "Logged:" dropdown → Select "Custom Range..."\
From: Click "First Event" → Select "Events On" → Set date: 03/02/2019 at 4:00:00 PM\
To: Same process → Set: 03/02/2019 at 4:30:00 PM\
Click OK

● Step 4: Select Security Log

Click "Event Logs:" dropdown\
Expand "Windows Logs" (click the + icon)\
Check "Security"\
Click OK

● Step 5: Save Filter

Name the filter (or just click OK with default name)

● Step 6: Find the Event

Double click on the date and time column as it will organize from starting time.\
Slowly scroll down\
Look at "Task Category" column\
Find "Security Group Management"\
**● Security Group Management events indicate privilege changes**\
Note the Date and Time for that first occurrence

**Ans: 03/02/2019 4:04:47 PM**

### ● What tool was used to get Windows passwords?

**Solution Approach:\
We need to look for credential dumping tools that attackers commonly use to extract Windows passwords. These are typically found in the same locations as other malicious files.**\
You'll notice a command prompt keeps poping up with C:\TMP\mim.exe, so we can check that folder for finding the tool used.\
Go to C:\TMP and you'll find a text file named mim-out, opening it gives the tool name.

**Ans: mimikatz**

### ● What was the attackers external control and command servers IP?

**Solution Approach:\
We need to find the external IP address that the compromised system was communicating with. This is the attacker's C2 (Command and Control) server.**

**Step 1: Navigate to Hosts File**\
● Go to: C:\Windows\System32\drivers\etc \
● Double-click the hosts file\
● Select Notepad to open it

**Step 2: Analyze Hosts File Entries**\
Inside the hosts file, you'll see entries for google.com and www.google.com with an IP address.

**Why this is suspicious:**\
● Hosts file = Local DNS override (redirects domain names to specific IPs)\
● google.com shouldn't need manual entry (DNS resolves it automatically)\
● Threat actors use hosts file to redirect legitimate domains to their C2 servers

**Step 3: Verify if IP is Legitimate**\
● On your host machine (not the compromised one), open Command Prompt:
```bash
ping google.com
```
● Compare the IP address returned with the IP in the compromised system's hosts file.\
● If they don't match = The hosts file entry is malicious and points to the attacker's C2 server.

**Ans: 76.32.97.132**

### ● What was the extension name of the shell uploaded via the servers website?

**Solution Approach:\
We need to find a web shell that was uploaded through the website. Web shells are malicious scripts uploaded to web servers for remote command execution.**\
● Check Web Server Directory:
```bash
dir C:\inetpub\wwwroot /s
```
**Why this location:**\
● C:\inetpub\wwwroot = Default IIS (Internet Information Services) web root\
● Where website files are stored\
● Attackers upload shells here for web access

The output will show some files uploaded by the attacker and the file named test is the actual shell and the answer.

**Ans: .jsp**

### ● What was the last port the attacker opened?

**Solution Approach:\
We need to find firewall rules or port configurations that the attacker modified to open ports for access. The "last" port indicates the most recent firewall modification.**

● Step 1: Open Windows Firewall

Click Start icon\
Type: firewall\
Press Enter or click Windows Defender Firewall with Advanced Security

● Step 2: Navigate to Inbound Rules

In the left panel, click Inbound Rules\
This shows all inbound firewall rules (many entries)

● Step 3: Filter Rules

On the right panel, click Filter by Group\
Scroll to bottom of dropdown\
Select Rules without a Group

Result: Only two entries remain

● Step 4: Identify Suspicious Rule

Look for the suspicious entry: "Allow outside connections for development"

**Why this is suspicious:**

Generic, legitimate-sounding name (social engineering)\
Not part of any official Windows group\
Likely created by attacker for backdoor access

● Step 5: View Port Details

Double-click "Allow outside connections for development"\
Click the Protocols and Ports tab\
Check the Local port field\
That port number = your answer

**Ans: 1337**

### ● Check for DNS poisoning, what site was targeted?

**Solution Method: Check the Hosts File (Again)**\
We already found this earlier when looking for the C2 server IP! The hosts file contained entries for google.com and www.google.com redirecting to the attacker's IP.\
The domain name (like google.com or www.google.com) listed in the poisoned hosts file entry is the targeted site. This is the same hosts file we examined earlier when finding the C2 server IP!

**Ans: google.com**
