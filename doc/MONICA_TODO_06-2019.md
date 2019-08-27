## MEETING ##

- SCRUM telco - aggiornamento tecnico
	ogni martedì alle 10.30 
	https://eu.yourcircuit.com/guest?token=19b398b9-924b-476f-a7dc-fb042069aef8
	ref: Benadik Jan

- LOAD TESTING STRATEGY
	ogni martedì alle 14 - fino a ?
	ref: Benadik Jan

## SCRAL ##

- Monitoraggio/Supporto agli scenari di "load testing" (VPN, broker, SCRAL endpoint..)
- Miglioramento del processo di deployment
- Controllare warning su libreria Arrow

### KNOWN BUGS ###
- Problema con la registrazione dei devices multi-processo,
pare che qualche registrazione possa fallire se nel frattempo il catalogo viene aggioranto

### DONE ###
- Storage resource catalog (tramite docker volume)
- Dockerizza soluzione nginx + uwsgi + wristband
- Integrazione sensori ambientali su blimp (ref: Sebastian from HAW, Emanuele from DIGISKY)
