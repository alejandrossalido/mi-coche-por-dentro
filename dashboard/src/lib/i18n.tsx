'use client';

import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';

export type AppLanguage = 'es' | 'en' | 'it' | 'de';

export const APP_LANGUAGES: Array<{ id: AppLanguage; short: string; name: string; nativeName: string }> = [
  { id: 'es', short: 'ES', name: 'Spanish', nativeName: 'Español' },
  { id: 'en', short: 'EN', name: 'English', nativeName: 'English' },
  { id: 'it', short: 'IT', name: 'Italian', nativeName: 'Italiano' },
  { id: 'de', short: 'DE', name: 'German', nativeName: 'Deutsch' }
];

type Translation = { en: string; it: string; de: string };

// Spanish is the canonical source language. Keeping the source sentence as the
// key also lets us localize safe messages returned by the local backend.
export const UI_TRANSLATIONS: Record<string, Translation> = {
  'Velocidad del árbol de levas': { en: 'Camshaft speed', it: 'Regime albero a camme', de: 'Nockenwellendrehzahl' },
  'Refrigerante a la salida del radiador': { en: 'Coolant at radiator outlet', it: 'Refrigerante all’uscita del radiatore', de: 'Kühlmittel am Kühlerausgang' },
  'Mando del ventilador del radiador': { en: 'Radiator fan command', it: 'Comando ventola radiatore', de: 'Kühlerlüfter-Ansteuerung' },
  'Carga del alternador': { en: 'Alternator load', it: 'Carico alternatore', de: 'Generatorlast' },
  'Par calculado del motor': { en: 'Calculated engine torque', it: 'Coppia motore calcolata', de: 'Berechnetes Motordrehmoment' },
  'Par solicitado por el conductor': { en: 'Driver requested torque', it: 'Coppia richiesta dal conducente', de: 'Fahrerwunschmoment' },
  'Selecciona tu idioma': { en: 'Select your language', it: 'Seleziona la lingua', de: 'Sprache auswählen' },
  'Puedes cambiarlo en cualquier momento': { en: 'You can change it at any time', it: 'Puoi cambiarla in qualsiasi momento', de: 'Du kannst sie jederzeit ändern' },
  'Idioma': { en: 'Language', it: 'Lingua', de: 'Sprache' },
  'Seleccionar idioma': { en: 'Select language', it: 'Seleziona lingua', de: 'Sprache auswählen' },
  'Continuar': { en: 'Continue', it: 'Continua', de: 'Weiter' },
  'Paso': { en: 'Step', it: 'Passaggio', de: 'Schritt' },
  'de 3': { en: 'of 3', it: 'di 3', de: 'von 3' },
  'de 4': { en: 'of 4', it: 'di 4', de: 'von 4' },
  'Cerrar bienvenida': { en: 'Close welcome', it: 'Chiudi introduzione', de: 'Einführung schließen' },
  'Conecta el coche cuando quieras medir': { en: 'Connect the car when you want to measure', it: 'Collega l’auto quando vuoi misurare', de: 'Verbinde das Fahrzeug, wenn du messen möchtest' },
  'La aplicación no registra nada antes de iniciar una prueba. Primero comprueba el adaptador y la ECU.': { en: 'The application records nothing before a test starts. It first checks the adapter and ECU.', it: 'L’applicazione non registra nulla prima dell’avvio di un test. Prima controlla adattatore ed ECU.', de: 'Die Anwendung zeichnet vor dem Start eines Tests nichts auf. Zuerst werden Adapter und ECU geprüft.' },
  'Sigue una prueba reproducible': { en: 'Follow a reproducible test', it: 'Segui un test riproducibile', de: 'Führe einen reproduzierbaren Test durch' },
  'El modo guiado recomienda el protocolo y te dice qué hacer. Los datos se guardan automáticamente durante la captura.': { en: 'Guided mode recommends the protocol and tells you what to do. Data is saved automatically during capture.', it: 'La modalità guidata consiglia il protocollo e indica cosa fare. I dati vengono salvati automaticamente durante l’acquisizione.', de: 'Der geführte Modus empfiehlt das Protokoll und erklärt die Schritte. Die Daten werden während der Aufzeichnung automatisch gespeichert.' },
  'Analiza una sesión concreta': { en: 'Analyse a specific session', it: 'Analizza una sessione specifica', de: 'Analysiere eine bestimmte Sitzung' },
  'El asistente explica la sesión que selecciones. No mezcla carreras anteriores ni inventa mediciones ausentes.': { en: 'The assistant explains the selected session. It does not mix previous drives or invent missing measurements.', it: 'L’assistente spiega la sessione selezionata. Non mescola tragitti precedenti né inventa misure mancanti.', de: 'Der Assistent erklärt die ausgewählte Sitzung. Er vermischt keine früheren Fahrten und erfindet keine fehlenden Messwerte.' },
  'Empezar en modo guiado': { en: 'Start in guided mode', it: 'Avvia in modalità guidata', de: 'Im geführten Modus starten' },
  'Prefiero el modo profesional': { en: 'I prefer professional mode', it: 'Preferisco la modalità professionale', de: 'Ich bevorzuge den Profimodus' },
  'Modo guiado': { en: 'Guided mode', it: 'Modalità guidata', de: 'Geführter Modus' },
  'Modo profesional': { en: 'Professional mode', it: 'Modalità professionale', de: 'Profimodus' },
  '¿Cómo funciona?': { en: 'How does it work?', it: 'Come funziona?', de: 'Wie funktioniert es?' },
  'Todos los controles y datos técnicos visibles': { en: 'All controls and technical data visible', it: 'Tutti i controlli e i dati tecnici visibili', de: 'Alle Bedienelemente und technischen Daten sichtbar' },
  'La aplicación te acompaña paso a paso': { en: 'The application guides you step by step', it: 'L’applicazione ti guida passo dopo passo', de: 'Die Anwendung führt dich Schritt für Schritt' },
  'SISTEMA DE INFORMACIÓN DEL VEHÍCULO // 02': { en: 'VEHICLE INFORMATION SYSTEM // 02', it: 'SISTEMA INFORMATIVO DEL VEICOLO // 02', de: 'FAHRZEUGINFORMATIONSSYSTEM // 02' },
  'MI COCHE': { en: 'MY CAR', it: 'LA MIA AUTO', de: 'MEIN AUTO' },
  'POR DENTRO': { en: 'FROM THE INSIDE', it: 'DALL’INTERNO', de: 'VON INNEN' },
  'TELEMETRÍA · DIAGNÓSTICO · LABORATORIO DE RENDIMIENTO': { en: 'TELEMETRY · DIAGNOSTICS · PERFORMANCE LAB', it: 'TELEMETRIA · DIAGNOSTICA · LABORATORIO PRESTAZIONI', de: 'TELEMETRIE · DIAGNOSE · LEISTUNGSLABOR' },
  'SESIÓN': { en: 'SESSION', it: 'SESSIONE', de: 'SITZUNG' },
  'PERFIL DEL VEHÍCULO': { en: 'VEHICLE PROFILE', it: 'PROFILO VEICOLO', de: 'FAHRZEUGPROFIL' },
  'NINGÚN VEHÍCULO SELECCIONADO': { en: 'NO VEHICLE SELECTED', it: 'NESSUN VEICOLO SELEZIONATO', de: 'KEIN FAHRZEUG AUSGEWÄHLT' },
  'ESTADO DE CONEXIÓN OBD': { en: 'OBD CONNECTION STATUS', it: 'STATO CONNESSIONE OBD', de: 'OBD-VERBINDUNGSSTATUS' },
  'GRABANDO EN DIRECTO': { en: 'LIVE RECORDING', it: 'REGISTRAZIONE IN DIRETTA', de: 'LIVE-AUFZEICHNUNG' },
  'ECU CONECTADA': { en: 'ECU CONNECTED', it: 'ECU CONNESSA', de: 'ECU VERBUNDEN' },
  'EN ESPERA': { en: 'STANDBY', it: 'IN ATTESA', de: 'BEREIT' },
  'Confianza de los datos': { en: 'Data confidence', it: 'Affidabilità dei dati', de: 'Datenvertrauen' },
  'Origen': { en: 'Source', it: 'Origine', de: 'Quelle' },
  'Captura': { en: 'Capture', it: 'Acquisizione', de: 'Aufzeichnung' },
  'Calidad en directo': { en: 'Live quality', it: 'Qualità in tempo reale', de: 'Live-Qualität' },
  'Cobertura': { en: 'Coverage', it: 'Copertura', de: 'Abdeckung' },
  'Conservación': { en: 'Storage', it: 'Conservazione', de: 'Speicherung' },
  'Sin captura seleccionada': { en: 'No capture selected', it: 'Nessuna acquisizione selezionata', de: 'Keine Aufzeichnung ausgewählt' },
  'Esperando primera lectura': { en: 'Waiting for first reading', it: 'In attesa della prima lettura', de: 'Warten auf den ersten Messwert' },
  'Registrando ahora': { en: 'Recording now', it: 'Registrazione in corso', de: 'Aufzeichnung läuft' },
  'Pendiente': { en: 'Pending', it: 'In attesa', de: 'Ausstehend' },
  'Autoguardado activo': { en: 'Autosave active', it: 'Salvataggio automatico attivo', de: 'Automatisches Speichern aktiv' },
  'Datos fiables': { en: 'Reliable data', it: 'Dati affidabili', de: 'Zuverlässige Daten' },
  'Datos medidos': { en: 'Measured data', it: 'Dati misurati', de: 'Gemessene Daten' },
  'Datos simulados': { en: 'Simulated data', it: 'Dati simulati', de: 'Simulierte Daten' },
  'PUERTO OBD': { en: 'OBD PORT', it: 'PORTA OBD', de: 'OBD-PORT' },
  'PROTOCOLO DE LA ECU': { en: 'ECU PROTOCOL', it: 'PROTOCOLLO ECU', de: 'ECU-PROTOKOLL' },
  'LATENCIA DEL BUS': { en: 'BUS LATENCY', it: 'LATENZA BUS', de: 'BUS-LATENZ' },
  'FRECUENCIA DE MUESTREO': { en: 'SAMPLE RATE', it: 'FREQUENZA DI CAMPIONAMENTO', de: 'ABTASTRATE' },
  'LECTURAS CORRECTAS': { en: 'VALID READINGS', it: 'LETTURE CORRETTE', de: 'GÜLTIGE MESSWERTE' },
  'TENSIÓN OBD / ECU': { en: 'OBD / ECU VOLTAGE', it: 'TENSIONE OBD / ECU', de: 'OBD-/ECU-SPANNUNG' },
  'Sin puerto verificado': { en: 'No verified port', it: 'Nessuna porta verificata', de: 'Kein verifizierter Port' },
  'Protocolo pendiente': { en: 'Protocol pending', it: 'Protocollo in attesa', de: 'Protokoll ausstehend' },
  'Vehículo del garaje': { en: 'Garage vehicle', it: 'Veicolo del garage', de: 'Fahrzeug aus der Garage' },
  'Añadir vehículo': { en: 'Add vehicle', it: 'Aggiungi veicolo', de: 'Fahrzeug hinzufügen' },
  'Puerto del adaptador': { en: 'Adapter port', it: 'Porta adattatore', de: 'Adapter-Port' },
  'Ningún adaptador USB detectado': { en: 'No USB adapter detected', it: 'Nessun adattatore USB rilevato', de: 'Kein USB-Adapter erkannt' },
  'recomendado': { en: 'recommended', it: 'consigliato', de: 'empfohlen' },
  'no es OBD': { en: 'not OBD', it: 'non OBD', de: 'kein OBD' },
  'Conectar OBD': { en: 'Connect OBD', it: 'Collega OBD', de: 'OBD verbinden' },
  'Informe': { en: 'Report', it: 'Rapporto', de: 'Bericht' },
  'Diagnóstico completo': { en: 'Full diagnostic', it: 'Diagnosi completa', de: 'Vollständige Diagnose' },
  'Finalizar y analizar': { en: 'Finish and analyse', it: 'Termina e analizza', de: 'Beenden und analysieren' },
  'Diagnóstico': { en: 'Diagnostics', it: 'Diagnostica', de: 'Diagnose' },
  'Sesiones': { en: 'Sessions', it: 'Sessioni', de: 'Sitzungen' },
  'Asistente de diagnóstico': { en: 'Diagnostic assistant', it: 'Assistente diagnostico', de: 'Diagnoseassistent' },
  'Antes / Después': { en: 'Before / After', it: 'Prima / Dopo', de: 'Vorher / Nachher' },
  'Garaje': { en: 'Garage', it: 'Garage', de: 'Garage' },
  'ITV / Monitores': { en: 'Inspection / Monitors', it: 'Revisione / Monitor', de: 'HU / Monitore' },
  'Modo 06': { en: 'Mode 06', it: 'Modalità 06', de: 'Modus 06' },
  'Cobertura OBD genérica': { en: 'Generic OBD coverage', it: 'Copertura OBD generica', de: 'Generische OBD-Abdeckung' },
  'Ficha específica confirmada': { en: 'Specific profile confirmed', it: 'Scheda specifica confermata', de: 'Spezifisches Profil bestätigt' },
  'Línea base aprendida': { en: 'Learned baseline', it: 'Baseline appresa', de: 'Gelernte Referenz' },
  'Límites personalizados': { en: 'Custom limits', it: 'Limiti personalizzati', de: 'Benutzerdefinierte Grenzwerte' },
  'Motor pendiente de identificar': { en: 'Engine identification pending', it: 'Identificazione motore in attesa', de: 'Motoridentifikation ausstehend' },
  'Comprobando cobertura…': { en: 'Checking coverage…', it: 'Verifica copertura…', de: 'Abdeckung wird geprüft…' },
  'Buscando adaptador y ECU…': { en: 'Searching for adapter and ECU…', it: 'Ricerca di adattatore ed ECU…', de: 'Adapter und ECU werden gesucht…' },
  'No se encontró una ECU operativa. Revisa contacto y puerto.': { en: 'No responding ECU was found. Check ignition and port.', it: 'Nessuna ECU operativa trovata. Controlla quadro e porta.', de: 'Keine antwortende ECU gefunden. Zündung und Port prüfen.' },
  'Adaptador conectado y ECU detectada.': { en: 'Adapter connected and ECU detected.', it: 'Adattatore collegato ed ECU rilevata.', de: 'Adapter verbunden und ECU erkannt.' },
  'No se pudo conectar con el adaptador.': { en: 'Could not connect to the adapter.', it: 'Impossibile collegarsi all’adattatore.', de: 'Verbindung zum Adapter fehlgeschlagen.' },
  'Validando conexión y señales compatibles…': { en: 'Validating connection and compatible signals…', it: 'Verifica di connessione e segnali compatibili…', de: 'Verbindung und kompatible Signale werden geprüft…' },
  'Captura validada e iniciada. Sigue las instrucciones del protocolo.': { en: 'Capture validated and started. Follow the test instructions.', it: 'Acquisizione convalidata e avviata. Segui le istruzioni del protocollo.', de: 'Aufzeichnung validiert und gestartet. Folge den Testanweisungen.' },
  'Error durante la prevalidación del diagnóstico.': { en: 'Error during diagnostic pre-check.', it: 'Errore durante la prevalidazione diagnostica.', de: 'Fehler bei der Diagnose-Vorprüfung.' },
  'No se pudo iniciar la captura.': { en: 'Could not start capture.', it: 'Impossibile avviare l’acquisizione.', de: 'Aufzeichnung konnte nicht gestartet werden.' },
  'No se pudo detener la sesión.': { en: 'Could not stop the session.', it: 'Impossibile arrestare la sessione.', de: 'Sitzung konnte nicht beendet werden.' },
  'No se pudo leer los DTC.': { en: 'Could not read DTCs.', it: 'Impossibile leggere i DTC.', de: 'DTCs konnten nicht gelesen werden.' },
  'La ECU no informa de códigos DTC.': { en: 'The ECU reports no DTCs.', it: 'L’ECU non segnala DTC.', de: 'Die ECU meldet keine DTCs.' },
  'Pruebas guiadas determinantes': { en: 'Guided diagnostic tests', it: 'Test diagnostici guidati', de: 'Geführte Diagnosetests' },
  'Objetivo seleccionado': { en: 'Selected objective', it: 'Obiettivo selezionato', de: 'Ausgewähltes Ziel' },
  'Selecciona objetivo': { en: 'Select objective', it: 'Seleziona obiettivo', de: 'Ziel auswählen' },
  'Validar OBD e iniciar': { en: 'Validate OBD and start', it: 'Convalida OBD e avvia', de: 'OBD prüfen und starten' },
  'Validar conexión e iniciar esta prueba': { en: 'Validate connection and start this test', it: 'Convalida la connessione e avvia il test', de: 'Verbindung prüfen und Test starten' },
  'Diagnóstico completo guiado': { en: 'Guided full diagnostic', it: 'Diagnosi completa guidata', de: 'Geführte vollständige Diagnose' },
  'Batería o carga eléctrica': { en: 'Battery or charging system', it: 'Batteria o sistema di ricarica', de: 'Batterie oder Ladesystem' },
  'Temperatura o refrigeración': { en: 'Temperature or cooling', it: 'Temperatura o raffreddamento', de: 'Temperatur oder Kühlung' },
  'Ralentí inestable o vibración': { en: 'Unstable idle or vibration', it: 'Minimo instabile o vibrazioni', de: 'Unruhiger Leerlauf oder Vibration' },
  'Falta de potencia': { en: 'Loss of power', it: 'Perdita di potenza', de: 'Leistungsverlust' },
  'Humo, consumo o emisiones': { en: 'Smoke, consumption or emissions', it: 'Fumo, consumo o emissioni', de: 'Rauch, Verbrauch oder Emissionen' },
  'Le cuesta arrancar': { en: 'Hard to start', it: 'Avviamento difficile', de: 'Startschwierigkeiten' },
  'Elige el síntoma y prepararemos la prueba que mejor puede confirmarlo con datos.': { en: 'Choose the symptom and we will prepare the test most likely to confirm it with data.', it: 'Scegli il sintomo e prepareremo il test più adatto a confermarlo con i dati.', de: 'Wähle das Symptom; wir bereiten den Test vor, der es am besten mit Daten bestätigen kann.' },
  '¿Qué notas en el coche?': { en: 'What do you notice in the car?', it: 'Cosa noti nell’auto?', de: 'Was bemerkst du am Fahrzeug?' },
  'Describe cuándo ocurre (opcional)': { en: 'Describe when it happens (optional)', it: 'Descrivi quando accade (facoltativo)', de: 'Beschreibe, wann es auftritt (optional)' },
  'Describe el síntoma con tus palabras…': { en: 'Describe the symptom in your own words…', it: 'Descrivi il sintomo con parole tue…', de: 'Beschreibe das Symptom mit eigenen Worten…' },
  'Kilometraje (opcional)': { en: 'Mileage (optional)', it: 'Chilometraggio (facoltativo)', de: 'Kilometerstand (optional)' },
  'Frío, antes de arrancar': { en: 'Cold, before starting', it: 'Freddo, prima dell’avviamento', de: 'Kalt, vor dem Start' },
  'A temperatura normal': { en: 'At normal temperature', it: 'A temperatura normale', de: 'Bei normaler Temperatur' },
  'Muy caliente': { en: 'Very hot', it: 'Molto caldo', de: 'Sehr heiß' },
  'Iniciar prueba': { en: 'Start test', it: 'Avvia test', de: 'Test starten' },
  'Cuadro de instrumentos': { en: 'Instrument panel', it: 'Quadro strumenti', de: 'Instrumententafel' },
  'Motor / Marcha': { en: 'Engine / Driving', it: 'Motore / Marcia', de: 'Motor / Fahrt' },
  'Temperaturas': { en: 'Temperatures', it: 'Temperature', de: 'Temperaturen' },
  'Admisión / Aire': { en: 'Intake / Air', it: 'Aspirazione / Aria', de: 'Ansaugung / Luft' },
  'Combustible / Mezcla': { en: 'Fuel / Mixture', it: 'Carburante / Miscela', de: 'Kraftstoff / Gemisch' },
  'Escape / DPF': { en: 'Exhaust / DPF', it: 'Scarico / DPF', de: 'Abgas / DPF' },
  'Sistema eléctrico': { en: 'Electrical system', it: 'Sistema elettrico', de: 'Elektrisches System' },
  'Marcador de incidencias // registro rápido': { en: 'Event marker // quick log', it: 'Indicatore eventi // registro rapido', de: 'Ereignismarker // Schnellprotokoll' },
  'Tirón': { en: 'Jerking', it: 'Strappo', de: 'Ruckeln' },
  'Pérdida potencia': { en: 'Power loss', it: 'Perdita di potenza', de: 'Leistungsverlust' },
  'Vibración': { en: 'Vibration', it: 'Vibrazione', de: 'Vibration' },
  'Humo': { en: 'Smoke', it: 'Fumo', de: 'Rauch' },
  'Ralentí irregular': { en: 'Irregular idle', it: 'Minimo irregolare', de: 'Unruhiger Leerlauf' },
  'Ruido / anomalía': { en: 'Noise / anomaly', it: 'Rumore / anomalia', de: 'Geräusch / Auffälligkeit' },
  'Memoria de averías de la ECU // códigos DTC': { en: 'ECU fault memory // DTC codes', it: 'Memoria guasti ECU // codici DTC', de: 'ECU-Fehlerspeicher // DTC-Codes' },
  'Buscar averías': { en: 'Scan faults', it: 'Cerca guasti', de: 'Fehler suchen' },
  'NO HAY AVERÍAS GUARDADAS NI PENDIENTES // SISTEMA SIN DTC': { en: 'NO STORED OR PENDING FAULTS // SYSTEM WITHOUT DTCs', it: 'NESSUN GUASTO MEMORIZZATO O IN ATTESA // SISTEMA SENZA DTC', de: 'KEINE GESPEICHERTEN ODER AUSSTEHENDEN FEHLER // SYSTEM OHNE DTCs' },
  'Monitorización activa sin alertas críticas': { en: 'Active monitoring without critical alerts', it: 'Monitoraggio attivo senza avvisi critici', de: 'Aktive Überwachung ohne kritische Warnungen' },
  'La captura sigue abierta, pero la ECU ha dejado de responder': { en: 'Capture is still open, but the ECU has stopped responding', it: 'L’acquisizione è ancora aperta, ma l’ECU non risponde più', de: 'Die Aufzeichnung ist noch offen, aber die ECU antwortet nicht mehr' },
  'Alerta activa durante la marcha': { en: 'Active alert while driving', it: 'Avviso attivo durante la marcia', de: 'Aktive Warnung während der Fahrt' },
  'Captura inactiva': { en: 'Capture inactive', it: 'Acquisizione inattiva', de: 'Aufzeichnung inaktiv' },
  'Captura activa': { en: 'Capture active', it: 'Acquisizione attiva', de: 'Aufzeichnung aktiv' },
  'Esperando lectura': { en: 'Waiting for reading', it: 'In attesa della lettura', de: 'Warten auf Messwert' },
  'Dato real de la ECU': { en: 'Real ECU data', it: 'Dato reale ECU', de: 'Realer ECU-Wert' },
  'Dato OBD genérico': { en: 'Generic OBD data', it: 'Dato OBD generico', de: 'Generischer OBD-Wert' },
  'Calculado con caudal y velocidad de la ECU': { en: 'Calculated from ECU flow and speed', it: 'Calcolato da portata e velocità ECU', de: 'Aus ECU-Durchfluss und Geschwindigkeit berechnet' },
  'Promedio integrado del trayecto': { en: 'Integrated trip average', it: 'Media integrata del tragitto', de: 'Integrierter Fahrtmittelwert' },
  'No disponible': { en: 'Unavailable', it: 'Non disponibile', de: 'Nicht verfügbar' },
  'No ofrecido por esta ECU': { en: 'Not provided by this ECU', it: 'Non fornito da questa ECU', de: 'Von dieser ECU nicht bereitgestellt' },
  'Pendiente de identificar en esta ECU': { en: 'Identification pending for this ECU', it: 'Identificazione in attesa per questa ECU', de: 'Identifikation für diese ECU ausstehend' },
  'Formato distinto en esta ECU': { en: 'Different format on this ECU', it: 'Formato diverso su questa ECU', de: 'Abweichendes Format bei dieser ECU' },
  'Biblioteca de sesiones': { en: 'Session library', it: 'Libreria sessioni', de: 'Sitzungsbibliothek' },
  'Encuentra, nombra, analiza y compara cada prueba sin perder su contexto.': { en: 'Find, name, analyse and compare every test without losing its context.', it: 'Trova, nomina, analizza e confronta ogni test senza perderne il contesto.', de: 'Finde, benenne, analysiere und vergleiche jeden Test, ohne den Kontext zu verlieren.' },
  'Buscar por nombre, síntoma o vehículo…': { en: 'Search by name, symptom or vehicle…', it: 'Cerca per nome, sintomo o veicolo…', de: 'Nach Name, Symptom oder Fahrzeug suchen…' },
  'Todos los vehículos': { en: 'All vehicles', it: 'Tutti i veicoli', de: 'Alle Fahrzeuge' },
  'Aún no hay sesiones en esta vista': { en: 'There are no sessions in this view yet', it: 'Non ci sono ancora sessioni in questa vista', de: 'In dieser Ansicht gibt es noch keine Sitzungen' },
  'Seleccionar sesión…': { en: 'Select session…', it: 'Seleziona sessione…', de: 'Sitzung auswählen…' },
  'Renombrar': { en: 'Rename', it: 'Rinomina', de: 'Umbenennen' },
  'Guardar cambios': { en: 'Save changes', it: 'Salva modifiche', de: 'Änderungen speichern' },
  'Cancelar edición': { en: 'Cancel editing', it: 'Annulla modifica', de: 'Bearbeitung abbrechen' },
  'Asistente técnico // conversación con evidencias': { en: 'Technical assistant // evidence-based conversation', it: 'Assistente tecnico // conversazione basata su prove', de: 'Technischer Assistent // evidenzbasiertes Gespräch' },
  'Cuéntame qué notas. Separaré hechos medidos, posibilidades y siguientes comprobaciones.': { en: 'Tell me what you notice. I will separate measured facts, possibilities and next checks.', it: 'Dimmi cosa noti. Separero i fatti misurati, le possibilità e i controlli successivi.', de: 'Beschreibe deine Beobachtung. Ich trenne Messfakten, Möglichkeiten und nächste Prüfungen.' },
  'Nivel de explicación': { en: 'Explanation level', it: 'Livello di spiegazione', de: 'Erklärungsniveau' },
  'Conductor': { en: 'Driver', it: 'Conducente', de: 'Fahrer' },
  'Técnico': { en: 'Technical', it: 'Tecnico', de: 'Technisch' },
  'Taller': { en: 'Workshop', it: 'Officina', de: 'Werkstatt' },
  'Motor de respuesta': { en: 'Response engine', it: 'Motore di risposta', de: 'Antwortsystem' },
  'Análisis local verificable: los datos no salen del equipo.': { en: 'Verifiable local analysis: data never leaves this computer.', it: 'Analisi locale verificabile: i dati non lasciano il computer.', de: 'Überprüfbare lokale Analyse: Die Daten verlassen den Computer nicht.' },
  'Añade una explicación generativa, manteniendo intactos los resultados OBD locales.': { en: 'Adds a generative explanation while keeping local OBD results unchanged.', it: 'Aggiunge una spiegazione generativa mantenendo invariati i risultati OBD locali.', de: 'Ergänzt eine generative Erklärung, ohne lokale OBD-Ergebnisse zu verändern.' },
  'Local verificable': { en: 'Verifiable local', it: 'Locale verificabile', de: 'Überprüfbar lokal' },
  'Explicación generativa': { en: 'Generative explanation', it: 'Spiegazione generativa', de: 'Generative Erklärung' },
  'Comprobando configuración de IA…': { en: 'Checking AI configuration…', it: 'Verifica configurazione IA…', de: 'KI-Konfiguration wird geprüft…' },
  'Contexto real': { en: 'Real context', it: 'Contesto reale', de: 'Realer Kontext' },
  'Sesión analizada': { en: 'Analysed session', it: 'Sessione analizzata', de: 'Analysierte Sitzung' },
  'Prueba sin título': { en: 'Untitled test', it: 'Test senza titolo', de: 'Test ohne Titel' },
  'Alcance de la respuesta': { en: 'Answer scope', it: 'Ambito della risposta', de: 'Antwortumfang' },
  'Una única sesión': { en: 'One session only', it: 'Una sola sessione', de: 'Nur eine Sitzung' },
  'Finaliza la captura para analizar todos sus datos.': { en: 'Finish capture to analyse all its data.', it: 'Termina l’acquisizione per analizzarne tutti i dati.', de: 'Beende die Aufzeichnung, um alle Daten zu analysieren.' },
  'Cargando el alcance de los datos…': { en: 'Loading data scope…', it: 'Caricamento ambito dati…', de: 'Datenumfang wird geladen…' },
  'Vehículo': { en: 'Vehicle', it: 'Veicolo', de: 'Fahrzeug' },
  'Cargando…': { en: 'Loading…', it: 'Caricamento…', de: 'Wird geladen…' },
  'Motivo guardado de la prueba': { en: 'Saved test reason', it: 'Motivo del test salvato', de: 'Gespeicherter Testgrund' },
  'Señales': { en: 'Signals', it: 'Segnali', de: 'Signale' },
  'Calidad': { en: 'Quality', it: 'Qualità', de: 'Qualität' },
  'Referencia del propio coche': { en: 'Vehicle’s own baseline', it: 'Riferimento del veicolo', de: 'Fahrzeugeigene Referenz' },
  'Aprendiendo': { en: 'Learning', it: 'Apprendimento', de: 'Lernphase' },
  'Resultado de sesión': { en: 'Session result', it: 'Risultato sessione', de: 'Sitzungsergebnis' },
  'Datos disponibles': { en: 'Available data', it: 'Dati disponibili', de: 'Verfügbare Daten' },
  'Sin señales válidas': { en: 'No valid signals', it: 'Nessun segnale valido', de: 'Keine gültigen Signale' },
  'Borrar conversación': { en: 'Clear conversation', it: 'Cancella conversazione', de: 'Gespräch löschen' },
  '¿Qué está mal en esta sesión?': { en: 'What is wrong in this session?', it: 'Cosa non va in questa sessione?', de: 'Was ist in dieser Sitzung auffällig?' },
  '¿Puedo seguir circulando?': { en: 'Can I keep driving?', it: 'Posso continuare a guidare?', de: 'Kann ich weiterfahren?' },
  'El coche da tirones al acelerar': { en: 'The car jerks under acceleration', it: 'L’auto strattona in accelerazione', de: 'Das Fahrzeug ruckelt beim Beschleunigen' },
  '¿Qué debería revisar primero?': { en: 'What should I check first?', it: 'Cosa dovrei controllare prima?', de: 'Was sollte ich zuerst prüfen?' },
  'Prepara un resumen para el taller': { en: 'Prepare a workshop summary', it: 'Prepara un riepilogo per l’officina', de: 'Erstelle eine Zusammenfassung für die Werkstatt' },
  'Captura en curso': { en: 'Capture in progress', it: 'Acquisizione in corso', de: 'Aufzeichnung läuft' },
  'Finaliza la prueba antes de preguntar. Así la respuesta utilizará la sesión completa y no un archivo parcial.': { en: 'Finish the test before asking. The answer will use the complete session rather than a partial file.', it: 'Termina il test prima di chiedere. La risposta userà la sessione completa e non un file parziale.', de: 'Beende den Test vor der Frage. Die Antwort verwendet dann die vollständige Sitzung statt einer Teildatei.' },
  'Explícame el problema como tú lo dirías': { en: 'Explain the problem in your own words', it: 'Spiega il problema con parole tue', de: 'Beschreibe das Problem mit eigenen Worten' },
  'Cruzando tu descripción con DTC, sensores y reglas…': { en: 'Comparing your description with DTCs, sensors and rules…', it: 'Confronto della descrizione con DTC, sensori e regole…', de: 'Beschreibung wird mit DTCs, Sensoren und Regeln abgeglichen…' },
  'Dictar síntoma': { en: 'Dictate symptom', it: 'Detta sintomo', de: 'Symptom diktieren' },
  'El reconocimiento de voz no está disponible en este equipo.': { en: 'Speech recognition is not available on this computer.', it: 'Il riconoscimento vocale non è disponibile su questo computer.', de: 'Spracherkennung ist auf diesem Computer nicht verfügbar.' },
  'No se pudo reconocer la voz.': { en: 'Speech could not be recognised.', it: 'Impossibile riconoscere la voce.', de: 'Sprache konnte nicht erkannt werden.' },
  'No se pudo cargar la sesión.': { en: 'Could not load the session.', it: 'Impossibile caricare la sessione.', de: 'Sitzung konnte nicht geladen werden.' },
  'No se pudo analizar la pregunta.': { en: 'Could not analyse the question.', it: 'Impossibile analizzare la domanda.', de: 'Frage konnte nicht analysiert werden.' },
  'Error consultando el asistente.': { en: 'Error querying the assistant.', it: 'Errore durante la consultazione dell’assistente.', de: 'Fehler bei der Assistentenanfrage.' },
  'Añadir vehículo al garaje': { en: 'Add vehicle to garage', it: 'Aggiungi veicolo al garage', de: 'Fahrzeug zur Garage hinzufügen' },
  'Alta rápida · Perfil ampliable': { en: 'Quick setup · Expandable profile', it: 'Configurazione rapida · Profilo espandibile', de: 'Schnelleinrichtung · Erweiterbares Profil' },
  'Podrás diagnosticarlo desde ahora y completar sus datos técnicos más adelante.': { en: 'You can diagnose it now and complete its technical data later.', it: 'Puoi diagnosticarlo subito e completare i dati tecnici in seguito.', de: 'Du kannst es sofort diagnostizieren und die technischen Daten später ergänzen.' },
  'Marca *': { en: 'Make *', it: 'Marca *', de: 'Marke *' },
  'Modelo *': { en: 'Model *', it: 'Modello *', de: 'Modell *' },
  'Año *': { en: 'Year *', it: 'Anno *', de: 'Baujahr *' },
  'Propulsión *': { en: 'Powertrain *', it: 'Propulsione *', de: 'Antrieb *' },
  'Gasolina': { en: 'Petrol', it: 'Benzina', de: 'Benzin' },
  'Diésel': { en: 'Diesel', it: 'Diesel', de: 'Diesel' },
  'Híbrido': { en: 'Hybrid', it: 'Ibrido', de: 'Hybrid' },
  'Híbrido enchufable': { en: 'Plug-in hybrid', it: 'Ibrido plug-in', de: 'Plug-in-Hybrid' },
  'Eléctrico': { en: 'Electric', it: 'Elettrico', de: 'Elektrisch' },
  'Versión o motor': { en: 'Version or engine', it: 'Versione o motore', de: 'Version oder Motor' },
  'Muy recomendable para distinguir motorizaciones del mismo año.': { en: 'Highly recommended to distinguish engines from the same year.', it: 'Molto consigliato per distinguere motori dello stesso anno.', de: 'Sehr empfohlen, um Motorvarianten desselben Baujahrs zu unterscheiden.' },
  'Apodo': { en: 'Nickname', it: 'Soprannome', de: 'Spitzname' },
  'Opcional · Ej. Mi coche diario': { en: 'Optional · E.g. My daily car', it: 'Facoltativo · Es. La mia auto quotidiana', de: 'Optional · Z. B. Mein Alltagsauto' },
  'Datos técnicos opcionales': { en: 'Optional technical data', it: 'Dati tecnici facoltativi', de: 'Optionale technische Daten' },
  'Si no los conoces, déjalos vacíos. La cobertura genérica seguirá disponible.': { en: 'Leave unknown fields empty. Generic coverage will remain available.', it: 'Lascia vuoti i campi sconosciuti. La copertura generica resterà disponibile.', de: 'Unbekannte Felder leer lassen. Die generische Abdeckung bleibt verfügbar.' },
  'Generación': { en: 'Generation', it: 'Generazione', de: 'Generation' },
  'Acabado / variante': { en: 'Trim / variant', it: 'Allestimento / variante', de: 'Ausstattung / Variante' },
  'Código de motor': { en: 'Engine code', it: 'Codice motore', de: 'Motorcode' },
  'Si figura en la documentación': { en: 'If stated in the documentation', it: 'Se indicato nella documentazione', de: 'Falls in den Unterlagen angegeben' },
  'Mercado': { en: 'Market', it: 'Mercato', de: 'Markt' },
  'Europa': { en: 'Europe', it: 'Europa', de: 'Europa' },
  'Estados Unidos': { en: 'United States', it: 'Stati Uniti', de: 'Vereinigte Staaten' },
  'Latinoamérica': { en: 'Latin America', it: 'America Latina', de: 'Lateinamerika' },
  'Otro': { en: 'Other', it: 'Altro', de: 'Andere' },
  'No hace falta introducir matrícula ni VIN para crear el vehículo.': { en: 'A licence plate or VIN is not required to create the vehicle.', it: 'Non serve inserire targa o VIN per creare il veicolo.', de: 'Kennzeichen oder VIN sind zum Anlegen des Fahrzeugs nicht erforderlich.' },
  'Cancelar': { en: 'Cancel', it: 'Annulla', de: 'Abbrechen' },
  'Guardando…': { en: 'Saving…', it: 'Salvataggio…', de: 'Speichern…' },
  'Añadir al garaje': { en: 'Add to garage', it: 'Aggiungi al garage', de: 'Zur Garage hinzufügen' },
  'Cerrar formulario': { en: 'Close form', it: 'Chiudi modulo', de: 'Formular schließen' },
  'No se pudo guardar el vehículo.': { en: 'Could not save the vehicle.', it: 'Impossibile salvare il veicolo.', de: 'Fahrzeug konnte nicht gespeichert werden.' },
  'Comparación antes / después': { en: 'Before / after comparison', it: 'Confronto prima / dopo', de: 'Vorher-/Nachher-Vergleich' },
  'La aplicación comprueba primero si ambas capturas se pueden comparar con rigor.': { en: 'The application first checks whether both captures can be compared reliably.', it: 'L’applicazione verifica prima se le acquisizioni sono confrontabili in modo rigoroso.', de: 'Die Anwendung prüft zuerst, ob beide Aufzeichnungen zuverlässig vergleichbar sind.' },
  'Antes': { en: 'Before', it: 'Prima', de: 'Vorher' },
  'Después': { en: 'After', it: 'Dopo', de: 'Nachher' },
  'Comparar': { en: 'Compare', it: 'Confronta', de: 'Vergleichen' },
  'Selecciona dos sesiones diferentes.': { en: 'Select two different sessions.', it: 'Seleziona due sessioni diverse.', de: 'Wähle zwei verschiedene Sitzungen.' },
  'No se pudieron comparar las sesiones.': { en: 'The sessions could not be compared.', it: 'Impossibile confrontare le sessioni.', de: 'Die Sitzungen konnten nicht verglichen werden.' },
  'Expediente Técnico y Registro de Reparaciones': { en: 'Technical file and repair history', it: 'Scheda tecnica e registro riparazioni', de: 'Technische Akte und Reparaturverlauf' },
  'Inventario completo de la ECU Volkswagen': { en: 'Complete Volkswagen ECU inventory', it: 'Inventario completo ECU Volkswagen', de: 'Vollständiges Volkswagen-ECU-Inventar' },
  'Leer ECU': { en: 'Read ECU', it: 'Leggi ECU', de: 'ECU lesen' },
  'Repetir inventario completo': { en: 'Repeat full inventory', it: 'Ripeti inventario completo', de: 'Vollständige Inventur wiederholen' },
  'Leyendo todos los bloques…': { en: 'Reading all blocks…', it: 'Lettura di tutti i blocchi…', de: 'Alle Blöcke werden gelesen…' },
  'Cobertura real:': { en: 'Real coverage:', it: 'Copertura reale:', de: 'Reale Abdeckung:' },
  'Solo usa capturas medidas, calidad ≥ 75% y sin alertas.': { en: 'Only measured captures with quality ≥ 75% and no alerts are used.', it: 'Usa solo acquisizioni misurate con qualità ≥ 75% e senza avvisi.', de: 'Es werden nur gemessene Aufzeichnungen mit Qualität ≥ 75 % und ohne Warnungen verwendet.' },
  'Exportar Copia ZIP': { en: 'Export ZIP backup', it: 'Esporta backup ZIP', de: 'ZIP-Sicherung exportieren' },
  'No hay intervenciones registradas en el historial de este vehículo.': { en: 'No work is recorded in this vehicle’s history.', it: 'Nessun intervento registrato nella cronologia del veicolo.', de: 'Im Verlauf dieses Fahrzeugs sind keine Arbeiten erfasst.' },
  '+ Registrar Nueva Reparación / Mantenimiento': { en: '+ Record new repair / maintenance', it: '+ Registra nuova riparazione / manutenzione', de: '+ Neue Reparatur / Wartung erfassen' },
  'Guardar Reparación': { en: 'Save repair', it: 'Salva riparazione', de: 'Reparatur speichern' },
  'Preparación real de monitores OBD para la ITV': { en: 'Actual OBD monitor readiness for inspection', it: 'Stato reale dei monitor OBD per la revisione', de: 'Tatsächliche OBD-Monitorbereitschaft für die HU' },
  'Actualizar monitores': { en: 'Refresh monitors', it: 'Aggiorna monitor', de: 'Monitore aktualisieren' },
  'Conecta el vehículo para consultar los monitores reales.': { en: 'Connect the vehicle to read the actual monitors.', it: 'Collega il veicolo per leggere i monitor reali.', de: 'Fahrzeug verbinden, um die tatsächlichen Monitore zu lesen.' },
  'Esta lectura OBD no sustituye la inspección física ni garantiza superar la ITV.': { en: 'This OBD reading does not replace a physical inspection or guarantee a pass.', it: 'Questa lettura OBD non sostituisce l’ispezione fisica né garantisce il superamento della revisione.', de: 'Diese OBD-Auslesung ersetzt keine physische Prüfung und garantiert kein Bestehen der HU.' },
  'Diagnóstico a bordo en Modo 06': { en: 'On-board diagnostics in Mode 06', it: 'Diagnostica di bordo in Modalità 06', de: 'On-Board-Diagnose in Modus 06' },
  'Leyendo Modo 06…': { en: 'Reading Mode 06…', it: 'Lettura Modalità 06…', de: 'Modus 06 wird gelesen…' },
  'Actualizar': { en: 'Refresh', it: 'Aggiorna', de: 'Aktualisieren' },
  'Esta pantalla no existe': { en: 'This page does not exist', it: 'Questa pagina non esiste', de: 'Diese Seite existiert nicht' },
  'Vuelve al cuadro de diagnóstico para continuar trabajando con el vehículo.': { en: 'Return to the diagnostic dashboard to continue working with the vehicle.', it: 'Torna al quadro diagnostico per continuare a lavorare sul veicolo.', de: 'Kehre zur Diagnoseübersicht zurück, um mit dem Fahrzeug weiterzuarbeiten.' },
  'Volver al diagnóstico': { en: 'Return to diagnostics', it: 'Torna alla diagnostica', de: 'Zur Diagnose zurückkehren' },
  'Finaliza una sesión con datos válidos para explicar el problema con tus propias palabras.': { en: 'Finish a session with valid data to describe the problem in your own words.', it: 'Termina una sessione con dati validi per descrivere il problema con parole tue.', de: 'Beende eine Sitzung mit gültigen Daten, um das Problem mit eigenen Worten zu beschreiben.' },
  'Esta sesión contiene datos simulados.': { en: 'This session contains simulated data.', it: 'Questa sessione contiene dati simulati.', de: 'Diese Sitzung enthält simulierte Daten.' },
  'Por ejemplo: “al acelerar en tercera da un tirón y pierde fuerza”. Usaré únicamente la sesión indicada en el panel de contexto.': { en: 'For example: “it jerks and loses power when accelerating in third gear”. I will only use the session shown in the context panel.', it: 'Ad esempio: “accelerando in terza strattona e perde potenza”. Userò solo la sessione indicata nel pannello del contesto.', de: 'Zum Beispiel: „Beim Beschleunigen im dritten Gang ruckelt es und verliert Leistung“. Ich verwende nur die im Kontext angezeigte Sitzung.' },
  'Intro para enviar · Mayús+Intro para nueva línea': { en: 'Enter to send · Shift+Enter for a new line', it: 'Invio per inviare · Maiusc+Invio per una nuova riga', de: 'Eingabetaste zum Senden · Umschalt+Eingabe für neue Zeile' },
  'Las evidencias de la última respuesta aparecerán aquí con sus valores exactos.': { en: 'Evidence from the latest answer will appear here with its exact values.', it: 'Le evidenze dell’ultima risposta appariranno qui con i valori esatti.', de: 'Die Belege der letzten Antwort erscheinen hier mit ihren exakten Werten.' },
  'Datos que faltan': { en: 'Missing data', it: 'Dati mancanti', de: 'Fehlende Daten' },
  'Base exacta de esta respuesta': { en: 'Exact basis for this answer', it: 'Base esatta di questa risposta', de: 'Exakte Grundlage dieser Antwort' },
  'Ver todo el contexto utilizado': { en: 'View all context used', it: 'Vedi tutto il contesto utilizzato', de: 'Gesamten verwendeten Kontext anzeigen' },
  'Cómo avanzar sin cambiar piezas a ciegas': { en: 'How to proceed without replacing parts blindly', it: 'Come procedere senza sostituire pezzi alla cieca', de: 'So gehst du weiter vor, ohne Teile auf Verdacht zu tauschen' },
  'Siguiente prueba recomendada': { en: 'Next recommended test', it: 'Prossimo test consigliato', de: 'Nächster empfohlener Test' },
  'MONITOR DEL BUS': { en: 'BUS MONITOR', it: 'MONITOR DEL BUS', de: 'BUS-MONITOR' },
  'DATOS EN DIRECTO': { en: 'LIVE DATA', it: 'DATI IN TEMPO REALE', de: 'LIVE-DATEN' },
  'Profundidad del resultado': { en: 'Result detail level', it: 'Livello di dettaglio del risultato', de: 'Detailtiefe des Ergebnisses' },
  'Empieza por la conclusión y abre solo el detalle que necesites.': { en: 'Start with the conclusion and open only the details you need.', it: 'Inizia dalla conclusione e apri solo i dettagli necessari.', de: 'Beginne mit dem Fazit und öffne nur die benötigten Details.' },
  'Consumo medio del trayecto': { en: 'Average trip consumption', it: 'Consumo medio del viaggio', de: 'Durchschnittlicher Fahrtverbrauch' },
  'Diagnóstico específico de consumo diésel': { en: 'Diesel consumption diagnosis', it: 'Diagnosi specifica del consumo diesel', de: 'Spezifische Diesel-Verbrauchsdiagnose' },
  'Comprobación local de monitores del sistema de diagnóstico': { en: 'Local diagnostic-system monitor check', it: 'Controllo locale dei monitor del sistema diagnostico', de: 'Lokale Prüfung der Diagnosesystem-Monitore' },
  'Códigos DTC de Emisiones': { en: 'Emissions DTCs', it: 'DTC delle emissioni', de: 'Emissions-DTCs' },
  'Sin lectura verificable': { en: 'No verifiable reading', it: 'Nessuna lettura verificabile', de: 'Kein verifizierbarer Messwert' },
  'Forma de trabajo': { en: 'Working mode', it: 'Modalità di lavoro', de: 'Arbeitsmodus' },
  'Referencia histórica del vehículo': { en: 'Vehicle history baseline', it: 'Riferimento storico del veicolo', de: 'Historische Fahrzeugreferenz' },
  'vLinker FS y cobertura de la aplicación': { en: 'vLinker FS and application coverage', it: 'vLinker FS e copertura dell’applicazione', de: 'vLinker FS und Anwendungsabdeckung' },
  'Prueba reproducible': { en: 'Reproducible test', it: 'Test riproducibile', de: 'Reproduzierbarer Test' },
  'Mismo protocolo, condición y origen de datos.': { en: 'Same protocol, condition and data source.', it: 'Stesso protocollo, condizione e origine dati.', de: 'Gleiches Protokoll, gleicher Zustand und gleiche Datenquelle.' },
  'Inicia una prueba guiada y aparecerá aquí al finalizar.': { en: 'Start a guided test and it will appear here when finished.', it: 'Avvia un test guidato e apparirà qui al termine.', de: 'Starte einen geführten Test; nach Abschluss erscheint er hier.' },
  'Estado del motor': { en: 'Engine condition', it: 'Stato del motore', de: 'Motorzustand' },
  'Prueba recomendada': { en: 'Recommended test', it: 'Test consigliato', de: 'Empfohlener Test' },
  'Esperando el inicio de la captura // Bus de datos en reposo': { en: 'Waiting for capture to start // Data bus idle', it: 'In attesa dell’avvio dell’acquisizione // Bus dati inattivo', de: 'Warten auf Aufzeichnungsstart // Datenbus inaktiv' },
  'Selecciona hasta 4 canales · cada canal conserva su propia escala y comparte el mismo eje temporal': { en: 'Select up to 4 channels · each keeps its own scale and shares the same time axis', it: 'Seleziona fino a 4 canali · ciascuno mantiene la propria scala e condivide lo stesso asse temporale', de: 'Wähle bis zu 4 Kanäle · jeder behält seine eigene Skala und nutzt dieselbe Zeitachse' },
  'Sistema de inyección': { en: 'Injection system', it: 'Sistema di iniezione', de: 'Einspritzsystem' },
  'Inyector-bomba // sin rail common-rail': { en: 'Unit injector // no common rail', it: 'Iniettore-pompa // senza common rail', de: 'Pumpe-Düse // kein Common Rail' },
  'Estado del control de mezcla': { en: 'Mixture-control status', it: 'Stato del controllo miscela', de: 'Status der Gemischregelung' },
  'Estado eléctrico / BIP de inyectores': { en: 'Injector electrical / BIP status', it: 'Stato elettrico / BIP degli iniettori', de: 'Elektrischer / BIP-Status der Injektoren' },
  'Estado de regeneración': { en: 'Regeneration status', it: 'Stato della rigenerazione', de: 'Regenerationsstatus' },
  'Inicio': { en: 'Start', it: 'Inizio', de: 'Beginn' },
  'lecturas': { en: 'readings', it: 'letture', de: 'Messwerte' },
  'Estado del enlace OBD': { en: 'OBD link status', it: 'Stato del collegamento OBD', de: 'OBD-Verbindungsstatus' },
  'Revisar': { en: 'Check', it: 'Controllare', de: 'Prüfen' },
  'Sin datos': { en: 'No data', it: 'Nessun dato', de: 'Keine Daten' },
  'Validando el flujo de datos de la ECU…': { en: 'Validating ECU data flow…', it: 'Validazione del flusso dati ECU…', de: 'ECU-Datenstrom wird geprüft…' },
  '✅ SIN IMPEDIMENTOS OBD EVIDENTES': { en: '✅ NO OBVIOUS OBD BLOCKERS', it: '✅ NESSUN IMPEDIMENTO OBD EVIDENTE', de: '✅ KEINE OFFENSICHTLICHEN OBD-HINDERNISSE' },
  'No se pudo completar el inventario de la ECU.': { en: 'The ECU inventory could not be completed.', it: 'Impossibile completare l’inventario ECU.', de: 'Die ECU-Inventur konnte nicht abgeschlossen werden.' },
  'No se pudo completar el inventario.': { en: 'The inventory could not be completed.', it: 'Impossibile completare l’inventario.', de: 'Die Inventur konnte nicht abgeschlossen werden.' },
  'Aún no hay suficientes sesiones verificables.': { en: 'There are not enough verifiable sessions yet.', it: 'Non ci sono ancora abbastanza sessioni verificabili.', de: 'Es gibt noch nicht genügend verifizierbare Sitzungen.' },
  'Sin clasificar': { en: 'Unclassified', it: 'Non classificato', de: 'Nicht klassifiziert' },
  'Capturando datos': { en: 'Capturing data', it: 'Acquisizione dati', de: 'Daten werden aufgezeichnet' },
  'No se pudo leer la ECU.': { en: 'The ECU could not be read.', it: 'Impossibile leggere la ECU.', de: 'Die ECU konnte nicht ausgelesen werden.' },
  'NO DISPONIBLE': { en: 'UNAVAILABLE', it: 'NON DISPONIBILE', de: 'NICHT VERFÜGBAR' },
  'Condición del motor distinta': { en: 'Different engine condition', it: 'Condizione motore diversa', de: 'Abweichender Motorzustand' },
  'Calidad limitada': { en: 'Limited quality', it: 'Qualità limitata', de: 'Eingeschränkte Qualität' },
  'No se pudo comunicar con el analizador local.': { en: 'Could not communicate with the local analyser.', it: 'Impossibile comunicare con l’analizzatore locale.', de: 'Keine Verbindung zum lokalen Analysemodul.' },
  'Comprobando…': { en: 'Checking…', it: 'Verifica…', de: 'Prüfung…' },
  'Comparar con rigor': { en: 'Compare reliably', it: 'Confronta con rigore', de: 'Zuverlässig vergleichen' },
  'Con error': { en: 'With error', it: 'Con errore', de: 'Fehlerhaft' },
  'Histórico sin identificar': { en: 'Unidentified history', it: 'Storico non identificato', de: 'Nicht zugeordneter Verlauf' },
  'Sin estado informado': { en: 'No status reported', it: 'Nessuno stato comunicato', de: 'Kein Status gemeldet' },
  'Bucle abierto: motor frío': { en: 'Open loop: cold engine', it: 'Ciclo aperto: motore freddo', de: 'Offener Regelkreis: Motor kalt' },
  'Bucle cerrado con fallo de realimentación': { en: 'Closed loop with feedback fault', it: 'Ciclo chiuso con errore di retroazione', de: 'Geschlossener Regelkreis mit Rückkopplungsfehler' },
  'La ECU no respondió': { en: 'The ECU did not respond', it: 'La ECU non ha risposto', de: 'Die ECU hat nicht geantwortet' },
  'Lectura rechazada por la ECU': { en: 'Reading rejected by the ECU', it: 'Lettura rifiutata dalla ECU', de: 'Messwert von der ECU abgelehnt' },
  'Sin comprobar': { en: 'Not checked', it: 'Non verificato', de: 'Nicht geprüft' },
  'Sin fallos BIP detectados por la ECU': { en: 'No BIP faults detected by the ECU', it: 'Nessun guasto BIP rilevato dalla ECU', de: 'Keine BIP-Fehler von der ECU erkannt' },
  'Revoluciones del motor': { en: 'Engine speed', it: 'Regime motore', de: 'Motordrehzahl' },
  'Carga del motor': { en: 'Engine load', it: 'Carico motore', de: 'Motorlast' },
  'Aceite del motor': { en: 'Engine oil', it: 'Olio motore', de: 'Motoröl' },
  'Calculado desde mg/str y RPM (motor 4 cilindros)': { en: 'Calculated from mg/str and RPM (4-cylinder engine)', it: 'Calcolato da mg/ciclo e RPM (motore 4 cilindri)', de: 'Aus mg/Hub und Drehzahl berechnet (4-Zylinder-Motor)' },
  'Trazabilidad de los datos': { en: 'Data traceability', it: 'Tracciabilità dei dati', de: 'Datennachverfolgbarkeit' },
  'Sin sesión activa': { en: 'No active session', it: 'Nessuna sessione attiva', de: 'Keine aktive Sitzung' },
  'No se puede comunicar con el backend local.': { en: 'Cannot communicate with the local backend.', it: 'Impossibile comunicare con il backend locale.', de: 'Keine Verbindung zum lokalen Backend.' },
  'ECU detectada. Identificando la centralita Volkswagen con lecturas seguras…': { en: 'ECU detected. Identifying the Volkswagen control unit with safe readings…', it: 'ECU rilevata. Identificazione della centralina Volkswagen con letture sicure…', de: 'ECU erkannt. Volkswagen-Steuergerät wird mit sicheren Abfragen identifiziert…' },
  'Adaptador conectado; no se pudo completar la identificación Volkswagen.': { en: 'Adapter connected; Volkswagen identification could not be completed.', it: 'Adattatore collegato; impossibile completare l’identificazione Volkswagen.', de: 'Adapter verbunden; Volkswagen-Identifizierung konnte nicht abgeschlossen werden.' },
  'La prevalidación no se ha superado.': { en: 'Pre-validation did not pass.', it: 'La prevalidazione non è stata superata.', de: 'Die Vorprüfung wurde nicht bestanden.' },
  'En espera': { en: 'Standby', it: 'In attesa', de: 'Bereit' },
  'Controles de sesión': { en: 'Session controls', it: 'Controlli della sessione', de: 'Sitzungssteuerung' },
  'Módulos principales': { en: 'Main modules', it: 'Moduli principali', de: 'Hauptmodule' },
  'Inicio rápido': { en: 'Quick start', it: 'Avvio rapido', de: 'Schnellstart' },
  'Instrumentación de telemetría': { en: 'Telemetry instruments', it: 'Strumentazione telemetrica', de: 'Telemetrieinstrumente' },
  'Ej.: al adelantar en cuarta, entre 2.000 y 2.500 rpm…': { en: 'E.g. when overtaking in fourth gear, between 2,000 and 2,500 rpm…', it: 'Es. durante un sorpasso in quarta, tra 2.000 e 2.500 giri/min…', de: 'Z. B. beim Überholen im vierten Gang zwischen 2.000 und 2.500 U/min…' },
  'Comprobaremos las señales disponibles de forma ordenada.': { en: 'We will check the available signals in a structured order.', it: 'Controlleremo i segnali disponibili in modo ordinato.', de: 'Wir prüfen die verfügbaren Signale in einer klaren Reihenfolge.' },
  'Preparando perfiles disponibles…': { en: 'Preparing available profiles…', it: 'Preparazione dei profili disponibili…', de: 'Verfügbare Profile werden vorbereitet…' },
  'Velocidad del vehículo': { en: 'Vehicle speed', it: 'Velocità del veicolo', de: 'Fahrzeuggeschwindigkeit' },
  'Pedal del acelerador': { en: 'Accelerator pedal', it: 'Pedale dell’acceleratore', de: 'Fahrpedal' },
  'Pendiente de comprobar': { en: 'Pending verification', it: 'In attesa di verifica', de: 'Prüfung ausstehend' },
  'DIAGNÓSTICO OBD-II LOCAL': { en: 'LOCAL OBD-II DIAGNOSTICS', it: 'DIAGNOSTICA OBD-II LOCALE', de: 'LOKALE OBD-II-DIAGNOSE' },
  'Cuadro de instrumentación local para telemetría OBD-II, diagnóstico determinista y análisis asistido.': { en: 'Local dashboard for OBD-II telemetry, deterministic diagnostics and assisted analysis.', it: 'Cruscotto locale per telemetria OBD-II, diagnostica deterministica e analisi assistita.', de: 'Lokales Dashboard für OBD-II-Telemetrie, deterministische Diagnose und assistierte Analyse.' },
  'identificación pendiente': { en: 'identification pending', it: 'identificazione in attesa', de: 'Identifizierung ausstehend' },
  'lecturas ·': { en: 'readings ·', it: 'letture ·', de: 'Messwerte ·' },
  'Captura detenida automáticamente': { en: 'Capture stopped automatically', it: 'Acquisizione arrestata automaticamente', de: 'Aufzeichnung automatisch gestoppt' },
  'Datos técnicos': { en: 'Technical data', it: 'Dati tecnici', de: 'Technische Daten' },
  'Lecturas válidas': { en: 'Valid readings', it: 'Letture valide', de: 'Gültige Messwerte' },
  'Cronología de anomalías y alertas': { en: 'Anomaly and alert timeline', it: 'Cronologia di anomalie e avvisi', de: 'Zeitverlauf von Anomalien und Warnungen' },
  'Leyendo el bus…': { en: 'Reading the bus…', it: 'Lettura del bus…', de: 'Bus wird ausgelesen…' },
  'El estado OBD de emisiones refleja únicamente la información digital leída de la ECU. Esta comprobación': { en: 'The OBD emissions status only reflects digital information read from the ECU. This check', it: 'Lo stato OBD delle emissioni riflette solo le informazioni digitali lette dalla ECU. Questo controllo', de: 'Der OBD-Emissionsstatus zeigt nur die aus der ECU gelesenen digitalen Informationen. Diese Prüfung' },
  ', ya que la inspección oficial incluye comprobaciones físicas de opacidad/gases, estado mecánico del escape e inspección visual.': { en: ', because the official inspection also includes physical opacity/gas checks, exhaust condition and a visual inspection.', it: ', poiché la revisione ufficiale comprende anche controlli fisici di opacità/gas, stato meccanico dello scarico e ispezione visiva.', de: ', da die amtliche Prüfung auch physische Abgas-/Trübungsmessungen, den mechanischen Zustand des Auspuffs und eine Sichtprüfung umfasst.' },
  'Fotograma congelado de la avería (': { en: 'Fault freeze frame (', it: 'Freeze frame del guasto (', de: 'Fehler-Freeze-Frame (' },
  'Valores capturados por la ECU en el instante en que se registró la avería.': { en: 'Values captured by the ECU when the fault was recorded.', it: 'Valori acquisiti dalla ECU quando è stato registrato il guasto.', de: 'Von der ECU beim Speichern des Fehlers erfasste Werte.' },
  'La ECU no ha proporcionado un fotograma congelado verificable para este código. No se muestran valores de ejemplo.': { en: 'The ECU did not provide a verifiable freeze frame for this code. No sample values are shown.', it: 'La ECU non ha fornito un freeze frame verificabile per questo codice. Non vengono mostrati valori di esempio.', de: 'Die ECU hat für diesen Code keinen verifizierbaren Freeze-Frame geliefert. Es werden keine Beispielwerte angezeigt.' },
  'Combustible, mezcla y emisiones': { en: 'Fuel, mixture and emissions', it: 'Carburante, miscela ed emissioni', de: 'Kraftstoff, Gemisch und Emissionen' },
  'OBD-II genérico, DTC, freeze frame y Modo 06 real preparados. Los PIDs OEM propietarios requieren paquetes verificados específicos.': { en: 'Generic OBD-II, DTCs, freeze frames and real Mode 06 are ready. Proprietary OEM PIDs require specific verified packages.', it: 'OBD-II generico, DTC, freeze frame e Modalità 06 reale sono pronti. I PID OEM proprietari richiedono pacchetti verificati specifici.', de: 'Generisches OBD-II, DTCs, Freeze-Frames und echter Modus 06 sind bereit. Proprietäre OEM-PIDs benötigen spezifische verifizierte Pakete.' },
  'Comprueba uno por uno los bloques documentados y conserva la respuesta bruta. Una métrica solo figura como confirmada si este coche la ha devuelto realmente.': { en: 'Checks documented blocks one by one and keeps the raw response. A metric is only confirmed when this car actually returns it.', it: 'Controlla uno a uno i blocchi documentati e conserva la risposta grezza. Una metrica è confermata solo se questa auto la restituisce realmente.', de: 'Prüft dokumentierte Blöcke einzeln und bewahrt die Rohantwort auf. Ein Messwert gilt nur als bestätigt, wenn dieses Fahrzeug ihn tatsächlich liefert.' },
  '“No disponible” significa que la ECU no devolvió ese campo o que todavía no se ha comprobado; no se sustituye por un valor calculado o simulado.': { en: '“Unavailable” means the ECU did not return that field or it has not been checked yet; it is never replaced with a calculated or simulated value.', it: '“Non disponibile” significa che la ECU non ha restituito quel campo o non è ancora stato verificato; non viene sostituito con un valore calcolato o simulato.', de: '„Nicht verfügbar“ bedeutet, dass die ECU dieses Feld nicht geliefert hat oder es noch nicht geprüft wurde; es wird nicht durch einen berechneten oder simulierten Wert ersetzt.' },
  'Descripción (ej. Cambio de Bujías y Limpieza de MAF)': { en: 'Description (e.g. spark-plug replacement and MAF cleaning)', it: 'Descrizione (es. sostituzione candele e pulizia MAF)', de: 'Beschreibung (z. B. Zündkerzenwechsel und MAF-Reinigung)' },
  'Notas (ej. Bujías NGK Iridium de 0.8mm)': { en: 'Notes (e.g. NGK Iridium 0.8 mm spark plugs)', it: 'Note (es. candele NGK Iridium da 0,8 mm)', de: 'Notizen (z. B. NGK-Iridium-Zündkerzen 0,8 mm)' },
  'señales objetivo': { en: 'target signals', it: 'segnali obiettivo', de: 'Zielsignale' },
  'El conductor no debe manipular la pantalla. Usa un acompañante y respeta siempre la vía y los límites legales.': { en: 'The driver must not operate the screen. Use a passenger and always obey road rules and speed limits.', it: 'Il conducente non deve usare lo schermo. Affidati a un passeggero e rispetta sempre la strada e i limiti di velocità.', de: 'Der Fahrer darf den Bildschirm nicht bedienen. Nutze einen Beifahrer und beachte stets Verkehrsregeln und Tempolimits.' },
  'FUERA DE LÍMITES': { en: 'OUT OF RANGE', it: 'FUORI LIMITE', de: 'AUSSERHALB DES GRENZWERTS' },
  '% de media': { en: '% average', it: '% di media', de: '% Mittelwert' },
  '% de variabilidad': { en: '% variability', it: '% di variabilità', de: '% Streuung' },
  'Sesión de diagnóstico': { en: 'Diagnostic session', it: 'Sessione diagnostica', de: 'Diagnosesitzung' },
  'Evolución temporal de las señales seleccionadas': { en: 'Selected signal timeline', it: 'Andamento temporale dei segnali selezionati', de: 'Zeitlicher Verlauf der ausgewählten Signale' },
  'Mariposa de admisión': { en: 'Intake throttle', it: 'Farfalla di aspirazione', de: 'Drosselklappe' },
  'Aire de admisión (IAT)': { en: 'Intake air (IAT)', it: 'Aria di aspirazione (IAT)', de: 'Ansaugluft (IAT)' },
  'Caudal de aire (MAF)': { en: 'Air flow (MAF)', it: 'Portata aria (MAF)', de: 'Luftmassenstrom (MAF)' },
  'Presión del colector (MAP)': { en: 'Manifold pressure (MAP)', it: 'Pressione collettore (MAP)', de: 'Saugrohrdruck (MAP)' },
  'Presión absoluta real del colector, medida por la ECU': { en: 'Actual absolute manifold pressure measured by the ECU', it: 'Pressione assoluta reale del collettore misurata dalla ECU', de: 'Von der ECU gemessener tatsächlicher absoluter Saugrohrdruck' },
  'Presión del rail real': { en: 'Actual rail pressure', it: 'Pressione rail reale', de: 'Ist-Raildruck' },
  'Presión del rail solicitada': { en: 'Requested rail pressure', it: 'Pressione rail richiesta', de: 'Soll-Raildruck' },
  'Cantidad de inyección': { en: 'Injection quantity', it: 'Quantità di iniezione', de: 'Einspritzmenge' },
  'Duración de inyección': { en: 'Injection duration', it: 'Durata di iniezione', de: 'Einspritzdauer' },
  'Consumo instantáneo calculado': { en: 'Calculated instantaneous consumption', it: 'Consumo istantaneo calcolato', de: 'Berechneter Momentanverbrauch' },
  'Avance de inyección': { en: 'Injection timing', it: 'Anticipo di iniezione', de: 'Einspritzzeitpunkt' },
  'Torsión de distribución': { en: 'Camshaft torsion value', it: 'Valore di torsione distribuzione', de: 'Nockenwellen-Synchronisationswert' },
  'Carga de hollín': { en: 'Soot load', it: 'Carico di fuliggine', de: 'Rußbeladung' },
  'Módulo de control': { en: 'Control module', it: 'Centralina di controllo', de: 'Steuergerät' },
  'Alimentación del adaptador OBD': { en: 'OBD adapter supply', it: 'Alimentazione adattatore OBD', de: 'OBD-Adapterversorgung' },
  'Batería y alternador': { en: 'Battery and alternator', it: 'Batteria e alternatore', de: 'Batterie und Lichtmaschine' },
  'Termostato y refrigeración': { en: 'Thermostat and cooling', it: 'Termostato e raffreddamento', de: 'Thermostat und Kühlung' },
  'Estabilidad de Ralentí': { en: 'Idle stability', it: 'Stabilità del minimo', de: 'Leerlaufstabilität' },
  'Turbo y admisión': { en: 'Turbo and intake', it: 'Turbo e aspirazione', de: 'Turbo und Ansaugung' },
  'Consumo e inyección': { en: 'Consumption and injection', it: 'Consumo e iniezione', de: 'Verbrauch und Einspritzung' },
  'Emisiones / ITV': { en: 'Emissions / inspection', it: 'Emissioni / revisione', de: 'Emissionen / HU' },
  'Recorrido reproducible para evaluar conexión, ralentí, calentamiento, carga y desaceleración.': { en: 'Reproducible route to assess connection, idle, warm-up, load and deceleration.', it: 'Percorso riproducibile per valutare connessione, minimo, riscaldamento, carico e decelerazione.', de: 'Reproduzierbare Fahrt zur Bewertung von Verbindung, Leerlauf, Warmlauf, Last und Verzögerung.' },
  'Comprueba caída de tensión, recuperación y estabilidad del sistema de carga.': { en: 'Checks voltage drop, recovery and charging-system stability.', it: 'Controlla caduta di tensione, recupero e stabilità del sistema di carica.', de: 'Prüft Spannungsabfall, Erholung und Stabilität des Ladesystems.' },
  'Evalúa velocidad de calentamiento, temperatura máxima y estabilidad térmica.': { en: 'Assesses warm-up rate, maximum temperature and thermal stability.', it: 'Valuta velocità di riscaldamento, temperatura massima e stabilità termica.', de: 'Bewertet Aufwärmgeschwindigkeit, Maximaltemperatur und thermische Stabilität.' },
  'Analiza oscilaciones de RPM, carga calculada y correcciones de mezcla en parado.': { en: 'Analyses RPM fluctuations, calculated load and mixture corrections while stationary.', it: 'Analizza oscillazioni dei giri, carico calcolato e correzioni della miscela da fermo.', de: 'Analysiert Drehzahlschwankungen, berechnete Last und Gemischkorrekturen im Stand.' },
  'Relaciona acelerador, carga, MAF y MAP durante una aceleración segura.': { en: 'Correlates accelerator, load, MAF and MAP during safe acceleration.', it: 'Mette in relazione acceleratore, carico, MAF e MAP durante un’accelerazione sicura.', de: 'Setzt Fahrpedal, Last, MAF und MAP bei sicherer Beschleunigung in Beziehung.' },
  'Diagnóstico dirigido del consumo: calentamiento, cantidad y duración de inyección, sincronización, inyectores, aire, EGR y turbo.': { en: 'Targeted consumption diagnosis: warm-up, injection quantity and duration, timing, injectors, air, EGR and turbo.', it: 'Diagnosi mirata dei consumi: riscaldamento, quantità e durata d’iniezione, fasatura, iniettori, aria, EGR e turbo.', de: 'Gezielte Verbrauchsdiagnose: Warmlauf, Einspritzmenge und -dauer, Synchronisation, Injektoren, Luft, EGR und Turbo.' },
  'Captura señales y códigos útiles para evaluar la preparación OBD previa a ITV.': { en: 'Captures useful signals and codes to assess OBD readiness before inspection.', it: 'Acquisisce segnali e codici utili per valutare la preparazione OBD prima della revisione.', de: 'Erfasst nützliche Signale und Codes zur Bewertung der OBD-Bereitschaft vor der HU.' },
  'Registrador multicanal // señales sincronizadas': { en: 'Multichannel logger // synchronised signals', it: 'Registratore multicanale // segnali sincronizzati', de: 'Mehrkanal-Aufzeichnung // synchronisierte Signale' },
  'Mantén una conducción segura y estable.': { en: 'Maintain safe, steady driving.', it: 'Mantieni una guida sicura e regolare.', de: 'Fahre sicher und gleichmäßig.' },
  'Ralentí estable': { en: 'Stable idle', it: 'Minimo stabile', de: 'Stabiler Leerlauf' },
  'Mantén el coche parado y sin acelerar durante 60 segundos.': { en: 'Keep the car stationary without accelerating for 60 seconds.', it: 'Mantieni l’auto ferma senza accelerare per 60 secondi.', de: 'Fahrzeug 60 Sekunden im Stand ohne Gasgeben halten.' },
  'Circulación suave': { en: 'Gentle driving', it: 'Guida dolce', de: 'Sanfte Fahrt' },
  'Inicia la marcha de forma progresiva y evita aceleraciones bruscas.': { en: 'Set off progressively and avoid sudden acceleration.', it: 'Parti progressivamente ed evita accelerazioni brusche.', de: 'Fahre gleichmäßig an und vermeide starkes Beschleunigen.' },
  'Velocidad constante': { en: 'Constant speed', it: 'Velocità costante', de: 'Konstante Geschwindigkeit' },
  'Mantén una velocidad estable durante aproximadamente 2 minutos.': { en: 'Maintain a steady speed for approximately 2 minutes.', it: 'Mantieni una velocità stabile per circa 2 minuti.', de: 'Halte etwa 2 Minuten lang eine konstante Geschwindigkeit.' },
  'Carga controlada': { en: 'Controlled load', it: 'Carico controllato', de: 'Kontrollierte Last' },
  'Acelera progresivamente en un lugar seguro, sin superar los límites legales.': { en: 'Accelerate progressively in a safe place without exceeding legal limits.', it: 'Accelera progressivamente in un luogo sicuro senza superare i limiti di legge.', de: 'Beschleunige an einem sicheren Ort gleichmäßig, ohne gesetzliche Grenzen zu überschreiten.' },
  'Retención': { en: 'Overrun', it: 'Rilascio', de: 'Schubbetrieb' },
  'Suelta el acelerador y deja que el vehículo desacelere con normalidad.': { en: 'Release the accelerator and let the vehicle decelerate normally.', it: 'Rilascia l’acceleratore e lascia decelerare normalmente il veicolo.', de: 'Nimm den Fuß vom Gas und lasse das Fahrzeug normal verzögern.' },
  'Ralentí final': { en: 'Final idle', it: 'Minimo finale', de: 'Abschließender Leerlauf' },
  'Detente con seguridad y mantén 60 segundos de ralentí antes de finalizar.': { en: 'Stop safely and maintain idle for 60 seconds before finishing.', it: 'Fermati in sicurezza e mantieni il minimo per 60 secondi prima di terminare.', de: 'Sicher anhalten und vor dem Abschluss 60 Sekunden im Leerlauf laufen lassen.' },
  'Ralentí sin consumidores': { en: 'Idle without electrical loads', it: 'Minimo senza utenze elettriche', de: 'Leerlauf ohne Verbraucher' },
  'Mantén el motor al ralentí con luces y climatización apagados.': { en: 'Keep the engine idling with lights and climate control off.', it: 'Mantieni il motore al minimo con luci e climatizzazione spenti.', de: 'Motor bei ausgeschaltetem Licht und Klimasystem im Leerlauf laufen lassen.' },
  'Carga eléctrica': { en: 'Electrical load', it: 'Carico elettrico', de: 'Elektrische Last' },
  'Enciende luces, luneta térmica y ventilador durante un minuto.': { en: 'Switch on the lights, heated rear window and blower for one minute.', it: 'Accendi luci, lunotto termico e ventola per un minuto.', de: 'Licht, Heckscheibenheizung und Gebläse eine Minute lang einschalten.' },
  'Recuperación': { en: 'Recovery', it: 'Recupero', de: 'Erholung' },
  'Apaga los consumidores y observa la recuperación de tensión.': { en: 'Switch off the loads and observe voltage recovery.', it: 'Spegni le utenze e osserva il recupero della tensione.', de: 'Verbraucher ausschalten und die Spannungserholung beobachten.' },
  'Inicio térmico': { en: 'Thermal start', it: 'Avvio termico', de: 'Thermischer Start' },
  'Registra la temperatura inicial con el motor frío o templado.': { en: 'Record the initial temperature with the engine cold or warm.', it: 'Registra la temperatura iniziale con il motore freddo o tiepido.', de: 'Anfangstemperatur bei kaltem oder lauwarmem Motor aufzeichnen.' },
  'Calentamiento suave': { en: 'Gentle warm-up', it: 'Riscaldamento dolce', de: 'Schonendes Warmlaufen' },
  'Circula sin carga elevada hasta alcanzar temperatura de servicio.': { en: 'Drive without high load until operating temperature is reached.', it: 'Guida senza carichi elevati fino alla temperatura di esercizio.', de: 'Ohne hohe Last fahren, bis Betriebstemperatur erreicht ist.' },
  'Estabilización': { en: 'Stabilisation', it: 'Stabilizzazione', de: 'Stabilisierung' },
  'Mantén circulación constante y observa si la temperatura se estabiliza.': { en: 'Maintain steady driving and observe whether the temperature stabilises.', it: 'Mantieni una guida costante e osserva se la temperatura si stabilizza.', de: 'Gleichmäßig fahren und beobachten, ob sich die Temperatur stabilisiert.' },
  'Referencia': { en: 'Baseline', it: 'Riferimento', de: 'Referenz' },
  'Mantén velocidad y carga constantes.': { en: 'Maintain constant speed and load.', it: 'Mantieni velocità e carico costanti.', de: 'Geschwindigkeit und Last konstant halten.' },
  'Aceleración progresiva': { en: 'Progressive acceleration', it: 'Accelerazione progressiva', de: 'Gleichmäßige Beschleunigung' },
  'Acelera de forma continua en una vía segura y legal.': { en: 'Accelerate continuously on a safe, legal road.', it: 'Accelera in modo continuo su una strada sicura e consentita.', de: 'Auf einer sicheren und zulässigen Straße gleichmäßig beschleunigen.' },
  'Suelta el acelerador para registrar la respuesta de descarga.': { en: 'Release the accelerator to record the overrun response.', it: 'Rilascia l’acceleratore per registrare la risposta in rilascio.', de: 'Gas wegnehmen, um die Reaktion im Schubbetrieb aufzuzeichnen.' },
  'Ralentí inicial': { en: 'Initial idle', it: 'Minimo iniziale', de: 'Anfangsleerlauf' },
  'Con el motor ya caliente, mantén 90 segundos de ralentí sin climatizador ni consumidores importantes.': { en: 'With the engine warm, maintain idle for 90 seconds without climate control or major electrical loads.', it: 'A motore caldo, mantieni il minimo per 90 secondi senza climatizzatore né utenze importanti.', de: 'Bei warmem Motor 90 Sekunden ohne Klimaanlage oder große Verbraucher im Leerlauf laufen lassen.' },
  'Circulación urbana estable': { en: 'Steady urban driving', it: 'Guida urbana regolare', de: 'Gleichmäßige Stadtfahrt' },
  'Circula con suavidad durante 3 minutos, evitando aceleraciones bruscas.': { en: 'Drive gently for 3 minutes, avoiding sudden acceleration.', it: 'Guida dolcemente per 3 minuti evitando accelerazioni brusche.', de: '3 Minuten sanft fahren und starkes Beschleunigen vermeiden.' },
  'Mantén una velocidad legal y estable durante 3 minutos, preferiblemente por encima de 60 km/h.': { en: 'Maintain a legal, steady speed for 3 minutes, preferably above 60 km/h.', it: 'Mantieni una velocità regolare e consentita per 3 minuti, preferibilmente oltre 60 km/h.', de: '3 Minuten eine zulässige, konstante Geschwindigkeit halten, möglichst über 60 km/h.' },
  'Carga progresiva': { en: 'Progressive load', it: 'Carico progressivo', de: 'Progressive Last' },
  'En una vía segura, acelera progresivamente entre unas 1.500 y 3.000 rpm sin superar los límites legales.': { en: 'On a safe road, accelerate progressively between about 1,500 and 3,000 rpm without exceeding legal limits.', it: 'Su una strada sicura, accelera progressivamente tra circa 1.500 e 3.000 giri/min senza superare i limiti.', de: 'Auf sicherer Strecke zwischen etwa 1.500 und 3.000 U/min gleichmäßig beschleunigen, ohne Grenzen zu überschreiten.' },
  'Suelta el acelerador y deja desacelerar el vehículo con una marcha engranada.': { en: 'Release the accelerator and let the vehicle decelerate in gear.', it: 'Rilascia l’acceleratore e lascia decelerare il veicolo con una marcia inserita.', de: 'Gas wegnehmen und das Fahrzeug mit eingelegtem Gang verzögern lassen.' },
  'Detente con seguridad y registra 90 segundos de ralentí con el motor caliente.': { en: 'Stop safely and record 90 seconds of idle with the engine warm.', it: 'Fermati in sicurezza e registra 90 secondi al minimo con il motore caldo.', de: 'Sicher anhalten und 90 Sekunden warmen Leerlauf aufzeichnen.' },
  'Motor caliente': { en: 'Warm engine', it: 'Motore caldo', de: 'Warmer Motor' },
  'Confirma que el motor está a temperatura normal de servicio.': { en: 'Confirm that the engine is at normal operating temperature.', it: 'Conferma che il motore sia alla normale temperatura di esercizio.', de: 'Bestätigen, dass der Motor normale Betriebstemperatur erreicht hat.' },
  'Ciclo mixto': { en: 'Mixed cycle', it: 'Ciclo misto', de: 'Gemischter Fahrzyklus' },
  'Combina circulación urbana y velocidad constante de forma segura.': { en: 'Safely combine urban driving and constant speed.', it: 'Combina in sicurezza guida urbana e velocità costante.', de: 'Stadtfahrt und konstante Geschwindigkeit sicher kombinieren.' },
  'Lectura final': { en: 'Final reading', it: 'Lettura finale', de: 'Abschlussmessung' },
  'Detente y realiza el escaneo final de DTC y monitores.': { en: 'Stop and perform the final DTC and monitor scan.', it: 'Fermati ed esegui la scansione finale di DTC e monitor.', de: 'Anhalten und den abschließenden DTC- und Monitor-Scan durchführen.' },
  'Arranque en Frío': { en: 'Cold start', it: 'Avviamento a freddo', de: 'Kaltstart' },
  'Estudia tensión de batería, arranque, temperatura ambiental/refrigerante y estabilización inicial.': { en: 'Examines battery voltage, starting, ambient/coolant temperature and initial stabilisation.', it: 'Analizza tensione batteria, avviamento, temperatura ambiente/refrigerante e stabilizzazione iniziale.', de: 'Untersucht Batteriespannung, Startvorgang, Umgebungs-/Kühlmitteltemperatur und anfängliche Stabilisierung.' },
  'Aceleración Controlada': { en: 'Controlled acceleration', it: 'Accelerazione controllata', de: 'Kontrollierte Beschleunigung' },
  'Observa la respuesta dinámica de aire, presión de admisión y carga bajo aceleración.': { en: 'Observes the dynamic response of air, intake pressure and load under acceleration.', it: 'Osserva la risposta dinamica di aria, pressione di aspirazione e carico in accelerazione.', de: 'Beobachtet die dynamische Reaktion von Luft, Ansaugdruck und Last beim Beschleunigen.' },
  'Curva de Calentamiento': { en: 'Warm-up curve', it: 'Curva di riscaldamento', de: 'Warmlaufkurve' },
  'Estudia el tiempo de subida de temperatura del refrigerante y termostato.': { en: 'Examines coolant warm-up time and thermostat behaviour.', it: 'Analizza il tempo di aumento della temperatura del refrigerante e il comportamento del termostato.', de: 'Untersucht die Aufwärmzeit des Kühlmittels und das Thermostatverhalten.' },
  'Perfil Personalizado': { en: 'Custom profile', it: 'Profilo personalizzato', de: 'Benutzerdefiniertes Profil' },
  'Selección libre de sensores por el usuario.': { en: 'User-defined sensor selection.', it: 'Selezione libera dei sensori da parte dell’utente.', de: 'Freie Sensorauswahl durch den Benutzer.' },
  'Mi Coche por Dentro — Telemetría OBD-II': { en: 'Inside My Car — OBD-II Telemetry', it: 'Dentro la mia auto — Telemetria OBD-II', de: 'Mein Auto von innen — OBD-II-Telemetrie' },
  'Diagnóstico OBD-II guiado': { en: 'Guided OBD-II diagnostics', it: 'Diagnostica OBD-II guidata', de: 'Geführte OBD-II-Diagnose' },
  'señales propietarias verificadas': { en: 'verified proprietary signals', it: 'segnali proprietari verificati', de: 'verifizierte proprietäre Signale' },
  'Síntoma:': { en: 'Symptom:', it: 'Sintomo:', de: 'Symptom:' },
  'Conversación:': { en: 'Conversation:', it: 'Conversazione:', de: 'Gespräch:' },
  'Histórico:': { en: 'History:', it: 'Storico:', de: 'Verlauf:' },
  'MÍN': { en: 'MIN', it: 'MIN', de: 'MIN' },
  'MÁX': { en: 'MAX', it: 'MAX', de: 'MAX' },
  'Ver en telemetría': { en: 'View in telemetry', it: 'Vedi nella telemetria', de: 'In Telemetrie anzeigen' },
  'Explicación generativa acotada': { en: 'Bounded generative explanation', it: 'Spiegazione generativa vincolata', de: 'Begrenzte generative Erklärung' },
  'señales OBD ·': { en: 'OBD signals ·', it: 'segnali OBD ·', de: 'OBD-Signale ·' },
  'Crítico': { en: 'Critical', it: 'Critico', de: 'Kritisch' },
  'Explicación': { en: 'Explanation', it: 'Spiegazione', de: 'Erklärung' },
  'Conclusión automática basada en evidencia': { en: 'Automatic evidence-based conclusion', it: 'Conclusione automatica basata sulle evidenze', de: 'Automatische evidenzbasierte Schlussfolgerung' },
  'señales': { en: 'signals', it: 'segnali', de: 'Signale' },
  'Sesión': { en: 'Session', it: 'Sessione', de: 'Sitzung' },
  '❌ ATENCIÓN: MIL O DTCs ACTIVOS': { en: '❌ ATTENTION: ACTIVE MIL OR DTCs', it: '❌ ATTENZIONE: MIL O DTC ATTIVI', de: '❌ ACHTUNG: MIL ODER DTCs AKTIV' },
  'Testigo MIL (Luz Avería Cuadro)': { en: 'MIL warning light (dashboard fault light)', it: 'Spia MIL (spia guasto sul quadro)', de: 'MIL-Warnleuchte (Fehlerleuchte im Kombiinstrument)' },
  'Avería(s)': { en: 'Fault(s)', it: 'Guasto/i', de: 'Fehler' },
  'sesiones anteriores válidas y': { en: 'valid previous sessions and', it: 'sessioni precedenti valide e', de: 'gültige frühere Sitzungen und' },
  'señales comparables.': { en: 'comparable signals.', it: 'segnali confrontabili.', de: 'vergleichbare Signale.' },
  'métricas confirmadas': { en: 'confirmed metrics', it: 'metriche confermate', de: 'bestätigte Messgrößen' },
  'métricas catalogadas': { en: 'catalogued metrics', it: 'metriche catalogate', de: 'katalogisierte Messgrößen' },
  'Límites: [': { en: 'Limits: [', it: 'Limiti: [', de: 'Grenzwerte: [' },
  'Resultado · Después': { en: 'Result · After', it: 'Risultato · Dopo', de: 'Ergebnis · Nachher' },
  'Conclusión calculada': { en: 'Calculated conclusion', it: 'Conclusione calcolata', de: 'Berechnetes Fazit' },
  'más estables': { en: 'more stable', it: 'più stabili', de: 'stabiler' },
  'más variables': { en: 'more variable', it: 'più variabili', de: 'variabler' },
  'Más estable': { en: 'More stable', it: 'Più stabile', de: 'Stabiler' },
  'Más variable': { en: 'More variable', it: 'Più variabile', de: 'Variabler' },
  'Kilómetros': { en: 'Kilometres', it: 'Chilometri', de: 'Kilometer' },
  'Duración': { en: 'Duration', it: 'Durata', de: 'Dauer' },
  'frío': { en: 'cold', it: 'freddo', de: 'kalt' },
  'Bucle abierto: carga o retención': { en: 'Open loop: load or overrun', it: 'Ciclo aperto: carico o rilascio', de: 'Offener Regelkreis: Last oder Schubbetrieb' },
  'Presión barométrica': { en: 'Barometric pressure', it: 'Pressione barometrica', de: 'Barometrischer Druck' },
  'Relación equivalente ordenada': { en: 'Commanded equivalence ratio', it: 'Rapporto di equivalenza richiesto', de: 'Soll-Äquivalenzverhältnis' },
  'Corrección corta (STFT)': { en: 'Short-term trim (STFT)', it: 'Correzione a breve termine (STFT)', de: 'Kurzzeitkorrektur (STFT)' },
  'Corrección larga (LTFT)': { en: 'Long-term trim (LTFT)', it: 'Correzione a lungo termine (LTFT)', de: 'Langzeitkorrektur (LTFT)' },
  'Hollín calculado': { en: 'Calculated soot', it: 'Fuliggine calcolata', de: 'Berechneter Ruß' },
  'Hollín medido': { en: 'Measured soot', it: 'Fuliggine misurata', de: 'Gemessener Ruß' },
  'Presión diferencial': { en: 'Differential pressure', it: 'Pressione differenziale', de: 'Differenzdruck' },
  'Desde última regeneración': { en: 'Since last regeneration', it: 'Dall’ultima rigenerazione', de: 'Seit letzter Regeneration' },
  'Tiempo desde regeneración': { en: 'Time since regeneration', it: 'Tempo dalla rigenerazione', de: 'Zeit seit Regeneration' },
  'Regeneración activa': { en: 'Regeneration active', it: 'Rigenerazione attiva', de: 'Regeneration aktiv' },
  'Regeneración inactiva': { en: 'Regeneration inactive', it: 'Rigenerazione inattiva', de: 'Regeneration inaktiv' },
  'Passat de prueba': { en: 'Test Passat', it: 'Passat di prova', de: 'Test-Passat' },
  'Opcional · Ej. Kona de Alejandro': { en: "Optional · E.g. Alejandro's Kona", it: 'Opzionale · Es. la Kona di Alejandro', de: 'Optional · z. B. Alejandros Kona' }
};

