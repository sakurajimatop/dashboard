#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 16:18:18 2024

@author: sakurajima
"""

import plotly.express as px
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader

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

    df = pd.read_csv(
        "shipments.csv",
        sep=";",
        encoding="latin1",
    )

    st.markdown("# Gross Margin por comercial")
    df["Gross Margin"] = df["Invoiced Value"] * df["Markup"]

    fig = go.Figure(go.Bar(x=df["Gross Margin"], y=df["sales_ex"], orientation="h"))
    # fig.update_layout(xaxis = {"categoryorder":"total ascending"})
    fig.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig, use_container_width=True)
elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")
