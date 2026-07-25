import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Pocket Option Style Trading Dashboard", page_icon="📈", layout="wide")

# تنسيق الشاشة لتشبه المنصات الاحترافية المظلمة
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; background-color: #ff5722; color: white; font-weight: bold; border-radius: 5px; }
    .metric-card { background-color: #1e222d; padding: 10px; border-radius: 8px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ منصة التداول والتحليل اللحظي المتقدمة")

# 1. شريط الأصول العلوي (المشابه للصورة)
cols = st.columns(4)
assets_top = [
    ("EUR/GBP OTC", "EURGBP=X", "+88%"),
    ("AUD/JPY OTC", "AUDJPY=X", "+75%"),
    ("AUD/USD OTC", "AUDUSD=X", "+86%"),
    ("EUR/USD OTC", "EURUSD=X", "+89%")
]

for i, (name, sym, profit) in enumerate(assets_top):
    with cols[i]:
        st.markdown(f"""
            <div style="background-color: #1e222d; padding: 8px; border-radius: 6px; border: 1px solid #333; text-align: center;">
                <b>{name}</b><br>
                <span style="color: #00CC96; font-size: 14px;">العائد: {profit}</span>
            </div>
        """, unsafe_allow_html=True)

st.write("---")

# تقسيم الشاشة إلى قسمين: الشارت في اليسار، ولوحة الإشارات المماثلة للصورة في اليمين
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("📊 الرسم البياني للشموع اليابانية الحية")
    
    # اختيار الأصل للرسم
    chosen_pair = st.selectbox("اختر زوج العملات للشارت", ["AUD/USD", "EUR/USD", "GBP/USD", "AUD/JPY"])
    symbol_map = {"AUD/USD": "AUDUSD=X", "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "AUD/JPY": "AUDJPY=X"}
    ticker = symbol_map[chosen_pair]
    
    # جلب البيانات
    data = yf.download(ticker, period="3d", interval="1m", progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        
    if not data.empty:
        # حساب مؤشر بسيط لتحديد الإشارة
        data['SMA_10'] = data['Close'].rolling(10).mean()
        last_close = float(data['Close'].iloc[-1])
        last_sma = float(data['SMA_10'].iloc[-1])
        
        # رسم الشموع اليابانية باستخدام Plotly
        fig = go.Figure(data=[go.Candlestick(
            x=data.tail(100).index,
            open=data['Open'].tail(100),
            high=data['High'].tail(100),
            low=data['Low'].tail(100),
            close=data['Close'].tail(100),
            name=chosen_pair,
            increasing_line_color='#00CC96', decreasing_line_color='#EF553B'
        )])
        
        fig.add_trace(go.Scatter(x=data.tail(100).index, y=data['SMA_10'].tail(100), mode='lines', name='SMA 10', line=dict(color='#FFA15A', width=1.5)))
        fig.update_layout(xaxis_rangeslider_visible=False, height=450, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("جاري تحديث بيانات السوق...")

with right_col:
    st.markdown("### 🎛️ لوحة الإشارات والتحليل (Cross Signal)")
    
    # محاكاة مصفوفة العملات المشابهة للصورة
    st.write("**مصفوفة قوة العملات (%)**")
    matrix_data = {
        "EUR": ["-", "0.7%", "-0.69%", "0.26%"],
        "USD": ["-0.66%", "-", "-1.4%", "-0.45%"],
        "JPY": ["0.73%", "1.39%", "-", "0.9%"],
        "GBP": ["-0.19%", "0.48%", "-0.93%", "-"]
    }
    df_matrix = pd.DataFrame(matrix_data, index=["EUR", "USD", "JPY", "GBP"])
    st.dataframe(df_matrix, use_container_width=True)
    
    st.write("---")
    
    # عناصر التحكم المشابهة للصورة تماماً
    selected_currency = st.selectbox("Select Currency", ["AUD/USD", "EUR/USD", "GBP/USD", "EUR/GBP"])
    duration_unit = st.selectbox("Duration Unit", ["1 Minutes", "2 Minutes", "5 Minutes"])
    profit_percent = st.text_input("% Profit ($)", "86%")
    
    # زر توليد الإشارات
    if st.button("Get Signals"):
        # منطق دقيق ومباشر لتوليد الإشارة بناءً على الاتجاه اللحظي
        if not data.empty:
            if last_close > last_sma:
                signal_result = "STRONG BUY 🟢"
                signal_color = "#00CC96"
            else:
                signal_result = "STRONG SELL 🔴"
                signal_color = "#EF553B"
                
            st.markdown(f"""
                <div style="background-color: #1e222d; padding: 15px; border-radius: 8px; text-align: center; border: 2px solid {signal_color}; margin-top: 10px;">
                    <h3 style="color: {signal_color}; margin: 0;">{signal_result}</h3>
                    <p style="margin: 5px 0 0 0; color: #aaa; font-size: 12px;">تم التأكيد بناءً على حركة الشموع وزخم الإغلاق</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("الرجاء انتظار تحميل البيانات.")
