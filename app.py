import streamlit as st
import calendar
from datetime import date
import random

# ================= 页面基础设置 =================
st.set_page_config(page_title="🥑 合租生活管家", page_icon="🌿", layout="wide")

# 自定义绿色可爱风 CSS
st.markdown("""
    <style>
    .stApp { background-color: #f0f9f0; }
    h1, h2, h3 { color: #2e7d32; font-family: 'Comic Sans MS', cursive, sans-serif; }
    .stButton>button { background-color: #81c784; color: white; border-radius: 20px; border: none; padding: 10px 20px; font-weight: bold; }
    .stButton>button:hover { background-color: #66bb6a; color: white; }
    .stSelectbox, .stTextInput, .stNumberInput { border-radius: 10px; }
    .css-1r6slb0, .css-1n76uvr { background-color: #ffffff; border-radius: 15px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); }
    .item-available { color: #000000; font-weight: bold; }
    .item-unavailable { color: #9e9e9e; text-decoration: line-through; }
    </style>
""", unsafe_allow_html=True)

st.title("🥑 我们的合租生活管家 🌿")

# ================= 初始化数据 (Session State) =================
if 'initialized' not in st.session_state:
    st.session_state.users = ['柴犬 🐕', '博美 🐶', '狸花 🐈', '布偶 🐱']
    st.session_state.current_year = 2026
    st.session_state.current_month = 9
    
    # 1. 模拟费用数据 (2026年1-8月，每月1000水电)
    st.session_state.bills = {}
    for m in range(1, 9):
        st.session_state.bills[(2026, m, 1)] = 1000.0
    
    # 2. 模拟公共物品数据
    st.session_state.items = {
        "扫帚": {"status": "available", "user": ""},
        "拖把": {"status": "in_use", "user": "柴犬 🐕"},
        "厨房纸巾": {"status": "available", "user": ""},
        "炒锅": {"status": "in_use", "user": "狸花 🐈"},
        "案板": {"status": "available", "user": ""},
        "洗洁精": {"status": "available", "user": ""}
    }
    
    # 3. 室友公约
    st.session_state.rules = """一、保持公共区域干净卫生 🧹
二、晚上12点后保持安静 🤫
三、月末结清公共费用 💰
四、每周打扫卫生 🧽
五、好好吃饭 🍚"""
    
    st.session_state.initialized = True

# ================= 侧边栏设置 =================
with st.sidebar:
    st.header("⚙️ 基础设置")
    st.write("📅 **当前模拟时间：2026年9月**")
    
    view_month = st.selectbox("选择查看2026年月份", range(1, 13), index=8) # 默认9月
    
    st.subheader("👥 室友管理")
    users_str = st.text_area("编辑室友代号（逗号分隔）", value=",".join(st.session_state.users))
    if st.button("更新室友名单"):
        st.session_state.users = [u.strip() for u in users_str.split(',') if u.strip()]
        st.success("名单已更新！")

# ================= 主体内容 (四个功能模块) =================
tab1, tab2, tab3, tab4 = st.tabs(["💰 费用分摊", "🧹 清洁排班", "📦 物品登记", "📜 室友公约"])

# ----------------- 功能1：费用AA分摊 -----------------
with tab1:
    st.header(f"💰 2026年 {view_month}月 费用日历")
    
    # 计算本月总费用
    month_bills = {k: v for k, v in st.session_state.bills.items() if k[0] == 2026 and k[1] == view_month}
    total_expense = sum(month_bills.values())
    per_person = total_expense / len(st.session_state.users) if len(st.session_state.users) > 0 else 0
    
    col1, col2 = st.columns(2)
    col1.metric("本月需结清总费用", f"¥ {total_expense:.2f}")
    col2.metric(f"每人需AA分摊 ({len(st.session_state.users)}人)", f"¥ {per_person:.2f}")
    
    # 记账输入
    with st.expander("➕ 添加/修改单日费用"):
        with st.form("bill_form"):
            b_day = st.number_input("日期 (日)", min_value=1, max_value=calendar.monthrange(2026, view_month)[1], value=1)
            b_amount = st.number_input("金额 (元)", min_value=0.0, value=1000.0)
            if st.form_submit_button("确认记账"):
                st.session_state.bills[(2026, view_month, b_day)] = b_amount
                st.rerun()

    # 日历展示
    st.markdown("### 📅 本月花销日历")
    cal = calendar.monthcalendar(2026, view_month)
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    
    # 表头
    cols = st.columns(7)
    for i, day_name in enumerate(weekdays):
        cols[i].markdown(f"**{day_name}**")
        
    # 日历网格
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                amount = st.session_state.bills.get((2026, view_month, day), 0)
                if amount > 0:
                    cols[i].success(f"{day}日\n\n¥{amount}")
                else:
                    cols[i].info(f"{day}日")

