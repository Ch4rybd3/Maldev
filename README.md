# Maldev
A repo where I put all my work regarding malwares, from the developpement of custom made malwares to malware reverse and analysis

# Scylla
Scylla is my greatest creation, a C2 that started as a simple beacon to receive encrypted keys and stolen data from my other malwares, but who aim to become something great which will have an admin pannel, database, being a 2way C2 by sending commands, ...

# Kelpie
Kelpie is my own version of msfvenom.
It is the answer to multiple issues I encountered while developping my malwares which are : 
- reusability, some malwares shared features and I didn't wanted to reinvent the wheel everytime I started a new project
- Get the ability to configure my malwares and get a working executable on the go without having to hardcode everything
- Being able to obfuscate/metamorphic/add entropy as easily between my malwares so I can just create engines that will do the work and apply them to every malwares I want
- Get a bit of automation on the background, facilitating the communication and triage when using Scylla (or any other C2)
- Being able to mix multiple payload to achieves multiple capabilities (ransomware + log cleaner + inforstealer for example), but the more payloads you add, the less stealthier you are and some sand grain can block the machine

# Coral
Coral is a tool that will generate fake data and fake environnement/files to allow the use of my malwares inside a corporate environnement without breaking everything, specially conceived regarding my deployment of CTFs.
It is a good way to test your information system defending capabilities to ransomwares, wiper and other type of malwares without risking to set one loose free in the information system because the scope was badly designed.

# Payloads
## WannaSwim (will be renamed Kraken when I'll have the time)
WannaSwim is a ransomware payload written in Python, it's based on, you guessed it, Wannacry.
It has a killswitch, which on the contrary of wannacry, is really cool as it does a double check based on google.com and a random URL that it generates every time it is launched

## Manta
Manta is an infostealer that targets hardware informations, OS informations etc.
It is not used to exfiltrate documents, but more to exfiltrate environnement informations to either : 
- Sell them and get money over the stolen data
- Prepare and weaponize correctly for attacking a specific target while using a relatively discret malware before using the heavy infantry

## BottomFeeder
BottomFeeder is a payload used to completely wipe a folder (or a whole endpoint) on a machine, you can use it to destroy things, but you should be cautious using it.

# Functionnality
## Cuttlefish
Cuttlefish is a really good killswitch that aim to evade sandbox detection.
I tries to connect to a random domain, if the connection is a HTTP200, then it means we're in a sandbox because they tend to make all request go 200 to analyse behavior, but seing this, the killswitch is set to True and nothing happen
If the first condition is OK then it moves to the second which is a simple connection to google.com, it it does not work, then it means we're in an isolated environnement and it shut itself down to prevent analysis

## Shrimp
Shrimp is a trace cleaner that will erase a lot of forensic artefacts.
I can delete the evtx, prefetch, ...
A good tool when you want to hide what you did

## Limpet
Limpet is the functionnality that aim to achieve persistance on the endpoint, it try different methods and make sure that it's as hard as possible to remove (Just like real limpets after all)

## Plankton
Plankton is a deadcode generator, it's generate a lot of deadcode that does nothing, but decrease readability and helps getting metamorphic results