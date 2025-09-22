## Overview:
**Sakura Room**
Use a variety of OSINT techniques to solve this room created by the OSINT Dojo.

## TIP-OFF:
***● What username does the attacker go by?***

Open the image on your browser and just view the source of image by right clicking and you'll find the username.

**Ans: SakuraSnowAngelAiko**

## RECONAISSANCE:
***● What is the full email address used by the attacker?***

Now we have find attacker email address by using the username we found earlier. Now our tool will be google dorking.
```bash
intitle:SakuraSnowAngelAiko
```
You'll find a github repository by this username and go to the repo and you'll find a repo named GPG. That's our key for finding email.\
Methodology is copy the content of the file and save it on your linux machine with .asc extension. Now run this:
```bash
gpg --import filename
```
You'll get the email address.

**Ans:SakuraSnowAngel83@protonmail.com**

***● What is the attacker's full real name?***

Now we have to find real name. Use google dorking again and you will find a linkedin profile. Visit the profile and you will find the real name.

**Ans: Aiko Abe**

## UNVEIL:
***● What cryptocurrency does the attacker own a cryptocurrency wallet for?***

Dorking gave us a github repo link named ETH, open it and open the script.\
Now tap on history, you will find 2 commits, 1 creating and 1 updating.\
Open creation commit and you will find something like this:
```bash
stratum://0xa102397dbeeBeFD8cD2F73A89122fCdB53abB6ef.Aiko:pswd@eu1.ethermine.org:4444
```
Syntax: stratum://ethwallet.workerid:password@miningpool:port\
Follow the syntax and copy the ethwallet address and go to this link [Etherscan](https://etherscan.io/) and search the address, you'll find many transactions of ETH and ETH stands for Ethereum.

**Ans: Ethereum**

***● What is the attacker's cryptocurrency wallet address?***

We already found wallet address from the github commit.

**Ans: 0xa102397dbeeBeFD8cD2F73A89122fCdB53abB6ef**

***● What mining pool did the attacker receive payments from on January 23, 2021 UTC?***

So now we have to filter out the transcations, open filter and apply incoming then you'll see plenty of transaction happening coming from Ethermine and if we calculate age it's meeting the question date range.

**Ans: Ethermine**

***● What other cryptocurrency did the attacker exchange with using their cryptocurrency wallet?***

Now analyze the transactions you will find some outgoing transactions with a different wallet name.

**Ans: Tether**

## TAUNT
***● What is the attacker's current Twitter handle?***

Search google with the username we found earlier and you'll get a twitter account.

**Ans: SakuraLoverAiko**

***● What is the BSSID for the attacker's Home WiFi?***

While scanning the tweets a pattern stands out: the account references Deep Paste in bold and posted screenshots of MD5 hash with each message. DeepPaste is a dark-web text-paste service where posts are effectively permanent and uncensored. The MD5 hashes appear to be direct lookups — likely the keys needed to fetch the posted content.\
Accessing dark-web sites generally requires the Tor network and a specialized search tool to find .onion addresses; regular search engines like Google can’t reach those links. I couldn’t find a working .onion address for DeepPaste, so I’ll extract the content from the hint image instead. If you have lawful access to DeepPaste, use the MD5 hash from the tweets (use the later hash — the author said the first was removed) to retrieve the paste.\
So I took the SSID name from a writeup who had extracted the info from pastebin service, writeup link [here](https://github.com/a3r0id/TryHackMe-Sakura-Room-Writeup).\
Now it's time to find BSSID and for this [Wigle.net](https://wigle.net/index) will help us. Go near JAPAN and paste the SSID and search, you'll see a tiny dot, zoom it and you'll get the BSSID.

**Ans: 84:af:ec:34:fc:f8**

## HOMEBOUND
***● What airport is closest to the location the attacker shared a photo from prior to getting on their flight?***

Check out the post and do some osint to find the place. In the image you'll see aeroplane railways washington tower and try to geolocate the image. In the image you'll see aeroplane railways washington tower and try to geolocate the image.\
Which I did and found the place is: Long Bridge Park in Arlington, Virginia, United States.\
Now just look around the bridge on google maps and you'll an airport very close to that location, the airport code is our answer. For the code you can visit this [link](https://airportcodes.aero/name/R) and find it. 

**Ans: DCA**

***● What airport did the attacker have their last layover in?***

Again go to attacker twitter handle and browse, you'll see a photo of My final layover, time to relax! Now if you zoom into the photo you'll find the airline name.\
I put the image in google lens and got some results, now I analyzed the results and extracted the airport name, it took me a lot of time and was a lengthy process that's why I skipped detailed explaining here.\
Airport name is Haneda Airport, now get the airport code
**Ans: HND**

***● What lake can be seen in the map shared by the attacker as they were on their final flight home?***

It was pretty easy to find, question is about the picture shared by attacker(Sooo close to home! Can't wait to finally be back! :) This is a pretty large lake, so we can probably use Google Maps to go to the general location and find the name.

**Ans: Lake Inawashiro**

***● What city does the attacker likely consider "home"?***

In the taunt task we extracted attacker wifi BSSID, now as that wifi was listed as home network we assume that it's the place which attacker consider home.

**Ans: Hirosaki**