let activeLanguage: AppLanguage = 'es';

export const getActiveLanguage = (): AppLanguage => activeLanguage;

const dynamicTranslate = (value: string, language: AppLanguage): string | null => {
  if (language === 'es') return value;
  const numberPatterns: Array<[RegExp, Record<'en' | 'it' | 'de', string>]> = [
    [/^(\d+) lecturas$/, { en: '$1 readings', it: '$1 letture', de: '$1 Messwerte' }],
    [/^(\d+) señales$/, { en: '$1 signals', it: '$1 segnali', de: '$1 Signale' }],
    [/^(\d+) sesiones$/, { en: '$1 sessions', it: '$1 sessioni', de: '$1 Sitzungen' }],
    [/^(\d+) sesiones válidas$/, { en: '$1 valid sessions', it: '$1 sessioni valide', de: '$1 gültige Sitzungen' }],
    [/^Aprendiendo · faltan (\d+)$/, { en: 'Learning · $1 remaining', it: 'Apprendimento · ne mancano $1', de: 'Lernphase · noch $1' }],
    [/^Paso (\d+) de (\d+)$/, { en: 'Step $1 of $2', it: 'Passaggio $1 di $2', de: 'Schritt $1 von $2' }],
    [/^(\d+) señales propietarias verificadas$/, { en: '$1 verified proprietary signals', it: '$1 segnali proprietari verificati', de: '$1 verifizierte proprietäre Signale' }],
    [/^(\d+) códigos leídos de la ECU\.$/, { en: '$1 codes read from the ECU.', it: '$1 codici letti dall’ECU.', de: '$1 Codes aus der ECU gelesen.' }],
    [/^(\d+) min · (\d+) señales objetivo$/, { en: '$1 min · $2 target signals', it: '$1 min · $2 segnali obiettivo', de: '$1 min · $2 Zielsignale' }],
    [/^(\d+) min previstos · (\d+) señales solicitadas$/, { en: '$1 min expected · $2 requested signals', it: '$1 min previsti · $2 segnali richiesti', de: '$1 min vorgesehen · $2 angeforderte Signale' }],
    [/^(\d+) lecturas válidas · (\d+)\/(\d+) señales guardadas · (\d+)% de éxito$/, { en: '$1 valid readings · $2/$3 signals saved · $4% success', it: '$1 letture valide · $2/$3 segnali salvati · $4% di successo', de: '$1 gültige Messwerte · $2/$3 Signale gespeichert · $4% Erfolg' }],
    [/^Último dato válido hace ([\d.,]+) s · revisa el contacto o finaliza la prueba$/, { en: 'Last valid data $1 s ago · check the ignition or finish the test', it: 'Ultimo dato valido $1 s fa · controlla il quadro o termina il test', de: 'Letzter gültiger Wert vor $1 s · Zündung prüfen oder Test beenden' }],
    [/^Prueba finalizada y analizada\. Se guardaron datos de (\d+)\/(\d+) señales solicitadas\.$/, { en: 'Test completed and analysed. Data from $1/$2 requested signals was saved.', it: 'Test completato e analizzato. Sono stati salvati i dati di $1/$2 segnali richiesti.', de: 'Test abgeschlossen und analysiert. Daten von $1/$2 angeforderten Signalen wurden gespeichert.' }],
    [/^(.+) se ha añadido al garaje\.$/, { en: '$1 has been added to the garage.', it: '$1 è stata aggiunta al garage.', de: '$1 wurde zur Garage hinzugefügt.' }],
    [/^ · (\d+)\/(\d+) bloques responden$/, { en: ' · $1/$2 blocks respond', it: ' · $1/$2 blocchi rispondono', de: ' · $1/$2 Blöcke antworten' }],
    [/^ · (\d+)% de cobertura real$/, { en: ' · $1% real coverage', it: ' · $1% di copertura reale', de: ' · $1% reale Abdeckung' }],
    [/^ · (\d+) pendientes$/, { en: ' · $1 pending', it: ' · $1 in attesa', de: ' · $1 ausstehend' }],
    [/^Corrección del inyector (\d+)$/, { en: 'Injector $1 correction', it: 'Correzione iniettore $1', de: 'Injektorkorrektur $1' }],
    [/^Desviación de conmutación (\d+)$/, { en: 'Switch-time deviation $1', it: 'Deviazione di commutazione $1', de: 'Schaltzeitabweichung $1' }],
    [/^Estado (\d+)$/, { en: 'Status $1', it: 'Stato $1', de: 'Status $1' }],
    [/^ · ([\d.,]+) km analizados$/, { en: ' · $1 km analysed', it: ' · $1 km analizzati', de: ' · $1 km analysiert' }],
    [/^Sin fallos BIP \/\/ estado operativo (.+)$/, { en: 'No BIP faults // operating status $1', it: 'Nessun guasto BIP // stato operativo $1', de: 'Keine BIP-Fehler // Betriebsstatus $1' }],
    [/^Revisar estados BIP: (.+)$/, { en: 'Check BIP status: $1', it: 'Controllare gli stati BIP: $1', de: 'BIP-Status prüfen: $1' }],
    [/^(.+) · no es OBD$/, { en: '$1 · not OBD', it: '$1 · non è OBD', de: '$1 · kein OBD' }]
  ];
  for (const [pattern, replacements] of numberPatterns) {
    if (pattern.test(value)) return value.replace(pattern, replacements[language]);
  }
  return null;
};

