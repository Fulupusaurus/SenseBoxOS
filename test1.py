import streamlit as st
import pandas as pd
import plotly.express as px

# Seitenlayout
st.set_page_config(page_title="SenseBox Datenanalyse", layout="wide")

st.title("SenseBox Datenanalyse")
st.markdown("CSV Datei mit Sensordaten hochladen")

uploaded_file = st.file_uploader("CSV Datei auswählen", type="csv")

if uploaded_file:

    # CSV laden
    df = pd.read_csv(uploaded_file)

    st.success("Datei erfolgreich geladen")

    st.subheader("Rohdaten Vorschau")
    st.dataframe(df.head())

    # Zeitspalte 
    df["Zeitraum"] = pd.to_datetime(df["Zeitraum"])

    # Sortieren
    df = df.sort_values("Zeitraum")

    # Datum 
    df["Datum"] = df["Zeitraum"].dt.date

    # Tagesdurchschnitt berechnen
    daily_df = df.groupby("Datum").mean(numeric_only=True).reset_index()
    daily_df["Datum"] = pd.to_datetime(daily_df["Datum"])

    st.subheader("Tagesdurchschnitt")
    st.dataframe(daily_df.head())

    # Messwert auswählen
    st.subheader("Analyse Einstellungen")

    metric = st.selectbox(
        "Messwert auswählen",
        ["Temperatur", "Luftfeuchtigkeit", "Bodentemperatur", "Bodenfeuchtigkeit"]
    )

    # Zwei Analysemodi
    tab1, tab2 = st.tabs(["Standard Zeiträume", "Benutzerdefinierter Zeitraum"])

    # ---------------------------------------------------
    # STANDARD ZEITRÄUME
    # ---------------------------------------------------

    with tab1:

        period = st.radio(
            "Zeitraum auswählen",
            ["Letzte Woche", "Letzter Monat", "Letztes Jahr"]
        )

        today = daily_df["Datum"].max()

        if period == "Letzte Woche":
            filtered = daily_df[daily_df["Datum"] >= today - pd.Timedelta(days=7)]

        elif period == "Letzter Monat":
            filtered = daily_df[daily_df["Datum"] >= today - pd.Timedelta(days=30)]
            filtered = filtered.iloc[::2]

        elif period == "Letztes Jahr":
            filtered = daily_df[daily_df["Datum"] >= today - pd.Timedelta(days=365)]

        # Statistik
        mean_val = filtered[metric].mean()
        std_val = filtered[metric].std()
        min_val = filtered[metric].min()
        max_val = filtered[metric].max()

        st.subheader("Statistische Auswertung")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Mittelwert", f"{mean_val:.2f}")
        col2.metric("Standardabweichung", f"{std_val:.2f}")
        col3.metric("Minimum", f"{min_val:.2f}")
        col4.metric("Maximum", f"{max_val:.2f}")

        # Diagramm
        st.subheader("Messwert Verlauf")

        fig = px.line(
            filtered,
            x="Datum",
            y=metric,
            title=f"{metric} Verlauf ({period})",
            markers=True
        )

        st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------
    # BENUTZERDEFINIERTER ZEITRAUM
    # ---------------------------------------------------

    with tab2:

        st.subheader("Eigenen Zeitraum auswählen")

        start_date = st.date_input(
            "Startdatum",
            value=daily_df["Datum"].min()
        )

        end_date = st.date_input(
            "Enddatum",
            value=daily_df["Datum"].max()
        )

        custom_filtered = daily_df[
            (daily_df["Datum"] >= pd.to_datetime(start_date)) &
            (daily_df["Datum"] <= pd.to_datetime(end_date))
        ]

        if not custom_filtered.empty:

            # Statistik
            mean_val = custom_filtered[metric].mean()
            std_val = custom_filtered[metric].std()
            min_val = custom_filtered[metric].min()
            max_val = custom_filtered[metric].max()

            st.subheader("Statistische Auswertung")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Mittelwert", f"{mean_val:.2f}")
            col2.metric("Standardabweichung", f"{std_val:.2f}")
            col3.metric("Minimum", f"{min_val:.2f}")
            col4.metric("Maximum", f"{max_val:.2f}")

            # Diagramm
            st.subheader("Messwert Verlauf")

            fig = px.line(
                custom_filtered,
                x="Datum",
                y=metric,
                title=f"{metric} Verlauf ({start_date} bis {end_date})",
                markers=True
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Keine Daten im ausgewählten Zeitraum vorhanden.")

else:
    st.info("Bitte eine CSV Datei hochladen um zu beginnen.")