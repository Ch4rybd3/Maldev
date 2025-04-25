# WannaSwim
WannaSwim is a ransomware that aim to reproduce some of the mecanism of Wannacry.

# Prerequisites
- A workstation to launch the env_setup.exe file + the payload.exe file
- A C2 that is accessible through Internet (the free plan of AWS gives you a t2.micro for free for a year, which is more than enough), you could also use a website like .requestcatcher.com and set a custom domain, but you'll loose the capabilities of the C2 server which will log the results, ...

# Disclaimer
Even if this is a ransomware, it should be "risk-free" as the env_setup is creating a custom folder named CTF-FSA-002_Documents underr the user Document folder and everything is ran inside of this scope, so it could get launched on a workstation without any issue, but you should have the folder and exe whitelisted in your EDR (because this will trigger everything, like really, nothing really silent here)