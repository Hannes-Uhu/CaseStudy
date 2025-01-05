import streamlit as st
from datetime import date, timedelta

# Eine Überschrift der ersten Ebene
st.write("# Adminmenü")

# Beispiel-Daten für Geräte und Wartungsinformationen
devices = ["Gerät_A", "Gerät_B", "Gerät_C"]
reservations = {
    "Gerät_A": [("2025-01-05", "2025-01-07")],  # Beispiel-Reservierung für ganze Tage
    "Gerät_B": [],
    "Gerät_C": [],
}
maintenance_info = {
    "Gerät_A": {"next_maintenance": "2025-03-15", "quarterly_costs": 150},
    "Gerät_B": {"next_maintenance": "2025-04-10", "quarterly_costs": 200},
    "Gerät_C": {"next_maintenance": "2025-05-05", "quarterly_costs": 250},
}

# Reiter erstellen
tabs = st.tabs(["Geräteverwaltung", "Nutzerverwaltung", "Reservierungssystem", "Wartungs-Management"])

# Inhalt für Tab 1: Geräteverwaltung
with tabs[0]:
    st.header("Geräteverwaltung")
    st.write("Das ist der erste Reiter.")

    # Radio-Buttons zur Auswahl der Aktion
    action = st.radio(
        "Aktion auswählen:",
        ["Neues Gerät anlegen", "Gerät ändern"],
        key="geraeteverwaltung_aktion"
    )

    if action == "Neues Gerät anlegen":
        st.write("### Neues Gerät anlegen")
        new_device_name = st.text_input("Gerätename:", key="neues_geraet_name")
        new_device_manager = st.text_input("Geräteverantwortlicher Benutzer:", key="neues_geraet_manager")

        if st.button("Gerät speichern", key="neues_geraet_speichern"):
            if new_device_name and new_device_manager:
                st.success(f"Das Gerät '{new_device_name}' wurde erfolgreich angelegt!")
            else:
                st.error("Bitte alle Felder ausfüllen!")

    elif action == "Gerät ändern":
        st.write("### Gerät ändern")
        current_device = st.selectbox("Gerät auswählen:", devices, key="geraeteverwaltung_auswahl")
        updated_device_name = st.text_input("Neuer Gerätename:", current_device, key="geraeteverwaltung_name")
        updated_device_manager = st.text_input("Neuer Geräteverantwortlicher Benutzer:", key="geraeteverwaltung_manager")

        if st.button("Änderungen speichern", key="geraeteverwaltung_speichern"):
            st.success(f"Die Änderungen für '{current_device}' wurden gespeichert!")

# Inhalt für Tab 2: Nutzerverwaltung
with tabs[1]:
    st.header("Nutzerverwaltung")
    st.write("Hier können Sie neue Nutzer anlegen.")

    first_name = st.text_input("Vorname:", key="nutzer_vorname")
    last_name = st.text_input("Nachname:", key="nutzer_nachname")
    email = st.text_input("E-Mail-Adresse:", key="nutzer_email")

    if st.button("Nutzer hinzufügen", key="nutzer_hinzufuegen"):
        if first_name and last_name and email:
            st.success(f"Der Nutzer {first_name} {last_name} ({email}) wurde erfolgreich angelegt!")
        else:
            st.error("Bitte alle Felder ausfüllen!")

# Inhalt für Tab 3: Reservierungssystem
with tabs[2]:
    st.header("Reservierungssystem")
    st.write("Hier können Sie Reservierungen für Geräte verwalten.")

    # Gerät auswählen
    selected_device = st.selectbox("Gerät auswählen:", devices, key="reservierung_auswahl")

    # Bestehende Reservierungen anzeigen
    st.write(f"### Bestehende Reservierungen für {selected_device}:")
    if reservations[selected_device]:
        for start, end in reservations[selected_device]:
            st.write(f"- Start: {start}, Ende: {end}")
    else:
        st.write("Keine Reservierungen vorhanden.")

    # Neue Reservierung erstellen
    st.write("### Neue Reservierung erstellen")
    start_date = st.date_input("Startdatum", value=date.today(), key="reservierung_start")
    end_date = st.date_input("Enddatum", value=date.today() + timedelta(days=1), key="reservierung_end")

    if st.button("Reservierung speichern", key="reservierung_speichern"):
        if end_date <= start_date:
            st.error("Das Enddatum muss nach dem Startdatum liegen!")
        else:
            reservations[selected_device].append((start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            st.success(f"Reservierung für {selected_device} von {start_date} bis {end_date} wurde erfolgreich erstellt!")

# Inhalt für Tab 4: Wartungsmanagement
with tabs[3]:
    st.header("Wartungs-Management")
    st.write("Hier sehen Sie die Wartungsinformationen für die Geräte.")

    # Gerät auswählen
    selected_device = st.selectbox("Gerät auswählen:", devices, key="wartung_auswahl")

    if selected_device:
        info = maintenance_info[selected_device]
        st.write(f"### Wartungsinformationen für {selected_device}")
        st.write(f"- **Nächster Wartungstermin:** {info['next_maintenance']}")
        st.write(f"- **Quartalsmäßige Kosten:** {info['quarterly_costs']} €")
