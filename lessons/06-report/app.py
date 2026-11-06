"""Lesson 06: the dashboard. Reads output/workshop.db every 2 seconds.

    streamlit run lessons/06-report/app.py

Start it before lesson 05 and watch the agents fill it. Or fill it from the
recorded run, no network needed:

    python lessons/05-explore-competitors/explore.py --replay
"""

import os
import sqlite3
import sys

import altair as alt
import pandas as pd
import streamlit as st

REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO)

from shared.store import DB  # noqa: E402

FINISHED = ("done", "out of steps", "blocked", "error")

st.set_page_config(page_title="Competitor pricing", page_icon=":bar_chart:", layout="wide")


def query(sql, args=()):
    """A fresh read-only connection every time: the agents keep writing."""
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=5)
    try:
        return pd.read_sql_query(sql, db, params=args)
    finally:
        db.close()


if not os.path.exists(DB):
    st.title("Competitor pricing")
    st.info("No data yet. Run lesson 05, or replay the recorded run:\n\n"
            "`python lessons/05-explore-competitors/explore.py --replay`")
    st.stop()


# Sidebar: which run. By default, follow the newest one, so a run started
# while the dashboard is open shows up by itself.
with st.sidebar:
    st.header("Run")
    follow = st.toggle("Follow the newest run", value=True)
    runs = query("SELECT r.run_id, r.source, r.model, COUNT(a.site) AS competitors FROM runs r "
                 "LEFT JOIN agents a USING (run_id) GROUP BY r.run_id ORDER BY r.started DESC")
    labels = [f"{r.run_id} · {r.source} · {r.competitors} competitors" for r in runs.itertuples()]
    picked = st.selectbox("Or pick one", labels, disabled=follow)
    st.caption(f"Reading {os.path.relpath(DB, REPO)} every 2 seconds.")


def card(col, a):
    with col:
        done = a.status.startswith(FINISHED)
        icon = ":white_check_mark:" if a.status == "done" else ":warning:" if done else ":hourglass_flowing_sand:"
        st.markdown(f"**{a.company}** {icon}")
        st.caption(a.status)
        # Empty fields come back from pandas as NaN (or None), not "".
        shot = os.path.join(REPO, a.screenshot) if pd.notna(a.screenshot) else None
        if shot and os.path.exists(shot):
            st.image(shot, width="stretch")
        elif pd.notna(a.url):
            st.caption(f"on {a.url}")
        if pd.notna(a.why):
            st.caption(f"_{a.why}_")


@st.fragment(run_every="2s")
def dashboard():
    runs = query("SELECT run_id, source, model FROM runs ORDER BY started DESC")
    if runs.empty:
        st.info("No runs yet.")
        return
    run = runs.iloc[0] if follow else runs.iloc[labels.index(picked)]
    agents = query("SELECT * FROM agents WHERE run_id=? ORDER BY started", (run.run_id,))
    prices = query("SELECT * FROM prices WHERE run_id=?", (run.run_id,))

    finished = sum(s.startswith(FINISHED) for s in agents.status)
    st.title("Competitor pricing")
    st.caption(f"run {run.run_id} · {run.source} · model {run.model}")

    m = st.columns(4)
    m[0].metric("Competitors done", f"{finished} / {len(agents)}")
    m[1].metric("Prices found", len(prices))
    m[2].metric("Browser units", int(agents.units.fillna(0).sum()))
    m[3].metric("Model cost", f"${agents.model_usd.fillna(0).sum():.4f}")

    # One card per competitor: where it is and what it's looking at.
    per_row = 5
    for i in range(0, len(agents), per_row):
        cols = st.columns(per_row)
        for col, a in zip(cols, agents.iloc[i:i + per_row].itertuples()):
            card(col, a)

    if prices.empty:
        st.info("Waiting for the first prices...")
        return

    # The same price can be seen on two steps (before and after a toggle
    # that didn't change it). Keep one.
    prices = prices.drop_duplicates(subset=["company", "plan", "amount", "period"])
    plans = prices[(prices.kind == "subscription") & prices.usd_month.notna() & (prices.usd_month > 0)]

    left, right = st.columns(2)
    with left:
        st.subheader("Entry price")
        st.caption("Cheapest paid plan per month, USD")
        entry = plans.groupby("company", as_index=False).usd_month.min()
        st.altair_chart(
            alt.Chart(entry).mark_bar().encode(
                x=alt.X("usd_month:Q", title="USD / month"),
                y=alt.Y("company:N", sort="x", title=None),
                tooltip=["company", "usd_month"],
            ),
            width="stretch",
        )
    with right:
        st.subheader("Plan ladder")
        st.caption("Every subscription plan, per month, USD")
        st.altair_chart(
            alt.Chart(plans).mark_circle(size=120).encode(
                x=alt.X("usd_month:Q", title="USD / month", scale=alt.Scale(type="log")),
                y=alt.Y("company:N", title=None),
                color=alt.Color("billing:N", title="billed"),
                tooltip=["company", "plan", "amount", "period", "usd_month"],
            ),
            width="stretch",
        )

    # Annual discount: plans we saw both ways. That's the toggle from lesson 04.
    monthly = plans[plans.billing == "monthly"].groupby(["company", "plan"]).usd_month.max()
    annual = plans[plans.billing == "annual"].groupby(["company", "plan"]).usd_month.min()
    both = pd.concat([monthly.rename("monthly"), annual.rename("annual")], axis=1).dropna().reset_index()
    if not both.empty:
        both["discount"] = (1 - both.annual / both.monthly).map(lambda d: f"{d:.0%}")
        st.subheader("Annual discount")
        st.caption("Plans seen with both monthly and annual billing")
        st.dataframe(both, hide_index=True, width="stretch")

    st.subheader("Every price")
    st.caption("As shown on the page, and the comparable form the charts use")
    st.dataframe(
        prices[["company", "plan", "amount", "currency", "period", "usd_month", "billing", "kind", "step", "url"]],
        hide_index=True,
        width="stretch",
        column_config={"url": st.column_config.LinkColumn("page")},
    )

    st.subheader("What the research cost")
    cost = agents[["company", "status", "page_status", "step", "browser_seconds", "units", "model_usd"]]
    st.dataframe(cost.rename(columns={"step": "steps", "page_status": "page status"}), hide_index=True, width="stretch")


dashboard()
