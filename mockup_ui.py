import streamlit as st
from datetime import date, timedelta
from masterclass_users_devices import Device

# Überschrift der ersten Ebene
st.write("# Adminmenü")

# Beispiel-Daten
devices = [dev.device_name for dev in Device.find_all()]

reservations = {
    "Gerät_A": [("2025-01-05", "2025-01-07")],  
    "Gerät_B": [("2025-01-10", "2025-02-12")],
    "Gerät_C": [("2025-02-01", "2025-01-07")],
}

maintenance_info = {
    "Gerät_A": {"next_maintenance": "2025-03-15", "quarterly_costs": 150},
    "Gerät_B": {"next_maintenance": "2025-04-10", "quarterly_costs": 200},
    "Gerät_C": {"next_maintenance": "2025-05-05", "quarterly_costs": 250},
}

tabs = st.tabs(["Geräteverwaltung", "Nutzerverwaltung", "Reservierungssystem", "Wartungs-Management"])

#Tab 1: Geräteverwaltung
with tabs[0]:
    st.header("Geräteverwaltung")
    st.write("Hier können Sie neue Geräte anlegen, bestehende Geräte ändern oder löschen.")

    action = st.radio(
        "Aktion auswählen:",
        ["Neues Gerät anlegen", "Gerät ändern", "Gerät löschen"],
        key="geraeteverwaltung_aktion"
    )

    if action == "Neues Gerät anlegen":
        st.write("### Neues Gerät anlegen")
        new_device_name = st.text_input("Gerätename:", key="neues_geraet_name")
        new_device_manager = st.text_input("Geräteverantwortlicher Benutzer:", key="neues_geraet_manager")
        if st.button("Gerät speichern", key="neues_geraet_speichern"):
            if new_device_name and new_device_manager:
                new_device = Device(device_name=new_device_name,managed_by_user_id=new_device_manager)
                new_device.store_data()
                st.success(f"Das Gerät '{new_device_name}' wurde erfolgreich angelegt!")
            else:
                st.error("Bitte alle Felder ausfüllen!")
    
    elif action == "Gerät ändern":
        st.write("### Gerät ändern")
        current_device = st.selectbox("Gerät auswählen:", devices, key="geraeteverwaltung_auswahl")
        updated_device_manager = st.text_input("Neuer Geräteverantwortlicher Benutzer:", key="geraeteverwaltung_manager")

        if st.button("Änderungen speichern", key="geraeteverwaltung_speichern"):
            device_instance = Device.find_by_attribute("device_name", current_device)
            device_instance.managed_by_user_id = updated_device_manager
            device_instance.store_data()
            st.success(f"Die Änderungen für '{current_device}' wurden gespeichert!")

    elif action == "Gerät löschen":
        st.write("### Gerät löschen")
        device_to_delete = st.selectbox("Gerät auswählen:", devices, key="geraeteverwaltung_loeschen_auswahl")
        if st.button("Gerät löschen", key="geraeteverwaltung_loeschen"):
            # Assuming Device class has a delete method
            device_instance = Device.find_by_attribute("device_name", device_to_delete)
            device_instance.delete()
            st.success(f"Das Gerät '{device_to_delete}' wurde erfolgreich gelöscht!")


#Tab 2: Nutzerverwaltung
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

#Tab 3: Reservierungssystem
with tabs[2]:
    st.header("Reservierungssystem")
    st.write("Hier können Sie Reservierungen für Geräte verwalten.")
  
    selected_device = st.selectbox("Gerät auswählen:", devices, key="reservierung_auswahl")

    st.write(f"### Bestehende Reservierungen für {selected_device}:")
    if reservations[selected_device]:
        for start, end in reservations[selected_device]:
            st.write(f"- Start: {start}, Ende: {end}")
    else:
        st.write("Keine Reservierungen vorhanden.")

    st.write("### Neue Reservierung erstellen")
    start_date = st.date_input("Startdatum", value=date.today(), key="reservierung_start")
    end_date = st.date_input("Enddatum", value=date.today() + timedelta(days=1), key="reservierung_end")

    if st.button("Reservierung speichern", key="reservierung_speichern"):
        if end_date <= start_date:
            st.error("Das Enddatum muss nach dem Startdatum liegen!")
        else:
            reservations[selected_device].append((start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            st.success(f"Reservierung für {selected_device} von {start_date} bis {end_date} wurde erfolgreich erstellt!")

#Tab 4: Wartungsmanagement
with tabs[3]:
    st.header("Wartungs-Management")
    st.write("Hier sehen Sie die Wartungsinformationen für die Geräte.")

    selected_device = st.selectbox("Gerät auswählen:", devices, key="wartung_auswahl")

    if selected_device:
        info = maintenance_info[selected_device]
        st.write(f"### Wartungsinformationen für {selected_device}")
        st.write(f"- **Nächster Wartungstermin:** {info['next_maintenance']}")
        st.write(f"- **Quartalsmäßige Kosten:** {info['quarterly_costs']} €")
