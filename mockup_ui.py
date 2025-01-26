import streamlit as st
from datetime import date, timedelta
from masterclass_users_devices import Device, User
from tinydb import Query
import pandas as pd
from datetime import datetime
import altair as alt
from streamlit_calendar import calendar

st.write("# Adminmenü")

devices = [dev.device_name for dev in Device.find_all()]
users = [user.name for user in User.find_all()]


tabs = st.tabs(["Geräteverwaltung", "Nutzerverwaltung", "Reservierungssystem", "Wartungs-Management"])

#Tab 1: Geräteverwaltung
with tabs[0]:
    st.header("Geräteverwaltung")
    st.write("Hier können Sie neue Geräte anlegen, bestehende Geräte ändern oder löschen.")

    action = st.radio(
        "Aktion auswählen:",
        ["Neues Gerät anlegen", "Gerät ändern", "Gerät löschen", "Geräteliste anzeigen"],
        key="geraeteverwaltung_aktion"
    )

    if action == "Neues Gerät anlegen":
        st.write("### Neues Gerät anlegen")
        new_device_name = st.text_input("Gerätename:", key="neues_geraet_name")
        
        user_dict = {user.name: user.id for user in User.find_all()}
        user_names = list(user_dict.keys())

        new_device_manager_name = st.selectbox("Geräteverantwortlicher Benutzer:", user_names, key="neues_geraet_manager")
        
        if new_device_manager_name:
            st.write(f"**User ID:** {user_dict[new_device_manager_name]}")
        
        end_of_life_date = st.date_input("End-of-Life Datum:", key="neues_geraet_end_of_life")
        maintenance_interval = st.number_input("Wartungsintervall (in Tagen):", min_value=1, step=1, key="neues_geraet_wartungsintervall")
        maintenance_costs = st.number_input("Wartungkosten (in Euro):", min_value=100, step=1, key="neues_geraet_wartungskosten")

        if st.button("Gerät speichern", key="neues_geraet_speichern"):
            if new_device_name and new_device_manager_name:
                new_device_manager_id = user_dict[new_device_manager_name]
                new_device = Device(
                    device_name=new_device_name, 
                    managed_by_user_id=new_device_manager_id,
                    maintenance_interval = maintenance_interval,
                    maintenance_costs = maintenance_costs
                    )
                creation_date = datetime.now().date()
                next_maintenance = creation_date + timedelta(days=maintenance_interval)
                new_device.update_last_updated()
                new_device.set_end_of_life(end_of_life_date)
                new_device.store_data()
                st.success(f"Das Gerät '{new_device_name}' wurde erfolgreich angelegt!")
            else:
                st.error("Bitte alle Felder ausfüllen!")



    elif action == "Gerät ändern":
        st.write("### Gerät ändern")
        current_device = st.selectbox("Gerät auswählen:", devices, key="geraeteverwaltung_auswahl")
        
        if current_device:
            device_instance = Device.find_by_attribute("device_name", current_device)
            
            user_dict = {user.name: user.id for user in User.find_all()}
            user_names = list(user_dict.keys())
            
            updated_device_manager_name = st.selectbox(
                "Neuer Geräteverantwortlicher Benutzer:", 
                user_names, 
                index=user_names.index(device_instance.managed_by_user_id) if device_instance.managed_by_user_id in user_names else 0,
                key="geraeteverwaltung_manager"
            )
            
            if st.button("Änderungen speichern", key="geraeteverwaltung_speichern"):
                if updated_device_manager_name:
                    updated_device_manager_id = user_dict[updated_device_manager_name]
                    device_instance.managed_by_user_id = updated_device_manager_id
                    device_instance.update_last_updated()
                    device_instance.store_data()
                    st.success(f"Die Änderungen für '{current_device}' wurden gespeichert!")
                else:
                    st.error("Bitte einen neuen Geräteverantwortlichen auswählen!")

    elif action == "Gerät löschen":
        st.write("### Gerät löschen")
        device_to_delete = st.selectbox("Gerät auswählen:", devices, key="geraeteverwaltung_loeschen_auswahl")

        if st.button("Gerät löschen", key="geraeteverwaltung_loeschen"):
            st.session_state["delete_device_confirmation"] = device_to_delete

        if "delete_device_confirmation" in st.session_state:
            st.warning(f"Bist du sicher, dass du das Gerät '{st.session_state['delete_device_confirmation']}' löschen möchtest?")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Ja, löschen", key="delete_device_confirm"):
                    device_instance = Device.find_by_attribute("device_name", st.session_state["delete_device_confirmation"])
                    if device_instance:
                        device_instance.delete()
                        st.success(f"Das Gerät '{st.session_state['delete_device_confirmation']}' wurde erfolgreich gelöscht!")
                    else:
                        st.error(f"Das Gerät '{st.session_state['delete_device_confirmation']}' wurde nicht gefunden!")
                    del st.session_state["delete_device_confirmation"]

            with col2:
                if st.button("Abbrechen", key="delete_device_cancel"):
                    st.info("Löschvorgang abgebrochen.")
                    del st.session_state["delete_device_confirmation"]
    
    elif action == "Geräteliste anzeigen":
        st.write("### Geräteliste anzeigen")
        all_devices = Device.find_all()
        if all_devices:
            device_data = []
            for device in all_devices:
                user_instance = User.find_by_attribute("id", device.managed_by_user_id)
                manager_name = user_instance.name if user_instance else "Kein Verantwortlicher"
                device_data.append({"Gerätename": device.device_name, "Verantwortlicher": manager_name})
            
            df = pd.DataFrame(device_data)
            st.dataframe(df, width=1500)
        else:
            st.write("Keine Geräte vorhanden.")

