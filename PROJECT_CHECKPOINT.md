PROGETTO: cleaning_scheduler

STACK:
- Python
- Django
- SQLite
- VS Code
- Windows

APP DJANGO:
- apartments
- bookings
- cleanings
- condominiums
- employees
- operations_calendar
- accounting
- customers

---------------------------------------

FUNZIONALITÀ ATTIVE:

CALENDARIO:
- vista settimana / 15 giorni / mese / 3 mesi
- navigazione avanti / indietro / oggi
- evidenzia weekend
- separazione mesi
- filtri per tipologia immobile
- drag & drop pulizie
- assegnazione dipendenti
- note rapide
- click prenotazione → apertura dettaglio
- click pulizia → apertura dettaglio

PRENOTAZIONI:
- check-in / check-out con orari
- numero persone
- letti matrimoniali / singoli
- creazione automatica pulizia al check-out

PULIZIE:
- collegate a prenotazione
- modificabili manualmente
- spostabili
- costi modificabili

CLIENTI:
- un cliente può avere più immobili
- immobili collegati al cliente

CONTABILITÀ:
- filtro per cliente
- filtro per date
- somma automatica costi
- calcolo IVA
- report tabellare
- export PDF
- export Excel
- consuntivo mensile
- zip fatture mensili

DASHBOARD:
- totale mese
- totale anno
- media pulizia
- top clienti

---------------------------------------

LOGICA COSTI:

IMMOBILE contiene:
- costo pulizia
- costo kit fisso
- costo kit a persona
- costo letto matrimoniale
- costo letto singolo
- tappetino
- extra

BOOKING contiene:
- numero persone
- letti matrimoniali usati
- letti singoli usati

CLEANING:
- eredita dati da booking + immobile
- calcola total_cost:

FORMULA:
costo pulizia
+ kit fisso
+ (kit persona × persone)
+ (letto matrimoniale × numero letti matrimoniali)
+ (letto singolo × numero letti singoli)
+ tappetino
+ extra

---------------------------------------

AUTOMAZIONI:

- salvataggio prenotazione →
  crea/aggiorna pulizia al check-out

- pulizia:
  - collegata a booking
  - aggiorna costi automaticamente
  - mantiene override se modificata manualmente

---------------------------------------

MODELLI PRINCIPALI:

- Customer
- Apartment
- Booking
- Cleaning
- DayNote
- Invoice

---------------------------------------

URL PRINCIPALI:

- /
- /dashboard/
- /accounting/
- /accounting/pdf/
- /accounting/monthly/
- /accounting/monthly-invoices/
- /accounting/export/

---------------------------------------

FILE CHIAVE:

- apartments/models.py
- bookings/models.py
- cleanings/models.py
- accounting/views.py
- accounting/urls.py
- operations_calendar/views.py
- operations_calendar/templates/operations_calendar/month_calendar.html
- accounting/templates/accounting/report.html
- core/urls.py
- core/settings.py

---------------------------------------

STATO ATTUALE:

- sistema contabilità funzionante
- calcolo costi automatico attivo
- report cliente funzionante
- export PDF funzionante
- export Excel attivo
- fatture ZIP attive
- clienti collegati agli immobili

---------------------------------------

PROSSIMI SVILUPPI POSSIBILI:

- fattura professionale (logo, P.IVA, layout)
- gestione pagamenti
- storico fatture
- statistiche avanzate
- app mobile dipendenti
- notifiche automatiche
- automazione pianificazione pulizie

---------------------------------------

NOTE:

- verificare sempre i costi dopo modifiche ai modelli
- attenzione alle migrazioni Django
- backup prima di modifiche importanti