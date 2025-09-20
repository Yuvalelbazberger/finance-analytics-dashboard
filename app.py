import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Mini Finance Dashboard", page_icon="📊", layout="wide")
st.title("📊 Mini Finance Dashboard")

ticker = st.text_input("בחר מניה/קריפטו (למשל NVDA, AAPL, TSLA, BTC-USD):", "NVDA")
period = st.selectbox("בחר תקופה", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
col_choice = st.selectbox("בחר עמודה לתצוגה", ["Close", "Adj Close", "Volume"], index=0)

@st.cache_data(ttl=60 * 60)
def load_data(tkr: str, per: str) -> pd.DataFrame:
    # auto_adjust=False כדי לקבל גם Adj Close
    df = yf.download(tkr, period=per, auto_adjust=False)
    return df

if ticker:
    data = load_data(ticker, period)

    if data.empty:
        st.warning("לא נמצאו נתונים לטיקר הזה. נסה טיקר אחר.")
    else:
        if col_choice not in data.columns:
            st.info(f"'{col_choice}' לא קיים בנתונים. מציג 'Close' במקום.")
            col_choice = "Close"

        st.subheader(f"גרף {col_choice} — {ticker}")
        st.line_chart(data[col_choice])

        series = data[col_choice].dropna().astype(float)
        first = float(series.iloc[0])
        last = float(series.iloc[-1])

        pct_return = (last / first - 1.0) * 100.0
        mean_val = float(series.mean())
        vol_pct = float(series.pct_change().std() * 100.0)  # תנודתיות משוערת

        st.subheader("📊 סטטיסטיקות בסיסיות")
        c1, c2, c3 = st.columns(3)
        c1.metric("שינוי מצטבר %", f"{pct_return:.2f}%")
        c2.metric(f"ממוצע {col_choice}", f"{mean_val:.2f}")
        c3.metric("תנודתיות %", f"{vol_pct:.2f}%")

        st.subheader("⬇️ הורדת נתונים")
        export_df = data.reset_index()  # כדי שה-Date יהיה עמודה בקובץ
        csv_bytes = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="הורד CSV של כל הנתונים",
            data=csv_bytes,
            file_name=f"{ticker}_{period}.csv",
            mime="text/csv",
        )
else:
    st.info("הקלד טיקר למעלה כדי להתחיל (למשל NVDA, AAPL, TSLA, BTC-USD).")
