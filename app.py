import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="منصة تحليلات الفوركس والشموع المباشرة", page_icon="📈", layout="wide")

# تنسيق واجهة احترافية مظلمة تشبه منصات التداول الكبرى
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; background-color: #00CC96; color: white; font-weight: bold; border-radius: 5px; height: 45px; }
    </style>
""", unsafe_allow_html=True)

st.title("📈 المنصة الحية لتحليلات فوركس والشموع اليابانية الاحترافية")
st.write("مخصصة لتحليل أزواج الفوركس الحية وتقديم إشارات دقيقة ومباشرة بناءً على حركة السعر والزخم.")

# شريط الأدوات الجانبي لإعدادات الفوركس
st.sidebar.header("🛠️ إعدادات سوق الفوركس")

forex_pairs = {
    "EUR/USD (يورو / دولار أمريكي)": "EURUSD=X",
    "GBP/USD (سترلينج / دولار أمريكي)": "GBPUSD=X",
    "USD/JPY (دولار / ين ياباني)": "USDJPY=X",
    "AUD/USD (أسترالي / دولار أمريكي)": "AUDUSD=X",
    "USD/CHF (دولار / فرنك سويسري)": "USDCHF=X"
}

selected_name = st.sidebar.selectbox("اختر زوج العملات", list(forex_pairs.keys()))
ticker_symbol = forex_pairs[selected_name]

tf_dict = {"دقيقة واحدة (1m)": "1m", "5 دقائق (5m)": "5m", "1 ساعة (1h)": "1h", "يومي (1d)": "1d"}
selected_tf = st.sidebar.selectbox("الإطار الزمني", list(tf_dict.keys()))
tf_code = tf_dict[selected_tf]

# دالة حساب مؤشر القوة النسبية RSI لتصفية الإشارات الكاذبة
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

with st.spinner(f"جاري جلب وتحليل بيانات {selected_name} الحية..."):
    try:
        # جلب البيانات الحية من السوق
        data = yf.download(ticker_symbol, period="5d", interval=tf_code, progress=False)
        
        if data.empty or len(data) < 25:
            st.warning("⚠️ السوق مغلق حالياً أو البيانات غير كافية لهذا الإطار. ستعمل البيانات بشكل حي بمجرد افتتاح السوق يوم الإثنين.")
        else:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
                
            current_price = float(data['Close'].iloc[-1])
            prev_price = float(data['Close'].iloc[-2])
            
            # حساب المتوسط المتحرك الأسي EMA ومؤشر RSI الاستراتيجي
            data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
            data['RSI'] = calculate_rsi(data['Close'])
            
            current_ema = float(data['EMA_20'].iloc[-1])
            current_rsi = float(data['RSI'].iloc[-1])
            
            # استراتيجية دقيقة ومحترفة لتحديد الدخول (Strong Buy / Strong Sell)
            if current_price > current_ema and 45 < current_rsi < 70:
                signal_type = "STRONG BUY 🟢"
                signal_color = "#00CC96"
                signal_desc = "السعر يتداول أعلى المتوسط الأسي مع زخم صاعد مؤكد في مؤشر RSI."
            elif current_price < current_ema and 30 < current_rsi < 55:
                signal_type = "STRONG SELL 🔴"
                signal_color = "#EF553B"
                signal_desc = "السعر يتداول أدنى المتوسط الأسي مع ضغط بيعي مؤكد في مؤشر RSI."
            else:
                signal_type = "منطقة مراقبة / حياد 🟡"
                signal_color = "#FFA15A"
                signal_desc = "السوق في منطقة تذبذب حالياً، يفضل الانتظار لاختراق واضح."

            # عرض مؤشرات السوق الحية في الأعلى
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("السعر الحالي", f"{current_price:.5f}", f"{((current_price - prev_price)/prev_price)*100:.2f}%")
            c2.metric("حالة الإشارة الاستراتيجية", signal_type)
            c3.metric("مؤشر الزخم (RSI)", f"{current_rsi:.1f}")
            c4.metric("المتوسط الأسي (EMA 20)", f"{current_ema:.5f}")
            
            st.info(f"تحليل الاستراتيجية المباشر: {signal_desc}")
            
            # --- رسم الشموع اليابانية الاحترافية الحية ---
            st.subheader(f"🕯️ الشارت المباشر لـ {selected_name} ({selected_tf})")
            
            fig = go.Figure()

            # إضافة الشموع اليابانية الملونة
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='الشموع اليابانية',
                increasing_line_color='#00CC96', decreasing_line_color='#EF553B'
            ))
            
            # إضافة خط المتوسط المتحرك الأسي EMA
            fig.add_trace(go.Scatter(
                x=data.index, 
                y=data['EMA_20'], 
                mode='lines', 
                name='EMA 20', 
                line=dict(color='#2962FF', width=2)
            ))
            
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                height=550,
                margin=dict(l=10, r=10, t=10, b=10),
                template="plotly_dark",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"حدث خطأ أثناء جلب بيانات السوق: {e}")
