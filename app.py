#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 17:33:39 2024



Montar: Clientes mas rentables
Destinos mas rentables
Totales de kilos movidos por aereo

@author: sakurajima
"""
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import pandas as pd
import plotly.express as px
import streamlit as st
import time
import plotly.graph_objects as go
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

# https://blog.streamlit.io/drill-downs-and-filtering-with-streamlit-and-altair/
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["pre-authorized"],
)

authenticator.login()

if st.session_state["authentication_status"]:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.header("Brum Brum SL  :truck:")

    # with st.sidebar:
    #     with st.echo():
    #         # "SIDEBAR"

    #     with st.spinner("Loading..."):
    #         time.sleep(0)
    #     st.success("Done!")

    df = pd.read_csv(
        "shipments.csv",
        sep=";",
        encoding="latin1",
    )
    df["Date"] = pd.to_datetime(df["Date"], yearfirst=True)
    df["Gross Margin"] = df["Invoiced Value"] * df["Markup"]
    # df.columns

    df = filter_dataframe(df)

    fig = px.histogram(
        df,
        x=df["Date"].dt.strftime("%b"),
        y=df["Gross Margin"],
        color=df.Date.dt.year,
        barmode="group",
    )

    month_order = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    fig.update_layout(
        title="Monthly Sales",
        xaxis_title="Sales",
        yaxis_title="Month",
        yaxis={
            "categoryorder": "array",
            "categoryarray": month_order,
        },  # Ensure the y-axis is sorted correctly
    )
    st.plotly_chart(fig, use_container_width=True)

    department_fig = go.Figure(
        go.Bar(
            x=df["Gross Margin"],
            y=df["Department"],
            orientation="h",
            hovertemplate="<b>Gross Margin:</b> %{x}<br>",
        )
    )
    department_fig.update_yaxes(
        categoryorder="total ascending"
    )  # https://plotly.com/python/categorical-axes/

    st.plotly_chart(department_fig, use_container_width=True)


elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")
