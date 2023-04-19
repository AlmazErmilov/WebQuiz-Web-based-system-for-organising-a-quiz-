# NOE ENDRRINGER FOR A TESTE GIT DESKTOP 2. gang
# WebQuiz
#### Faget Databaser og webapplikasjoner, våren 2023. 
Note: Executed strictly what is required for the task below — no more, no less.\
(even though the assignment itself is a bit odd)

### Webbasert system for gjennomføring av en quiz. 

#### Systembeskrivelse

Det skal utvikles et system som tar for seg spørsmål og svar (quiz) via et grensesnitt på web. Systemet skal ha to brukertyper slik at noen lager quiz/spørsmål og andre kan svare/gjennomføre quiz. Den ene er quiz-administrator, det vil si den som definerer spørsmål og quiz. Den andre brukertypen er de som skal kunne gjennomføre quiz. Disse brukerne skal kunne velge blant definerte quiz. Dette betyr at, avhengig av bruker, skal man få opp to ulike typer grensesnitt, en vanlig bruker og en administrator. En quiz består av et sett spørsmål som i utgangspunktet skal ta høyde for ulike spørsmålstyper. 

Forsiden skal inneholde en form for "login" hvor man kan spesifisere brukertype. Hvis man velger administrator skal man få opp alle spørsmål og svar, med redigeringsmuligheter for alle felter. Det skal også være mulig for en administrator å se svar knyttet til hvert spørsmål. Det vil si at når en quiz er satt som aktivt, vil en vanlig bruker få opp spørsmålene og svarmulighet. Når brukeren er fornøyd med svarene skal det trykkes send/lagre slik at administrator får opp alle svarene til en bruker. Dette medfører at ulike brukere vil kunne svare forskjellig og en administrator skal få opp alle svar knyttet til et spørsmål. Et hovedelement er at administrator skal kunne ha navn (fornavn og etternavn), mens vanlige brukere skal være anonyme når de svarer. Det er forskjell på å lage en quiz som består av et sett spørsmål og det å gjennomføre en quiz, som vi for øvrig kan se på som en quiz-sesjon eller lignende. 

I databasen vil det være viktig å skille på definisjon av spørsmål og quiz og gjennomføringen av en quiz. Administrator må kunne definere/lagre spørsmål og quizer. Når en vanlig bruker gjennomfører en quiz må databasen kunne lagre informasjon om dette (hvilken quiz, hvilke svar ble gitt).  

Databasen må modelleres med relasjoner, primærnøkler og fremmednøkler etter prinsipper for ER-modellering. Det anbefales å bruke WorkBench til modellering og konstruksjon av databasen. 

#### Oppgave:

1. Lag et web basert system med en hovedside som viser valg av bruker (type her kan være bruker 1 og bruker 2 med ulike rettigheter som beskrevet over). Avhengig av hvilken bruker man velger, vil man få opp enten:
- Alle spørsmål, med redigeringsmuligheter slik som endring av felter, slettet spørsmål og endre svar, samt se svar. 
- Vanlig bruker: et og et spørsmål med mulighet for å svare og gå videre til neste spørsmål, samt sende/lagre hele quizen.
2. Det skal være mulig for administrator å kunne fjerne spørsmål, endre all informasjon for et spørsmål, samt sette spørsmålene inn i kategorier. (ie. sport, historie, matematikk osv). 
3. Benytt templates og mest mulig objektorienterte prinsipper i løsningen
4. Valider dokumenter og stilark hos http://www.w3c.org/
