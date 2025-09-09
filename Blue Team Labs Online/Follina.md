## Scenario:
On a Friday evening when you were in a mood to celebrate your weekend, your team was alerted to a new RCE vulnerability actively being exploited in the wild. You have been tasked with analyzing and researching the sample to collect information for the weekend team.

A zip file is included; download it on your VM.
## This file contains real malware, so it's highly recommended that you open it in a virtual machine.
**Our goal is to analyze the file and answer some questions.**

## Question 1) What is the SHA1 hash value of the sample?
First, unzip the file and we'll get a folder with a file named sample.doc inside.\
We need to calculate the hash of this file, and there are several methods for doing so.\
● Terminal way:
```bash
sha1sum sample.doc
```
● Virustotal:\
Upload the file to VirusTotal, and on the details page, you'll see the SHA1 hash of this file.

## Question 2) According to VirusTotal, what is the full file type of the provided sample?
After uploading the file to Virustotal, go to the details tab, and you'll find a file type value there. Just copy and paste it into the answer.

## Question 3) Extract the URL that is used within the sample and submit it.
For this question, we have to unzip the doc file. Unzipping it gives plenty of files.\
If you open word/_rels/document.xml.rels this file via cat, you'll see plenty of URLs there, but you'll find one starting with 'Target='. Paste that URL in the answer.\
You can also find that on Virustotal.

## Question 4) What is the name of the XML file that is storing the extracted URL?
The file that stores the extracted URL is this document.xml.rels file.

## Question 5) The extracted URL accesses an HTML file that triggers the vulnerability to execute a malicious payload. According to the HTML processing functions, any files with fewer than <Number> bytes would not invoke the payload. Submit the <Number>
Here, we have to do a bit of googling, and if you don't ask the right question, you'll have a hard time finding the answer.\
Use this question: What is the minimum byte size required for a file to invoke the payload in HTML processing functions?\
I hope you'll get the answer.\
You can also find the answer from the link below.

## Question 6) After execution, the sample will try to kill a process if it is already running. What is the name of this process?
This question is tricky because we won't know what the malware does until we run it. Since this is real malware, running it on your host machine is very risky—definitely use a VM if you want to analyze it. We won't run this malware; instead, we have online documentation about this malware written by John Hammond... If you read through the documentation, you'll find the answer.
Link: https://www.huntress.com/blog/microsoft-office-remote-code-execution-follina-msdt-bug?source=post_page-----13efe22e80e4---------------------------------------

## Question 7) You were asked to write a process-based detection rule using Windows Event ID 4688. What would be the ProcessName and ParentProcessname used in this detection rule?
The answer can also be found in the previous link. Read through the article and try to understand what's going on.

## Question 8) Submit the MITRE technique ID used by the sample for Execution.
This answer can also be found on VirusTotal. Go to the Behavior tab and navigate to MITRE ATT&CK Tactics and Techniques, then Inter-Process Communication, and you can find the associated TTPs.

## Question 9) Submit the CVE associated with the vulnerability that is being exploited.
Again, check VirusTotal for this information.
