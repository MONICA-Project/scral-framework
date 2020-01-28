## MEETING ##
- SCRUM telco - aggiornamento tecnico
	ogni martedì alle 10.30 
	https://eu.yourcircuit.com/guest?token=19b398b9-924b-476f-a7dc-fb042069aef8
	ref: Benadik Jan
	
## MEETING CLOSED ##
- LOAD TESTING STRATEGY
	ogni martedì alle 14 - fino a Woodstower
	ref: Benadik Jan
	
## SCRAL ##
- Miglioramento del processo di deployment

### Development ###
- Completare API
    - Delete
    - Patch
    - Get (integrazione con GOST CLI)
    - Active Devices information
- Documentazione API per utenti finali (Swagger or others)
- Miglior documentazione di quanto sviluppato
- Generalizzare un po' meglio il codice e allineamento dei moduli

### Dashboard and Monitoring ###
- Docker Compose, InfluxDB, ThingsBoard and Kubernetes. 
- Monitoraggio/Supporto agli scenari di "load testing" (VPN, broker, SCRAL endpoint..)

### Deployment ###
- Best practice and guidelines (Dockerhub, Git ReadMe, Confluence, ...)
- Monica IoT Toolbox
    - Docker Compose Packages
        - Task 7.6: https://confluence.fit.fraunhofer.de/confluence/display/MNC/Docker+Compose+packages
    - Open Source Components
        - Task 7.6: https://confluence.fit.fraunhofer.de/confluence/display/MNC/Open+Source+Components     

### KNOWN Bugs & Issues ###
- Problema con la registrazione dei devices multi-processo,
pare che qualche registrazione possa fallire se nel frattempo il catalogo viene aggioranto
- Controllare warning su libreria Arrow

### DONE ###
- Storage resource catalog (tramite docker volume) (?)
- Dockerizza soluzione nginx + uwsgi + wristband
- Integrazione sensori ambientali su blimp (ref: Sebastian from HAW, Emanuele from DIGISKY)



### Cose nuove ###
- Changelog update!
- Possiamo togliere lo SCRAL startup? Serve solo per il dockerfile?

### Cose fatte
- Possiamo avere un unico file di configurazione? Sì
- Cambiare il banner in giro
- Mettere il GOST MQTT Prefix tra le variabili del file di configurazione