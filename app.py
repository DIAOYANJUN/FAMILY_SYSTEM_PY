import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import io
import base64

# 页面基础配置
st.set_page_config(page_title="温馨家庭系统", page_icon="🏡", layout="centered")

DATA_FILE = "family_data.json"

# 数据加载与保存
def load_data():
    if not os.path.exists(DATA_FILE):
        initial = {
            "checkins": {},
            "photos": [],
            "mailboxes": {"baba": [], "mama": [], "erzi": [], "meimei": []}
        }
        save_data(initial)
        return initial
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 用户与宠物配置
users = {
    "baba": {"name": "爸爸", "role": "父亲", "birthday": "12-23", "emoji": "👨", "pass": "baba123456"},
    "mama": {"name": "妈妈", "role": "母亲", "birthday": "07-15", "emoji": "👩", "pass": "mama123456"},
    "erzi": {"name": "儿子", "role": "儿子", "birthday": "05-03", "emoji": "👦", "pass": "erzi123456"},
    "meimei": {"name": "妹妹", "role": "妹妹", "birthday": "01-09", "emoji": "👧", "pass": "meimei123456"}
}

pets = {
    "lulu": {"name": "噜噜 🐾", "img": "static/lulu.jpeg", "desc": "我是噜噜！家里最活泼的小可爱，每天负责卖萌和迎接大家回家，最喜欢吃好吃的零食！"},
    "bubu": {"name": "布布 🐾", "img": "static/bubu.jpeg", "desc": "我是布布！性格温顺又粘人，是大家的贴心小棉袄，最喜欢在阳光下懒洋洋地睡大觉。"},
    "yier": {"name": "一二 🐾", "img": "static/yier.jpeg", "desc": "我是一二！行事雷厉风行，是家庭里的快乐源泉，每天都在元气满满地巡视领地！"}
}

# 登录状态管理
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

data = load_data()

# --- 登录界面 ---
if not st.session_state.logged_in_user:
    st.markdown("<h2 style='text-align: center; color: #ff7b93;'>🏡 温馨家庭系统登录</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username_input = st.text_input("账号 (baba / mama / erzi / meimei)")
        password_input = st.text_input("密码", type="password")
        if st.button("登 录", use_container_width=True):
            if username_input in users and users[username_input]["pass"] == password_input:
                st.session_state.logged_in_user = username_input
                st.rerun()
            else:
                st.error("账号或密码错误！")
else:
    current_user = st.session_state.logged_in_user
    user_info = users[current_user]

    # --- 侧边栏：宠物展示与简介 ---
    with st.sidebar:
        st.markdown(f"### 🐾 家庭宠物小窝")
        for pet_key, pet_info in pets.items():
            if os.path.exists(pet_info["img"]):
                st.image(pet_info["img"], width=100)
            else:
                st.write(f"[{pet_info['name']} 图片未找到]")
            st.markdown(f"**{pet_info['name']}**")
            with st.expander("查看简介"):
                st.write(pet_info["desc"])
            st.markdown("---")

    # --- 主界面头部 ---
    st.markdown(f"<h1 style='color: #ff7b93;'>🏡 温馨家庭系统</h1>", unsafe_allow_html=True)
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"欢迎您，**{user_info['emoji']} {user_info['name']}**！")
    with col_h2:
        if st.button("退出登录"):
            st.session_state.logged_in_user = None
            st.rerun()

    st.markdown("---")

    # --- 左右双列布局 ---
    left_col, right_col = st.columns(2)

    with left_col:
        # 1. 生日倒计时
        st.markdown("### 🎂 家人生日倒计时")
        today = datetime.now()
        for u_key, u_val in users.items():
            m, d = map(int, u_val["birthday"].split("-"))
            b_day = datetime(today.year, m, d)
            if b_day.date() < today.date():
                b_day = datetime(today.year + 1, m, d)
            days_left = (b_day - today).days
            status = "🎉 今天生日！" if days_left == 0 else f"还有 {days_left} 天"
            st.info(f"{u_val['emoji']} **{u_val['name']}** ({m}月{d}日) — **{status}**")

        # 2. 个人专属信箱
        st.markdown(f"### 📬 我的专属信箱 ({user_info['name']})")
        my_mailbox = data["mailboxes"].get(current_user, [])
        if not my_mailbox:
            st.caption("信箱空空的，快让家人送你一幅画吧！")
        else:
            for mail in my_mailbox:
                st.image(mail["url"], caption=f"来自：{mail['sender']}")
                if st.button("删除这封信", key=f"del_mail_{mail['id']}"):
                    data["mailboxes"][current_user] = [m for m in my_mailbox if m["id"] != mail["id"]]
                    save_data(data)
                    st.rerun()

    with right_col:
        # 3. 每日打卡
        st.markdown("### ✨ 每日全家打卡")
        today_str = today.strftime("%Y-%m-%d")
        checkins = data["checkins"]

        for u_key, u_val in users.items():
            if u_key not in checkins:
                checkins[u_key] = {"streak": 0, "last_date": ""}
            
            c_data = checkins[u_key]
            checked_today = (c_data.get("last_date") == today_str)

            c1, c2, c3 = st.columns([2, 2, 2])
            c1.write(f"**{u_val['name']}**")
            c2.write(f"🔥 {c_data['streak']} 天")
            
            if u_key == current_user:
                if not checked_today:
                    if c3.button("点击打卡", key=f"check_{u_key}"):
                        c_data["checkedToday"] = True
                        c_data["streak"] += 1
                        c_data["last_date"] = today_str
                        checkins[u_key] = c_data
                        save_data(data)
                        st.success("打卡成功！")
                        st.rerun()
                else:
                    c3.button("已打卡", disabled=True, key=f"check_{u_key}")
            else:
                c3.write("已打卡" if checked_today else "未打卡")

        # 4. 相册与画作分享
        st.markdown("### 📸 公共家庭相册")
        uploaded_file = st.file_uploader("上传照片到全家相册", type=["jpg", "png", "jpeg"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_str = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode()
            
            data["photos"].insert(0, {"id": int(datetime.now().timestamp() * 1000), "url": img_str, "uploader": user_info["name"]})
            save_data(data)
            st.success("上传成功！")
            st.rerun()

        # 展示相册
        photos = data["photos"]
        if not photos:
            st.caption("暂无照片")
        else:
            for p in photos:
                st.image(p["url"], caption=p["uploader"])
                if st.button("删除照片", key=f"del_photo_{p['id']}"):
                    data["photos"] = [item for item in photos if item["id"] != p["id"]]
                    save_data(data)
                    st.rerun()
