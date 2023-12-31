# Installatie
Om dit project te kunnen runnen moeten er een aantal dingen geïnstallerd zijn. Dit zijn:
Python: https://www.python.org/
IDE / code editor: https://code.visualstudio.com/
Volg de instructies op de desbetreffende sites voor de installatie.

Om Flask te kunnen starten zul je eerst de Flask packages moeten installeren. Wil je latere problemen met versies voorkomen, dan raden we je aan een virtual environment te maken en daar de modules in te installeren door de volgende regels code, per regel, in de terminal uit te voeren:
# Let op! Het kan zijn dat er een foutmelding optreed tijdens het uitvoeren van de volgende commando's. Kijk voor de oplossing bij het kopje: Probleemoplossing.
```
pip install virtualenv
virtualenv venv
.\venv\scripts\activate
pip install -r requirements.txt
```

# De applicatie
Typ de volgende commando's in de terminal om de applicatie te starten: 
``` 
.\venv\scripts\activate
python app.py
```
Wanneer de applicatie gestart wordt kom je terecht op het home scherm. In de header staan nu een aantal links/knoppen:
1. Home
	Dit leidt terug naar het home scherm. Hierop is een uitleg over onze website zichtbaar.

2. Vragen platform
	Indien je niet bent ingelogd, leidt deze link je naar het inlogscherm.
	Indien je wel ingelogd bent, heb je nu enkele knoppen voor je om een selectie te maken voor het soort vraag dat je wilt zien.
		Daaronder staan de vragen die voldoen aan de geselecteerde opties. Wanneer je op een vraag klikt, komt er een nieuw menu naar voren. Hierop kunnen waardes aangepast worden en kan de vraag een uitzondderingstag gegeven worden. Er is een extra optie om ervoor te zorgen dat deze niet langer in de zoekopdrachten naar voren komen (tenzij hier specifiek op gezocht wordt). Ook kan je op een ID klikken om naar de betreffende vraag te gaan.

3. Admin
	Deze knop is alleen zichtbaar als je bent ingelogd met een administrator account. Het heeft net als het vragen plaatform een aantal knoppen om een selectie van gebruikers te laten zien. De gebruikers verschijnen hieronder.
	Ook hier kan je op een gebruiker klikken om meer informatie te zien. Hier is ook meteen een optie om de informatie van de gebruiker aan te passen en de eventueel te verwijderen.
	Er is ook een knop beschikbaar voor het aanmaken van nieuwe gebruikers. Het aanmaken van een administrator account is hier niet mogelijk en moet handmatig gedaan worden.

4. Login / Logout
	Indien je niet bent ingelogd, is de inlogknop zichtbaar. Deze leidt naar het inlogscherm. Op het inlogscherm wordt gevraagd om een gebruikersnaam en wachtwoord, welke na het invoeren geverifieerd worden. Indien dit succesvol is, wordt je ingelogd en wordt je naar het vragen platform geleidt.
	Indien je wel bent ingelogd, is de knop om uit te loggen zichtbaar. Deze logt de huidige gebruiker uit en leidt daarna naar het home scherm.

# Probleemoplossing:
1. 
```
Foutcode:
File "Pathname here"\venv\Scripts\Activate.ps1 cannot be loaded. The file "Pathname here"\venv\Scripts\Activate.ps1 is not digitally signed. You cannot run this script on the current system. For more information about running scripts and setting execution policy, see about_Execution_Policies at https:/go.microsoft.com/fwlink/?LinkID=135170.

Oplossing:
Voer de volgende code uit in de terminal: Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process

Waarschuwing!
Dit zorgt ervoor dat elk script in de IDE zonder controle gerunned kan worden, zolang deze draait. Nadat de IDE afgesloten is wordt deze policy weer naar de standaard teruggezet. Zorg er dus voor dat je, als je klaar bent, de IDE afsluit!
```