# ----------------- 功能2：清洁值日排班 -----------------
with tab2:
    st.header("🧹 清洁值日排班表")
    st.write("规则：每周安排两人打扫，保证四周内每人打扫次数相同。")
    
    if st.button("🎲 生成本月排班表 (2026年9月)"):
        users = st.session_state.users
        if len(users) >= 2:
            # 保证每个人均匀分配
            pool = users * 2 # 4周，每周2人，共需8人次。4个人每人2次刚好
            random.shuffle(pool)
            st.session_state.schedule = {
                "第一周": [pool[0], pool[1]],
                "第二周": [pool[2], pool[3]],
                "第三周": [pool[4], pool[5]],
                "第四周": [pool[6], pool[7]]
            }
        else:
            st.warning("人数不足，无法排班")

    if 'schedule' in st.session_state:
        for week, persons in st.session_state.schedule.items():
            st.markdown(f"**{week}**： 🧼 {persons[0]} & 🧽 {persons[1]}")
    else:
        # 默认展示9月模拟数据
        st.markdown("**第一周**： 🧼 柴犬 🐕 & 🧽 狸花 🐈")
        st.markdown("**第二周**： 🧼 博美 🐶 & 🧽 布偶 🐱")
        st.markdown("**第三周**： 🧼 柴犬 🐕 & 🧽 布偶 🐱")
        st.markdown("**第四周**： 🧼 博美 🐶 & 🧽 狸花 🐈")

# ----------------- 功能3：公共物品登记 -----------------
with tab3:
    st.header("📦 公共物品登记与提醒")
    
    # 添加新物品
    with st.form("add_item"):
        new_item = st.text_input("新增公共物品名称")
        if st.form_submit_button("添加物品") and new_item:
            st.session_state.items[new_item] = {"status": "available", "user": ""}
            st.rerun()

    st.markdown("### 当前物品状态")
    # 显示物品状态
    for item, info in st.session_state.items.items():
        col1, col2, col3 = st.columns([2, 2, 2])
        
        # 状态显示
        if info["status"] == "available":
            col1.markdown(f"<span class='item-available'>✅ {item} (可用)</span>", unsafe_allow_html=True)
        else:
            col1.markdown(f"<span class='item-unavailable'>🚫 {item} (正在被 {info['user']} 使用)</span>", unsafe_allow_html=True)
            
        # 状态修改
        new_status = col2.selectbox("更改状态", ["可用", "使用中"], key=f"status_{item}", index=0 if info["status"]=="available" else 1)
        selected_user = col3.selectbox("使用者", [""] + st.session_state.users, key=f"user_{item}", index=0 if info["user"]=="" else st.session_state.users.index(info["user"])+1)
        
        if new_status == "可用" and info["status"] != "available":
            st.session_state.items[item] = {"status": "available", "user": ""}
            st.rerun()
        elif new_status == "使用中" and selected_user != "":
            st.session_state.items[item] = {"status": "in_use", "user": selected_user}
            if info["status"] == "available" or info["user"] != selected_user:
                st.rerun()

# ----------------- 功能4：室友公约 -----------------
with tab4:
    st.header("📜 室友公约")
    st.write("有需要修改的条款请直接在下方编辑并保存。")
    
    edited_rules = st.text_area("公约内容", value=st.session_state.rules, height=200)
    if st.button("💾 保存公约"):
        st.session_state.rules = edited_rules
        st.success("公约已更新！")
        
    st.markdown("### 📌 当前公约展示")
    st.info(st.session_state.rules)
