import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🗳️ ECI Electors Revision Analysis (2024 vs Post-SIR)")

try:
    # 1. Load data
    df_before = pd.read_excel("before.xlsx")
    df_after = pd.read_excel("after.xlsx")

    # Clean column headers
    df_before.columns = df_before.columns.astype(str).str.strip()
    df_after.columns = df_after.columns.astype(str).str.strip()

    # 2. Add an "Alignment Key" column to fix spelling/formatting mismatches
    # This converts names to lowercase and removes all extra internal spaces
    df_before["Clean_AC_Name"] = df_before["AC Name"].astype(str).str.lower().str.strip().str.replace(r'\s+', ' ', regex=True)
    df_after["Clean_AC_Name"] = df_after["AC Name"].astype(str).str.lower().str.strip().str.replace(r'\s+', ' ', regex=True)

    # Convert elector columns to numbers
    df_before["total"] = pd.to_numeric(df_before["total"], errors='coerce')
    df_after["TOTAL"] = pd.to_numeric(df_after["TOTAL"], errors='coerce')

    # 3. Filter and prepare data for merging
    df_b = df_before[["AC Name", "Clean_AC_Name", "total"]].rename(columns={"total": "2024_Electors", "AC Name": "AC_Name_2024"})
    df_a = df_after[["AC Name", "Clean_AC_Name", "TOTAL"]].rename(columns={"TOTAL": "Post_SIR_Electors", "AC Name": "AC_Name_Post"})
    
    # Merge using our hidden standardized clean key
    df = pd.merge(df_b, df_a, on="Clean_AC_Name", how="inner")
    df = df.dropna()

    # 4. Perform Analytics
    df["Net_Change"] = df["Post_SIR_Electors"] - df["2024_Electors"]
    df["Pct_Change"] = (df["Net_Change"] / df["2024_Electors"]) * 100

    # Clean up the display name
    df["Assembly Constituency"] = df["AC_Name_2024"]

    # 5. Dashboard Layout: Top Metrics
    st.write("## 📊 Key Highlights")
    col1, col2, col3, col4 = st.columns(4)
    
    max_addition = df.loc[df["Net_Change"].idxmax()]
    max_deletion = df.loc[df["Net_Change"].idxmin()]
    max_pct_add = df.loc[df["Pct_Change"].idxmax()]
    max_pct_del = df.loc[df["Pct_Change"].idxmin()]

    col1.metric("Max Additions (Absolute)", f"{int(max_addition['Net_Change'])}", max_addition["Assembly Constituency"])
    col2.metric("Max Deletions (Absolute)", f"{int(max_deletion['Net_Change'])}", max_deletion["Assembly Constituency"])
    col3.metric("Max Growth (%)", f"{max_pct_add['Pct_Change']:.2f}%", max_pct_add["Assembly Constituency"])
    col4.metric("Max Drop (%)", f"{max_pct_del['Pct_Change']:.2f}%", max_pct_del["Assembly Constituency"])

    st.write("---")

    # 6. Dashboard Layout: Visualizations & Data Table
    left_chart, right_table = st.columns([3, 2])

    with left_chart:
        st.write("### Net Change by Constituency")
        df_sorted = df.sort_values(by="Net_Change")
        st.bar_chart(df_sorted.set_index("Assembly Constituency")["Net_Change"])

        st.write("### Percentage Change (%)")
        st.bar_chart(df_sorted.set_index("Assembly Constituency")["Pct_Change"])

    with right_table:
        st.write("### Complete Analyzed Dataset")
        df_display = df[["Assembly Constituency", "2024_Electors", "Post_SIR_Electors", "Net_Change", "Pct_Change"]].copy()
        df_display["Pct_Change"] = df_display["Pct_Change"].map("{:.2f}%".format)
        st.dataframe(df_display, height=500)

except Exception as e:
    st.error(f"An error occurred during calculation: {e}")