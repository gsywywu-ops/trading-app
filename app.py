import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="منصة التداول الحقيقية المباشرة", page_icon="📈", layout="wide")

st.title("📈 المنصة الحقيقية لتحليلات الفوركس والخيارات الثنائية (بيانات حية من السوق)")
st.write("هذا التطبيق متصل مباشرة بالأسواق المالية لجلب الأسعار الفعلية وحساب المؤشرات الفنية بدقة.")

st.sidebar.header("🛠️ إعدادات الأسواق المباشرة")
market_type = st.sidebar.selectbox("اختر السوق", ["الفوركس والذهب (Forex/Gold)", "الخيارات الثنائية (Binary Options)"])

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

if market_type == "الفوركس والذهب (Forex/Gold)":
    st.sidebar.subheader("إعدادات الفوركس الحية")
    pair_dict = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "Gold (XAU/USD)": "GC=F"
    }
    selected_name = st.sidebar.selectbox("اختر الأصل المالي", list(pair_dict.keys()))
    ticker_symbol = pair_dict[selected_name]
    
    tf_dict = {"1 دقيقة": "1m", "5 دقائق": "5m", "1 ساعة": "1h", "يومي": "1d"}
    selected_tf_name = st.sidebar.selectbox("اختر الإطار الزمني", list(tf_dict.keys()))
    tf_code = tf_dict[selected_tf_name]
    
    analyze_btn = st.sidebar.button("تحليلات السوق الحية الآن")
    
    if analyze_btn:
        with st.spinner(f"جاري الاتصال بالسوق وجلب بيانات {selected_name} الحية..."):
            try:
                data = yf.download(ticker_symbol, period="5d", interval=tf_code, progress=False)
                
                if data.empty or len(data) < 15:
                    st.error("عذراً، البيانات غير متوفرة حالياً لهذا الإطار الزمني، جرب إطاراً زمنياً آخر.")
                else:
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.get_level_values(0)
                        
                    current_price = float(data['Close'].iloc[-1])
                    rsi_series = calculate_rsi(data['Close'])
                    current_rsi = float(rsi_series.iloc[-1])
                    
                    if current_rsi < 35:
                        signal = "شراء قوية (STRONG BUY) 🟢"
                        sl = round(current_price - 0.0030, 4)
                        tp = round(current_price + 0.0050, 4)
                    elif current_rsi > 65:
                        signal = "بيع قوية (STRONG SELL) 🔴"
                        sl = round(current_price + 0.0030, 4)
                        tp = round(current_price - 0.0050, 4)
                    else:
                        signal = "منطقة حيادية (NEUTRAL) 🟡"
                        sl = "غير محدد"
                        tp = "غير محدد"

                    st.success(f"تم تحليل السعر الحقيقي لـ {selected_name} بنجاح!")
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("السعر الحالي من السوق", f"{current_price:.4f}")
                    col2.metric("التوصية الفنية", signal)
                    col3.metric("مؤشر القوة (RSI)", f"{current_rsi:.1f}")
                    col4.metric("وقف الخسارة المقترح", str(sl))
                    col5.metric("هدف الربح المقترح", str(tp))
                    
                    st.line_chart(data['Close'])
                    st.info("💡 تم حساب هذه القيم تلقائياً من حركة الأسعار الفعلية في السوق اللحظي.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء جلب البيانات الحية: {e}")

else:
    st.sidebar.subheader("إعدادات الخيارات الثنائية الحية")
    binary_asset = st.sidebar.selectbox("اختر زوج الخيارات", ["EUR/USD", "GBP/USD", "AUD/USD"])
    binary_symbol = f"{binary_asset[:3]}{binary_asset[4:]}=X"
    
    expiry = st.sidebar.selectbox("فريم الصفقة القصيرة", ["1 دقيقة", "2 دقيقة", "3 دقائق"])
    
    binary_btn = st.sidebar.button("توليد إشارة الخيارات الثنائية الفورية")
    
    if binary_btn:
        with st.spinner("جاري فحص الزخم السعري الفوري للفريمات القصيرة..."):
            try:
                b_data = yf.download(binary_symbol, period="1d", interval="1m", progress=False)
                if isinstance(b_data.columns, pd.MultiIndex):
                    b_data.columns = b_data.columns.get_level_values(0)
                    
                if not b_data.empty:
                    last_close = b_data['Close'].iloc[-1]
                    prev_close = b_data['Close'].iloc[-2]
                    
                    if last_close > prev_close:
                        b_signal = "صعود (CALL 🟢)"
                    else:
                        b_signal = "هبوط (PUT 🔴)"
                        
                    st.success(f"🎯 إشارة الخيارات الثنائية الفورية لـ {binary_asset} (فريم {expiry}):")
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("توجيه الصفقة", b_signal)
                    c2.metric("سعر المرجعي الحالي", f"{last_close:.5f}")
                    c3.metric("مدة العقد", expiry)
                    
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    st.warning(f"⏱️ توقيت الدخول المقترح فوراً عند الساعة: **{current_time}** (لمدة {expiry}). تداول بحذر شديد نظراً لارتفاع المخاطر.")
                else:
                    st.error("تعذر جلب بيانات الفريم القصير حالياً.")
            except Exception as e:
                st.error(f"خطأ في الاتصال: {e}")
    