export const translateText = (input: string, language: AppLanguage = activeLanguage): string => {
  if (!input || language === 'es') return input;
  const match = input.match(/^(\s*)([\s\S]*?)(\s*)$/);
  if (!match) return input;
  const [, before, value, after] = match;
  const exact = UI_TRANSLATIONS[value]?.[language];
  const dynamic = exact || dynamicTranslate(value, language);
  if (dynamic) return `${before}${dynamic}${after}`;
  let fragmented = value;
  const fragmentEntries = Object.entries(UI_TRANSLATIONS)
    .filter(([source]) => source.length >= 8 && fragmented.includes(source))
    .sort(([left], [right]) => right.length - left.length);
  for (const [source, translations] of fragmentEntries) {
    fragmented = fragmented.split(source).join(translations[language]);
  }
  if (fragmented !== value) return `${before}${fragmented}${after}`;
  return input;
};

const LANGUAGE_STORAGE_KEY = 'micoche-language';

interface LanguageContextValue {
  language: AppLanguage;
  setLanguage: (language: AppLanguage) => void;
  t: (value: string) => string;
  locale: string;
  speechLocale: string;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

const localeByLanguage: Record<AppLanguage, string> = {
  es: 'es-ES', en: 'en-GB', it: 'it-IT', de: 'de-DE'
};

const LocalizedDocument: React.FC<{ language: AppLanguage }> = ({ language }) => {
  const observerRef = useRef<MutationObserver | null>(null);
  const originalsRef = useRef(new WeakMap<Node, string>());
  const renderedRef = useRef(new WeakMap<Node, string>());
  const attributeOriginalsRef = useRef(new WeakMap<Element, Map<string, string>>());
  const attributeRenderedRef = useRef(new WeakMap<Element, Map<string, string>>());

  useEffect(() => {
    const translatableAttributes = ['placeholder', 'title', 'aria-label'];
    const originals = originalsRef.current;
    const rendered = renderedRef.current;
    const attributeOriginals = attributeOriginalsRef.current;
    const attributeRendered = attributeRenderedRef.current;

    const translateNode = (node: Node) => {
      if (node.parentElement?.closest('[data-i18n-ignore="true"]')) return;
      if (node.nodeType === Node.TEXT_NODE) {
        const current = node.nodeValue || '';
        if (current !== rendered.get(node)) originals.set(node, current);
        const source = originals.get(node) ?? current;
        const translated = translateText(source, language);
        rendered.set(node, translated);
        if (current !== translated) node.nodeValue = translated;
        return;
      }
      if (!(node instanceof Element)) return;
      let originalsForElement = attributeOriginals.get(node);
      let renderedForElement = attributeRendered.get(node);
      if (!originalsForElement) {
        originalsForElement = new Map();
        attributeOriginals.set(node, originalsForElement);
      }
      if (!renderedForElement) {
        renderedForElement = new Map();
        attributeRendered.set(node, renderedForElement);
      }
      for (const attribute of translatableAttributes) {
        const current = node.getAttribute(attribute);
        if (current === null) continue;
        if (current !== renderedForElement.get(attribute)) originalsForElement.set(attribute, current);
        const source = originalsForElement.get(attribute) ?? current;
        const translated = translateText(source, language);
        renderedForElement.set(attribute, translated);
        if (current !== translated) node.setAttribute(attribute, translated);
      }
      node.childNodes.forEach(translateNode);
    };

    const root = document.body;
    translateNode(root);
    observerRef.current?.disconnect();
    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        if (mutation.type === 'characterData') translateNode(mutation.target);
        if (mutation.type === 'attributes') translateNode(mutation.target);
        mutation.addedNodes.forEach(translateNode);
      }
    });
    observer.observe(root, {
      subtree: true,
      childList: true,
      characterData: true,
      attributes: true,
      attributeFilter: translatableAttributes
    });
    observerRef.current = observer;
    return () => observer.disconnect();
  }, [language]);

  return null;
};

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<AppLanguage>('es');

  useEffect(() => {
    const saved = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (saved && APP_LANGUAGES.some((item) => item.id === saved)) {
      setLanguageState(saved as AppLanguage);
    }
  }, []);

  const setLanguage = useCallback((nextLanguage: AppLanguage) => {
    activeLanguage = nextLanguage;
    setLanguageState(nextLanguage);
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, nextLanguage);
  }, []);

  useEffect(() => {
    activeLanguage = language;
    document.documentElement.lang = language;
    document.documentElement.dir = 'ltr';
    document.title = {
      es: 'Mi Coche por Dentro — Telemetría OBD-II',
      en: 'Inside My Car — OBD-II Telemetry',
      it: 'Dentro la mia auto — Telemetria OBD-II',
      de: 'Mein Auto von innen — OBD-II-Telemetrie'
    }[language];
  }, [language]);

  const value = useMemo<LanguageContextValue>(() => ({
    language,
    setLanguage,
    t: (text: string) => translateText(text, language),
    locale: localeByLanguage[language],
    speechLocale: localeByLanguage[language]
  }), [language, setLanguage]);

  return (
    <LanguageContext.Provider value={value}>
      <LocalizedDocument language={language} />
      {children}
    </LanguageContext.Provider>
  );
};

export const useI18n = (): LanguageContextValue => {
  const context = useContext(LanguageContext);
  if (!context) throw new Error('useI18n must be used inside LanguageProvider');
  return context;
};