#Tab 2: Nutzerverwaltung
with tabs[1]:
    st.header("Nutzerverwaltung")
    st.write("Hier können Sie neue Nutzer anlegen.")

    action = st.radio(
        "Aktion auswählen:",
        ["Neuen Nutzer anlegen", "Nutzer ändern", "Nutzer löschen", "Nutzerliste anzeigen"],
        key="nutzerverwaltung_aktion"
    )

    if action == "Neuen Nutzer anlegen":
        st.write("### Neuen Nutzer anlegen")
        new_name = st.text_input("Vor- und Nachname:", key="neuer_nutzer_name")
        new_id = st.text_input("E-Mail-Adresse:", key="neuer_nutzer_email")
        if st.button("Nutzer speichern", key="neuer_nutzer_speichern"):
            if new_name and new_id:
                new_user = User(name=new_name, id=new_id)
                new_user.store_data()
                st.success(f"Der Nutzer '{new_name}' wurde erfolgreich angelegt!")
            else:
                st.error("Bitte alle Felder ausfüllen!")

    elif action == "Nutzer ändern":
        st.write("### Nutzer ändern")
        current_user = st.selectbox("Nutzer auswählen:", users, key="nutzerverwaltung_auswahl")
        user_instance = User.find_by_attribute("name", current_user)

        if user_instance:
            st.write(f"Aktuelle E-Mail-Adresse: {user_instance.id}")
            updated_id = st.text_input("Neue E-Mail-Adresse:", key="nutzerverwaltung_email")

            if st.button("Änderungen speichern", key="nutzerverwaltung_speichern"):
                
                RecordQuery = Query()
                User.db_connector.update({"id": updated_id}, RecordQuery["name"] == current_user)

                st.success(f"Die Änderungen für '{current_user}' wurden erfolgreich gespeichert!")
        else:
            st.error(f"Der Nutzer '{current_user}' wurde nicht gefunden!")

    elif action == "Nutzer löschen":
        st.write("### Nutzer löschen")
        user_to_delete = st.selectbox("Nutzer auswählen:", users, key="nutzerverwaltung_loeschen_auswahl")

        if st.button("Nutzer löschen", key="nutzerverwaltung_loeschen"):
            st.session_state["delete_user_confirmation"] = user_to_delete

        if "delete_user_confirmation" in st.session_state:
            st.warning(f"Bist du sicher, dass du den Nutzer '{st.session_state['delete_user_confirmation']}' löschen möchtest?")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Ja, löschen"):
                    user_instance = User.find_by_attribute("name", st.session_state["delete_user_confirmation"])
                    if user_instance:
                        devices_to_update = Device.find_all()
                        for device in devices_to_update:
                            if device.managed_by_user_id == user_instance.id:
                                device.managed_by_user_id = None
                                device.store_data()
                                st.write(f"Der Nutzer wurde als Verantwortlicher von '{device.device_name}' entfernt.")
                        
                        user_instance.delete()
                        st.success(f"Der Nutzer '{st.session_state['delete_user_confirmation']}' wurde erfolgreich gelöscht und als Verantwortlicher entfernt!")
                    else:
                        st.error(f"Der Nutzer '{st.session_state['delete_user_confirmation']}' wurde nicht gefunden!")
                    del st.session_state["delete_user_confirmation"]  

            with col2:
                if st.button("Abbrechen"):
                    st.info("Löschvorgang abgebrochen.")
                    del st.session_state["delete_user_confirmation"]
    
    elif action == "Nutzerliste anzeigen":
        st.write("### Nutzerliste anzeigen")
        all_users = User.find_all()
        if all_users:
            user_data = [{"Name": user.name, "E-Mail-Adresse": user.id} for user in all_users]
            df = pd.DataFrame(user_data)
            st.dataframe(df, width=1500)
        else:
            st.write("Keine Nutzer vorhanden.")

