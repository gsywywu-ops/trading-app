import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="منصة التداول بالشموع اليابانية", page_icon="📈", layout="wide")

st.title("📈 المنصة الحية للشموع اليابانية وتحليلات السوق المباشرة")
st.write("هذه المنصة تعرض الرسوم البيانية للشموع اليابانية الحقيقية مع استراتيجية دقيقة ومباشرة لتأكيد الاتجاه.")

st.sidebar.header("🛠️ إعدادات الأسواق المباشرة")
market_choice = st.sidebar.selectbox("اختر القسم", ["الفوركس والذهب (Forex & Gold)", "الخيارات الثنائية (Binary Options)"])

# دالة حساب مؤشر RSI
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

if market_choice == "الفوركس والذهب (Forex & Gold)":
    st.sidebar.subheader("إعدادات الفوركس والشموع اليابانية")
    pair_dict = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "Gold (XAU/USD)": "GC=F"
    }
    selected_name = st.sidebar.selectbox("اختر زوج العملات / الذهب", list(pair_dict.keys()))
    ticker_symbol = pair_dict[selected_name]
    
    tf_dict = {"1 دقيقة": "1m", "5 دقائق": "5m", "1 ساعة": "1h", "يومي": "1d"}
    selected_tf = st.sidebar.selectbox("الإطار الزمني للشموع", list(tf_dict.keys()))
    tf_code = tf_dict[selected_tf]
    
    run_analysis = st.sidebar.button("عرض شارت الشموع واستراتيجية التأكيد")
    
    if run_analysis:
        with st.spinner(f"جاري جلب بيانات الشموع اليابانية لـ {selected_name}..."):
            try:
                data = yf.download(ticker_symbol, period="5d", interval=tf_code, progress=False)
                
                if data.empty or len(data) < 20:
                    st.error("البيانات غير كافية لهذا الإطار، جرب إطاراً زمنياً آخر.")
                else:
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.get_level_values(0)
                        
                    current_price = float(data['Close'].iloc[-1])
                    
                    # حساب المؤشرات
                    data['SMA_20'] = data['Close'].rolling(window=20).mean()
                    data['RSI'] = calculate_rsi(data['Close'])
                    
                    current_sma = float(data['SMA_20'].iloc[-1])
                    current_rsi = float(data['RSI'].iloc[-1])
                    
                    # استراتيجية تأكيد الاتجاه
                    if current_price > current_sma and current_rsi < 65 and current_rsi > 40:
                        strategy_signal = "شراء مؤكد (STRONG BUY) 🟢"
                        strategy_desc = "الشموع تتداول أعلى المتوسط المتحرك 20 مع زخم إيجابي في RSI."
                        sl = round(current_price - 0.0035, 4)
                        tp = round(current_price + 0.0060, 4)
                    elif current_price < current_sma and current_rsi > 35 and current_rsi < 60:
                        strategy_signal = "بيع مؤكد (STRONG SELL) 🔴"
                        strategy_desc = "الشموع تتداول أدنى المتوسط المتحرك 20 مع ضغط بيعي في RSI."
                        sl = round(current_price + 0.0035, 4)
                        tp = round(current_price - 0.0060, 4)
                    else:
                        strategy_signal = "منطقة تذبذب / حياد (NEUTRAL) 🟡"
                        strategy_desc = "السوق يعيد اختبار مستويات المتوسطات، يفضل الانتظار لتأكيد الإغلاق."
                        sl = "غير محدد"
                        tp = "غير محدد"

                    st.success(f"✅ تم تحميل تحليل الشموع واستراتيجية التأكيد لـ {selected_name} بنجاح!")
                    
                    # عرض المقاييس
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("السعر اللحظي", f"{current_price:.4f}")
                    col2.metric("إشارة الاستراتيجية", strategy_signal)
                    col3.metric("مؤشر RSI", f"{current_rsi:.1f}")
                    col4.metric("المتوسط المتحرك (SMA 20)", f"{current_sma:.4f}")
                    
                    st.info(f"📌 **تحليل الشموع والاستراتيجية:** {strategy_desc}")
                    
                    # --- رسم الشموع اليابانية الحقيقية باستخدام Plotly ---
                    st.subheader(f"🕯️ الرسم البياني للشموع اليابانية لـ {selected_name} ({selected_tf})")
                    
                    fig = go.Figure(data=[go.Candlestick(
                        x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'],
                        name='الشموع اليابانية'
                    )])
                    
                    # إضافة خط المتوسط المتحرك على الشارت لتكتمل الاستراتيجية
                    fig.add_trace(go.Scatter(
                        x=data.index, 
                        y=data['SMA_20'], 
                        mode='lines', 
                        name='المتوسط (SMA 20)', 
                        line=dict(color='orange', width=2)
                    ))
                    
                    fig.update_layout(
                        xaxis_rangeslider_visible=False,
                        height=500,
                        margin=dict(l=20, r=20, t=20, b=20),
                        template="plotly_dark"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.warning(f"🎯 **توصية إدارة المخاطر:** وقف الخسارة (SL): **{sl}** | هدف الربح (TP): **{tp}**")
            except Exception as e:
                st.error(f"حدث خطأ في جلب بيانات الشموع: {e}")

else:
    st.sidebar.subheader("إعدادات الخيارات الثنائية والشموع السريعة")
    b_pair = st.sidebar.selectbox("اختر الأصل", ["EUR/USD", "GBP/USD", "AUD/USD"])
    b_sym = f"{b_pair[:3]}{b_pair[4:]}=X"
    b_tf = st.sidebar.selectbox("فريم الصفقات السريعة", ["1 دقيقة", "2 دقيقة", "3 دقائق"])
    
    b_btn = st.sidebar.button("فحص شموع الخيارات الثنائية")
    
    if b_btn:
        with st.spinner("جاري فحص الشموع السريعة..."):
            try:
                b_df = yf.download(b_sym, period="1d", interval="1m", progress=False)
                if isinstance(b_df.columns, pd.MultiIndex):
                    b_df.columns = b_df.columns.get_level_values(0)
                    
                if not b_df.empty:
                    close_prices = b_df['Close']
                    last_c = close_prices.iloc[-1]
                    prev_c = close_prices.iloc[-2]
                    
                    if last_c > prev_c:
                        b_direction = "صعود (CALL 🟢)"
                        b_reason = "تأكيد إغلاق شمعة دقيقة صاعدة بقوة."
                    else:
                        b_direction = "هبوط (PUT 🔴)"
                        b_reason = "تأكيد إغلاق شمعة دقيقة هابطة بضغط بيعي."
                        
                    st.success(f"🎯 إشارة الخيارات الثنائية المؤكدة لـ {b_pair}:")
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("نوع العقد", b_direction)
                    c2.metric("السعر الحالي", f"{last_c:.5f}")
                    c3.metric("مدة العقد", b_tf)
                    
                    st.info(f"💡 **سبب التأكيد:** {b_reason}")
                    
                    # شارت شموع مصغر للخيارات الثنائية الأخيرة
                    st.subheader(f"🕯️ شارت الشموع السريعة لـ {b_pair}")
                    fig_b = go.Figure(data=[go.Candlestick(
                        x=b_df.tail(30).index,
                        open=b_df['Open'].tail(30),
                        high=b_df['High'].tail(30),
                        low=b_df['Low'].tail(30),
                        close=b_df['Close'].tail(30),
                        name='الشموع القصيرة'
                    )])
                    fig_b.update_layout(xaxis_rangeslider_visible=False, height=400, template="plotly_dark")
                    st.plotly_chart(fig_b, use_container_width=True)
                else:
                    st.error("تعذر تحميل البيانات.")
            except Exception as e:
                st.error(f"خطأ: {e}")
