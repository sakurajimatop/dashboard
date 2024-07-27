#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 20:13:03 2024

@author: sakurajima
"""

import streamlit as st

import pandas as pd


df = pd.read_csv(
    "/home/sakurajima/Documents/dexter_lab/python_local/projects/kedro_etl/shipments.csv",
    sep=";",
    encoding="latin1",
)
st.markdown("# Principales Origenes y Destinos 2 ❄️")
st.sidebar.markdown("# Origines y Destinos 2 ❄️")

destination_df = df.groupby(by=["Destination"]).count()
destination_df = destination_df.sort_values(by=["Origin"], ascending=False)
destination_df["shipment_number"]

origin_df = df.groupby(by=["Origin"]).count()
origin_df.sort_values(by=["Destination"], ascending=False)
origin_df["shipment_number"]
