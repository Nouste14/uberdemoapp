import streamlit as st
import plotly.express as px
import zipfile
import geopandas
import numpy as np
import pandas as pd



st.title("Chart 1")
st.write("This is Chart 1")

def read_and_preprocess_data() -> tuple[pd.DataFrame, geopandas.GeoDataFrame]:
    """
    Reads Uber data from the zip file and preprocesses it.
    """
    
    with zipfile.ZipFile('data/uber-data.zip') as zip:
        with zip.open('madrid-barrios-2020-1-All-DatesByHourBucketsAggregate.csv') as csv:
            data = pd.read_csv(csv)
        with zip.open('madrid_barrios.json') as geojson:
            codes = geopandas.read_file(geojson, encoding="utf-8")

    # change data types in codes because they are not the same as in data
    codes['GEOCODIGO'] = codes['GEOCODIGO'].astype(int)
    codes['MOVEMENT_ID'] = codes['MOVEMENT_ID'].astype(int)

    codes["DISPLAY_NAME"] = codes["DISPLAY_NAME"].str.split().str[1:].str.join(" ")

    # Merge the data with the codes (source)
    data = data.merge(codes[["GEOCODIGO","MOVEMENT_ID","DISPLAY_NAME"]], left_on="sourceid", right_on="MOVEMENT_ID", how="left")
    data = data.rename(columns={"GEOCODIGO":"src_neigh_code", "DISPLAY_NAME":"src_neigh_name"}).drop(columns=["MOVEMENT_ID"])

    data = data.merge(codes[["GEOCODIGO","MOVEMENT_ID","DISPLAY_NAME"]], left_on="dstid", right_on="MOVEMENT_ID", how="left")
    data = data.rename(columns={"GEOCODIGO":"dst_neigh_code", "DISPLAY_NAME":"dst_neigh_name"}).drop(columns=["MOVEMENT_ID"])

    # Create a new date column
    data["year"] = "2020"
    data["date"] = pd.to_datetime(data["day"].astype(str)+data["month"].astype(str)+data["year"].astype(str)+":"+data["start_hour"].astype(str), format="%d%m%Y:%H")

    # Create a new day_period column
    data["day_period"] = data.start_hour.astype(str) + "-" + data.end_hour.astype(str)
    data["day_of_week"] = data.date.dt.weekday
    data["day_of_week_str"] = data.date.dt.day_name()

    return data, codes


data, codes = read_and_preprocess_data()
sources = sorted(data.src_neigh_name.unique())
destinations = sorted(data.dst_neigh_name.unique())
    
source = st.sidebar.selectbox('Select the source', sources)
destination = st.sidebar.selectbox('Select the destination', destinations)
    
aux = data[(data.src_neigh_name == source) & (data.dst_neigh_name == destination)]
aux = aux.sort_values("date")
###LINES 72 - 80 SHOWS THE SIDEBAR AND THE SELECTBOXES FOR SOURCE AND DESTINATION NEIGHBORHOODS


# CHART 1
fig1 = px.line(
        aux, x="date", y="mean_travel_time", text="day_period",
        error_y="standard_deviation_travel_time",
        title="Travel time from {} to {}".format(source, destination),
        template="none"
    )

fig1.update_xaxes(title="Date")
fig1.update_yaxes(title="Avg. travel time (seconds)")
fig1.update_traces(mode="lines+markers", marker_size=10, line_width=3, error_y_color="gray", error_y_thickness=1, error_y_width=10)
    
st.plotly_chart(fig1, use_container_width=True)
