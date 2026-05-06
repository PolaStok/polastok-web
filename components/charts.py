"""
components/charts.py
Fungsi-fungsi visualisasi grafik yang digunakan di berbagai halaman.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_stock_trend(df: pd.DataFrame):
    """Grafik tren stok semua produk."""
    if "tanggal" not in df.columns or "stok" not in df.columns:
        st.info("Data tren tidak tersedia.")
        return

    fig = px.line(
        df,
        x="tanggal",
        y="stok",
        color="nama_produk",
        title="Tren Stok Produk",
        labels={"stok": "Jumlah Stok", "tanggal": "Tanggal"},
    )
    fig.update_layout(legend_title="Produk", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)


def plot_prediction_chart(dates: list, predictions: list, product_name: str):
    """Grafik hasil prediksi demand."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=predictions,
        mode="lines+markers",
        name="Prediksi Demand",
        line=dict(color="#2E86AB", width=2),
        marker=dict(size=8),
    ))
    fig.update_layout(
        title=f"Prediksi Demand — {product_name}",
        xaxis_title="Periode",
        yaxis_title="Unit",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_stock_distribution(df: pd.DataFrame):
    """Pie chart distribusi status stok."""
    status_count = df["status"].value_counts().reset_index()
    status_count.columns = ["Status", "Jumlah"]

    color_map = {"aman": "#28a745", "kritis": "#dc3545", "overstock": "#ffc107"}
    fig = px.pie(
        status_count,
        names="Status",
        values="Jumlah",
        color="Status",
        color_discrete_map=color_map,
        title="Distribusi Status Stok",
    )
    st.plotly_chart(fig, use_container_width=True)
