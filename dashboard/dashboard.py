import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid")
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main_data.csv")
    df = pd.read_csv(path, parse_dates=["order_purchase_timestamp"])
    return df


df = load_data()

# ---------------- Sidebar ----------------
st.sidebar.header("Filter")
min_date = df["order_purchase_timestamp"].min().date()
max_date = df["order_purchase_timestamp"].max().date()
date_range = st.sidebar.date_input("Rentang tanggal pembelian", value=(min_date, max_date),
                                   min_value=min_date, max_value=max_date)
all_states = sorted(df["customer_state"].dropna().unique())
states = st.sidebar.multiselect("State pelanggan", all_states, default=all_states)
top_n = st.sidebar.slider("Jumlah kategori teratas", 5, 15, 10)
min_orders = st.sidebar.slider("Minimal pesanan per state (Q2)", 1, 300, 100)

if len(date_range) != 2:
    st.info("Pilih tanggal awal dan akhir.")
    st.stop()

start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
fdf = df[(df["order_purchase_timestamp"] >= start) & (df["order_purchase_timestamp"] < end)
         & (df["customer_state"].isin(states))]

if fdf.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

order_level = fdf.drop_duplicates(subset="order_id")

# ---------------- Header & KPI ----------------
st.title("E-Commerce Public Dataset Dashboard")
st.caption("Pesanan berstatus delivered, Januari 2017 - Agustus 2018")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"R$ {fdf['price'].sum():,.0f}")
c2.metric("Total Pesanan", f"{order_level.shape[0]:,}")
c3.metric("Rata-rata Review", f"{order_level['review_score'].mean():.2f} / 5")
c4.metric("Pesanan Terlambat", f"{order_level['is_late'].mean() * 100:.1f}%")

tab1, tab2 = st.tabs(["Q1: Revenue per Kategori", "Q2: Keterlambatan & Review"])

# ---------------- Q1 ----------------
with tab1:
    st.subheader(f"{top_n} Kategori Produk dengan Revenue Tertinggi")
    cat = (fdf.groupby("product_category_name_english")["price"].sum()
           .sort_values(ascending=False).reset_index())
    cat["share"] = cat["price"] / cat["price"].sum() * 100
    top = cat.head(top_n)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#2a7fba"] * min(5, len(top)) + ["#b0b7bf"] * max(0, len(top) - 5)
    ax.barh(top["product_category_name_english"], top["price"], color=colors)
    ax.invert_yaxis()
    sns.despine()
    for i, (v, p) in enumerate(zip(top["price"], top["share"])):
        ax.text(v, i, f"  R$ {v/1e6:.2f} jt ({p:.1f}%)", va="center", fontsize=9)
    ax.set_xlim(0, top["price"].max() * 1.3)
    ax.set_xlabel("Total Revenue (R$)")
    ax.set_ylabel("")
    st.pyplot(fig)
    st.write(f"Kategori teratas menyumbang **{top['share'].sum():.1f}%** dari total revenue pada filter ini.")

    st.subheader("Tren Revenue Bulanan")
    monthly = fdf.groupby("order_month")["price"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 3.5))
    sns.lineplot(data=monthly, x="order_month", y="price", marker="o", color="#2a7fba", ax=ax)
    ax.set_ylim(bottom=0)
    sns.despine()
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Revenue (R$)")
    plt.xticks(rotation=45)
    st.pyplot(fig)

# ---------------- Q2 ----------------
with tab2:
    state_stats = (order_level.groupby("customer_state")
                   .agg(total_orders=("order_id", "count"),
                        late_pct=("is_late", lambda s: s.mean() * 100),
                        avg_delivery_days=("delivery_time_days", "mean"),
                        avg_review=("review_score", "mean"))
                   .reset_index())
    state_stats = state_stats[state_stats["total_orders"] >= min_orders].sort_values("late_pct", ascending=False)

    left, right = st.columns(2)
    with left:
        st.subheader("State dengan % Pesanan Terlambat Tertinggi")
        if state_stats.empty:
            st.info("Tidak ada state yang memenuhi minimal pesanan. Turunkan nilai filter.")
        else:
            fig, ax = plt.subplots(figsize=(6, 5))
            top_late = state_stats.head(10)
            cols = ["#d9534f"] * min(5, len(top_late)) + ["#b0b7bf"] * max(0, len(top_late) - 5)
            ax.barh(top_late["customer_state"], top_late["late_pct"], color=cols)
            ax.invert_yaxis()
            overall = order_level["is_late"].mean() * 100
            ax.axvline(overall, color="black", linestyle="--", linewidth=1)
            ax.text(overall, len(top_late) - 0.4, f" Rata-rata {overall:.1f}%", fontsize=9, va="bottom")
            sns.despine()
            ax.set_xlabel("Pesanan Terlambat (%)")
            ax.set_ylabel("State")
            st.pyplot(fig)
    with right:
        st.subheader("Review Score: Tepat Waktu vs Terlambat")
        rv = (order_level.groupby("is_late")["review_score"].mean().reset_index()
              .replace({"is_late": {0: "Tepat waktu", 1: "Terlambat"}}))
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.barplot(data=rv, x="is_late", y="review_score", hue="is_late",
                    palette=["#5cb85c", "#d9534f"], legend=False, ax=ax)
        for i, v in enumerate(rv["review_score"]):
            ax.text(i, v + 0.05, f"{v:.2f}", ha="center")
        ax.set_ylim(0, 5)
        ax.set_xlabel("")
        ax.set_ylabel("Rata-rata Review Score")
        st.pyplot(fig)
        if len(rv) == 2:
            st.write(f"Selisih skor: **{rv['review_score'].iloc[0] - rv['review_score'].iloc[1]:.2f}** poin.")

    st.subheader("Lama Pengiriman vs Review Score per State")
    if not state_stats.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.scatterplot(data=state_stats, x="avg_delivery_days", y="avg_review", size="total_orders",
                        sizes=(40, 600), alpha=0.7, legend=False, ax=ax)
        for _, r in state_stats.iterrows():
            ax.annotate(r["customer_state"], (r["avg_delivery_days"], r["avg_review"]),
                        fontsize=9, ha="center", va="center")
        ax.set_xlabel("Rata-rata Lama Pengiriman (hari)")
        ax.set_ylabel("Rata-rata Review Score")
        st.pyplot(fig)

st.caption("Sumber data: E-Commerce Public Dataset (Olist).")