#Tab 3: Reservierungssystem
with tabs[2]:
    st.header("Reservierungssystem")
    st.write("Hier können Sie Reservierungen für Geräte verwalten und eine Kalenderansicht der Reservierungen sehen.")

    selected_device_name = st.selectbox("Gerät auswählen:", devices, key="reservierung_auswahl")

    if selected_device_name:
        device_instance = Device.find_by_attribute("device_name", selected_device_name)

        st.write(f"### Bestehende Reservierungen für {selected_device_name}")
        if device_instance.reservations:
            df_device = pd.DataFrame(device_instance.reservations)
            st.dataframe(df_device, width=700)
        else:
            st.write("Keine Reservierungen vorhanden.")

        st.write(f"### Kalenderansicht für {selected_device_name}")
        if device_instance.reservations:
            reserved_dates = []
            for reservation in device_instance.reservations:
                start_date = datetime.strptime(reservation["start_date"], "%Y-%m-%d").date()
                end_date = datetime.strptime(reservation["end_date"], "%Y-%m-%d").date()
                reserved_dates.extend([start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)])

            reserved_dates_str = [date.strftime("%Y-%m-%d") for date in reserved_dates]

            events = [{"date": date, "event": "Reserviert"} for date in reserved_dates_str]
            calendar(events)
        else:
            st.write("Keine Reservierungen vorhanden.")

        st.write("### Neue Reservierung erstellen")
        start_date = st.date_input("Startdatum", value=datetime.now().date(), key="reservierung_start")
        end_date = st.date_input("Enddatum", value=datetime.now().date() + timedelta(days=1), key="reservierung_end")

        if st.button("Reservierung speichern", key="reservierung_speichern"):
            if end_date <= start_date:
                st.error("Das Enddatum muss nach dem Startdatum liegen!")
            elif device_instance.add_reservation(start_date, end_date):
                st.success(f"Reservierung für {selected_device_name} von {start_date} bis {end_date} wurde erfolgreich erstellt!")
            else:
                st.error("Konflikt: Die Reservierung überschneidet sich mit einer bestehenden Reservierung!")


#Tab 4: Wartungsmanagement
with tabs[3]:
    st.header("Wartungs-Management")
    st.write("Hier sehen Sie die Wartungsinformationen für die Geräte.")

    action = st.radio(
        "Aktion auswählen:",
        ["Detail-Geräteinformation", "Gesamtliste der Geräte"],
        key="wartungsmanagement_aktion"
    )

    if action == "Detail-Geräteinformation":
        selected_device_name = st.selectbox("Gerät auswählen:", devices, key="wartung_auswahl_einzel")
        
        if selected_device_name:
            device_instance = Device.find_by_attribute("device_name", selected_device_name)
            quarterly_costs = device_instance.calculate_quarterly_maintenance_costs()
            
            st.write(f"### Wartungsinformationen für {selected_device_name}")
            st.write(f"- **Nächster Wartungstermin:** {device_instance.next_maintenance}")
            st.write(f"- **End-of-Life Datum:** {device_instance.end_of_life}")
            st.write(f"- **Quartalsmäßige Kosten:** {quarterly_costs:.2f} €")

    elif action == "Gesamtliste der Geräte":
        st.write("### Gesamtliste der Geräte")
        all_devices = Device.find_all()
        
        if all_devices:

            sorted_devices = sorted(all_devices, key=lambda x: x.next_maintenance or datetime.max)
            
            device_data = []
            total_quarterly_costs = 0
            
            for device in sorted_devices:
                quarterly_costs = device.calculate_quarterly_maintenance_costs()
                total_quarterly_costs += quarterly_costs
                
                device_data.append({
                    "Gerätename": device.device_name,
                    "Nächste Wartung": device.next_maintenance,
                    "Quartalsmäßige Kosten (€)": f"{quarterly_costs:.2f}"
                })
            
            df = pd.DataFrame(device_data)
            st.dataframe(df, width=1500)
            
            st.write(f"**Gesamte Quartalskosten für alle Geräte:** {total_quarterly_costs:.2f} €")
        else:
            st.write("Keine Geräte vorhanden.")


