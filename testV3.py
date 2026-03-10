import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SenseBox Analyse Dashboard", layout="wide")

st.title("SenseBox Sensor Analyse & Vergleich")

st.markdown("Mehrere SenseBox CSV Dateien hochladen und Sensordaten vergleichen.")

# ---------------------------------------------------
# Einheiten der Sensoren
# ---------------------------------------------------

units = {
    "Temperatur": "°C",
    "Luftfeuchtigkeit": "%",
    "Bodentemperatur": "°C",
    "Bodenfeuchtigkeit": "%"
}

# ---------------------------------------------------
# CSV Upload
# ---------------------------------------------------

uploaded_files = st.file_uploader(
    "CSV Dateien auswählen",
    type="csv",
    accept_multiple_files=True
)

if uploaded_files:

    station_data = {}

    # ---------------------------------------------------
    # Dateien einlesen
    # ---------------------------------------------------

    for file in uploaded_files:

        station_name = file.name.replace(".csv", "")

        df = pd.read_csv(file)

        df["Zeitraum"] = pd.to_datetime(df["Zeitraum"])
        df = df.sort_values("Zeitraum")

        df["Datum"] = df["Zeitraum"].dt.date

        daily_df = df.groupby("Datum").mean(numeric_only=True).reset_index()
        daily_df["Datum"] = pd.to_datetime(daily_df["Datum"])

        station_data[station_name] = daily_df

    # ---------------------------------------------------
    # Sensor Auswahl
    # ---------------------------------------------------

    st.subheader("Analyse Einstellungen")

    metrics = st.multiselect(
        "Sensoren auswählen",
        ["Temperatur", "Luftfeuchtigkeit", "Bodentemperatur", "Bodenfeuchtigkeit"],
        default=["Temperatur"]
    )

    tab1, tab2 = st.tabs(["Standard Zeiträume", "Benutzerdefinierter Zeitraum"])

    # ---------------------------------------------------
    # STANDARD ZEITRÄUME
    # ---------------------------------------------------

    with tab1:

        period = st.radio(
            "Zeitraum auswählen",
            ["Letzte Woche", "Letzter Monat", "Letztes Jahr"]
        )

        all_data = []

        for station, data in station_data.items():

            today = data["Datum"].max()

            if period == "Letzte Woche":
                filtered = data[data["Datum"] >= today - pd.Timedelta(days=7)]

            elif period == "Letzter Monat":
                filtered = data[data["Datum"] >= today - pd.Timedelta(days=30)]
                filtered = filtered.iloc[::2]

            else:
                filtered = data[data["Datum"] >= today - pd.Timedelta(days=365)]

            filtered["Station"] = station
            all_data.append(filtered)

        combined = pd.concat(all_data)

        # ---------------------------------------------------
        # Statistik
        # ---------------------------------------------------

        if len(metrics) == 1:

            metric = metrics[0]

            stats = []

            for station in combined["Station"].unique():

                subset = combined[combined["Station"] == station]

                stats.append({
                    "Station": station,
                    f"Mittelwert ({units[metric]})": round(subset[metric].mean(), 2),
                    f"Standardabweichung ({units[metric]})": round(subset[metric].std(), 2),
                    f"Minimum ({units[metric]})": round(subset[metric].min(), 2),
                    f"Maximum ({units[metric]})": round(subset[metric].max(), 2)
                })

            stats_df = pd.DataFrame(stats)

            st.subheader("Statistischer Vergleich")

            st.dataframe(stats_df, use_container_width=True)

        # ---------------------------------------------------
        # Diagramme
        # ---------------------------------------------------

        st.subheader("Sensorverlauf")

        for metric in metrics:

            fig = px.line(
                combined,
                x="Datum",
                y=metric,
                color="Station",
                markers=True,
                title=f"{metric} Vergleich ({period})",
                labels={metric: f"{metric} ({units[metric]})"}
            )

            st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------
    # BENUTZERDEFINIERTER ZEITRAUM
    # ---------------------------------------------------

    with tab2:

        st.subheader("Eigenen Zeitraum auswählen")

        min_date = min(df["Datum"].min() for df in station_data.values())
        max_date = max(df["Datum"].max() for df in station_data.values())

        start_date = st.date_input("Startdatum", value=min_date)
        end_date = st.date_input("Enddatum", value=max_date)

        all_data = []

        for station, data in station_data.items():

            filtered = data[
                (data["Datum"] >= pd.to_datetime(start_date)) &
                (data["Datum"] <= pd.to_datetime(end_date))
            ]

            filtered["Station"] = station
            all_data.append(filtered)

        combined = pd.concat(all_data)

        if not combined.empty:

            # Statistik nur bei einem Sensor

            if len(metrics) == 1:

                metric = metrics[0]

                stats = []

                for station in combined["Station"].unique():

                    subset = combined[combined["Station"] == station]

                    stats.append({
                        "Station": station,
                        f"Mittelwert ({units[metric]})": round(subset[metric].mean(), 2),
                        f"Standardabweichung ({units[metric]})": round(subset[metric].std(), 2),
                        f"Minimum ({units[metric]})": round(subset[metric].min(), 2),
                        f"Maximum ({units[metric]})": round(subset[metric].max(), 2)
                    })

                stats_df = pd.DataFrame(stats)

                st.subheader("Statistischer Vergleich")

                st.dataframe(stats_df, use_container_width=True)

            # Diagramme

            st.subheader("Sensorverlauf")

            for metric in metrics:

                fig = px.line(
                    combined,
                    x="Datum",
                    y=metric,
                    color="Station",
                    markers=True,
                    title=f"{metric} Vergleich ({start_date} bis {end_date})",
                    labels={metric: f"{metric} ({units[metric]})"}
                )

                st.plotly_chart(fig, use_container_width=True)

        else:

            st.warning("Keine Daten im ausgewählten Zeitraum vorhanden.")

else:

    st.info("Bitte mindestens eine CSV Datei hochladen.")