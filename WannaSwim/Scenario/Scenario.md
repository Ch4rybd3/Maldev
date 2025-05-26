# Context
Vous êtes un spécialiste en DFIR, mandaté par un client, vous allez suivre le processus typique d'une réponse a incident.

# étapes de la DFIR simplifiée
## Prise de contact initiale
Le client "ICan'tC#", un producteur de lentilles pour lunettes vous contacte, complètement affolé car les postes de son parc informatique semblent ne plus fonctionner.
Il aborde le thème de virus, et dis avoir trouvé votre numéro sur le site du gouvernement pour connecter les victimes de cyberattaques avec les entreprises de DFIR.
Vous l'invitez donc a un échange de mail fournis dans le doccier de contexte.

## Détection, analyse
Vous utiliserez les outils des équipes sécurité du client pour cette investigation.
Le client dispose de : 
- SentinelOne (il dispose d'une licence Remote Ops + Forensic)
- Zscaler
- Varonis
- Crowdtrike (mollo avec l'outil, a utiliser en dernier quand le reste est passé pour s'assurer que rien n'a été oublié)
Vous suivrez les étapes de réponse a incident défini dans la norme de votre choix, nous conseillons : 
- NIST SP800-61
- ISO 27035
L'idée est de produire un rapport suivant la norme ci-dessus et de le présenter au client(reste de l'équipe).
Un template au format SP800-61 est disponible sous SERVEURSECU\Pôle IT\Securité Opé\Rapports Incident\0 - DFIR Template.docx

## Contenir, éradiquer, recouvrir
Vous pourrez utiliser les outils pour documenter les étapes de rémédiations
Toutes les actions de réponses doivent être documenté et non realisées (bloquer un hash dans S1 : On l'écrit dans le rapport, mais on ne le fait pas :P), l'idée est de ne pas briquer le CTF pour les autres.

# Objectifs
Les objectifs de ce CTF sont multiples : 
- Progresser sur les outils de Remote Ops principalement, mais tout les outils du SOC peuvent être utilisés (Même CrowdStrike, mais attendez un peu avant de le faire péter dedans tout de même, gardez un peu de challenge).
- Progresser sur la rédaction de rapport d'incident majeur
- Progresser sur la position de prestataire en réponse a incidents
- Progresser en réponse sur un certain type de malwares très utilisé
- Progresser en Forensic.

Comment commencer le CTF : 
Il faut copier coller les fichiers env_setup.exe et CTF-FSA-002.exe sur le Desktop de l'utilisateur (chemin Whitelisté)

