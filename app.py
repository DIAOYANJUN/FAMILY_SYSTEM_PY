import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import io
import base64
from streamlit_drawable_canvas import st_canvas

# 页面基础配置
st.set_page_config(page_title="温馨家庭系统", page_icon="🏡", layout="wide")

# 注入与截图完全一致的温馨粉色主题与左右悬浮宠物 CSS
st.markdown("""
    <style>
        /* 全局背景色 */
        .stApp {
            background-color: #fff9fa;
        }
        
        /* 左右两侧悬浮宠物样式 */
        .side-decoration {
            position: fixed;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            flex-direction: column;
            gap: 20px;
            align-items: center;
            z-index: 999;
        }
        .left-side { left: 20px; }
        .right-side { right: 20px; }
        .side-pet-box {
            text-align: center;
            background: white;
            padding: 8px;
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border: 2px solid #ffe6eb;
        }
        .side-pet {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid #ff7b93;
            display: block;
        }
        .pet-name {
            font-size: 0.75rem;
            color: #777777;
            font-weight: bold;
            margin-top: 4px;
        }
        @media (max-width: 1200px) {
            .side-decoration { display: none; }
        }

        /* 顶部 Header 样式 */
        .custom-header {
            background: white;
            padding: 15px 25px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            border: 1px solid #ffe6eb;
        }

        /* 按钮美化 */
        .stButton>button {
            background-color: #ff7b93;
            color: white;
            border-radius: 20px;
            border: none;
            padding: 6px 18px;
            font-weight: bold;
            transition: 0.2s;
        }
        .stButton>button:hover {
            background-color: #ff5c77;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "family_data.json"

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

users = {
    "baba": {"name": "爸爸", "role": "父亲", "birthday": "12-23", "emoji": "👨", "pass": "baba123456"},
    "mama": {"name": "妈妈", "role": "母亲", "birthday": "07-15", "emoji": "👩", "pass": "mama123456"},
    "erzi": {"name": "儿子", "role": "儿子", "birthday": "05-03", "emoji": "👦", "pass": "erzi123456"},
    "meimei": {"name": "妹妹", "role": "妹妹", "birthday": "01-09", "emoji": "👧", "pass": "meimei123456"}
}

# 根目录下的宠物图片
pets = {
    "lulu": {"name": "噜噜", "img": "lulu.jpeg", "desc": "我是噜噜！家里最活泼的小可爱~"},
    "bubu": {"name": "布布", "img": "bubu.jpeg", "desc": "我是布布！性格温顺又粘人~"},
    "yier": {"name": "一二", "img": "yier.jpeg", "desc": "我是一二！元气满满的快乐源泉~"}
}

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

    # --- 渲染左右两侧悬浮宠物（与截图一致） ---
    # 左侧：噜噜、布布
    lulu_b64 = base64.b64encode(open(pets["lulu"]["img"], "rb").read()).decode() if os.path.exists(pets["lulu"]["img"]) else ""
    bubu_b64 = base64.b64encode(open(pets["bubu"]["img"], "rb").read()).decode() if os.path.exists(pets["bubu"]["img"]) else ""
    yier_b64 = base64.b64encode(open(pets["yier"]["img"], "rb").read()).decode() if os.path.exists(pets["yier"]["img"]) else ""

    st.markdown(f"""
        <div class="side-decoration left-side">
            <div class="side-pet-box">
                <img src="data:image/jpeg;base64,{lulu_b64}" class="side-pet">
                <div class="pet-name">噜噜</div>
            </div>
            <div class="side-pet-box">
                <img src="data:image/jpeg;base64,{bubu_b64}" class="side-pet">
                <div class="pet-name">布布</div>
            </div>
        </div>
        <div class="side-decoration right-side">
            <div class="side-pet-box">
                <img src="data:image/jpeg;base64,{yier_b64}" class="side-pet">
                <div class="pet-name">一二</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 顶部 Header ---
    st.markdown(f"""
        <div class="custom-header">
            <h2 style='color: #ff7b93; margin:0; font-size: 1.4rem;'>🏡 温馨家庭系统 (云端共享)</h2>
            <div style='display: flex; align-items: center; gap: 15px;'>
                <span style='font-size: 0.95rem; color: #555;'>欢迎，{user_info['name']}！</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 顶部右侧功能按键区
    col_top1, col_top2 = st.columns([10, 1])
    with col_top1:
        st.write("")
    with col_top2:
        if st.button("退出登录"):
            st.session_state.logged_in_user = None
            st.rerun()

    # --- 左右双列布局（与截图结构完全对应） ---
    left_col, right_col = st.columns(2)

    with left_col:
        # 1. 生日倒计时卡片
        with st.container():
            st.markdown("### 🎂 家人生日倒计时")
            today = datetime.now()
            for u_key, u_val in users.items():
                m, d = map(int, u_val["birthday"].split("-"))
                b_day = datetime(today.year, m, d)
                if b_day.date() < today.date():
                    b_day = datetime(today.year + 1, m, d)
                days_left = (b_day - today).days
                status = "🎉 今天生日！" if days_left == 0 else f"还有 {days_left} 天"
                st.info(f"{u_val['emoji']} **{u_val['name']}** ({u_val['birthday'].replace('-', '月')}日)  ——  **{status}**")

        st.write("")

        # 2. 个人专属信箱卡片
        with st.container():
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
        # 3. 家庭涂鸦与赠送板卡片
        with st.container():
            st.markdown("### 🎨 家庭涂鸦与赠送板")
            stroke_color = st.color_picker("颜色", "#ff7b93", label_visibility="collapsed")
            
            # 画布
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0)",
                stroke_width=3,
                stroke_color=stroke_color,
                background_color="#ffffff",
                height=180,
                width=420,
                drawing_mode="freedraw",
                key="canvas",
            )
            
            rc1, rc2 = st.columns([2, 1])
            with rc1:
                recipient = st.selectbox("选择对象", [
                    ("all", "公开到全家相册 🌍"),
                    ("baba", "赠送给：爸爸 👨"),
                    ("mama", "赠送给：妈妈 👩"),
                    ("erzi", "赠送给：儿子 👦"),
                    ("meimei", "赠送给：妹妹 👧")
                ], format_func=lambda x: x[1], label_visibility="collapsed")[0]
            with rc2:
                if st.button("发送/保存 💌", use_container_width=True):
                    if canvas_result.image_data is not None:
                        img_arr = canvas_result.image_data
                        img = Image.fromarray(img_arr.astype('uint8'), 'RGBA').convert('RGB')
                        buffered = io.BytesIO()
                        img.save(buffered, format="JPEG")
                        img_str = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode()
                        
                        item = {"id": int(datetime.now().timestamp() * 1000), "url": img_str, "sender": user_info["name"]}
                        if recipient == 'all':
                            data["photos"].insert(0, item)
                            st.success("已分享到全家相册！")
                        else:
                            data["mailboxes"][recipient].insert(0, item)
                            st.success(f"已放入 [{users[recipient]['name']}] 的信箱！")
                        save_data(data)
                        st.rerun()

        st.write("")

        # 4. 每日全家打卡卡片
        with st.container():
            st.markdown("### ✨ 每日全家打卡")
            today_str = today.strftime("%Y-%m-%d")
            checkins = data["checkins"]

            for u_key, u_val in users.items():
                if u_key not in checkins:
                    checkins[u_key] = {"streak": 0, "last_date": ""}
                
                c_data = checkins[u_key]
                checked_today = (c_data.get("last_date") == today_str)

                cc1, cc2, cc3 = st.columns([2, 2, 2])
                cc1.write(f"**{u_val['name']}**")
                cc2.write(f"🔥 连续 {c_data['streak']} 天")
                
                if u_key == current_user:
                    if not checked_today:
                        if cc3.button("点击打卡", key=f"check_{u_key}"):
                            c_data["checkedToday"] = True
                            c_data["streak"] += 1
                            c_data["last_date"] = today_str
                            checkins[u_key] = c_data
                            save_data(data)
                            st.success("打卡成功！")
                            st.rerun()
                    else:
                        cc3.button("今日已打卡", disabled=True, key=f"check_{u_key}")
                else:
                    cc3.write("已打卡" if checked_today else "未打卡")

        st.write("")

        # 5. 公共家庭相册卡片
        with st.container():
            st.markdown("### 📸 公共家庭相册")
            uploaded_file = st.file_uploader("上传照片到全家相册", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode()
                
                data["photos"].insert(0, {"id": int(datetime.now().timestamp() * 1000), "url": img_str, "uploader": user_info["name"]})
                save_data(data)
                st.success("上传成功！")
                st.rerun()

            photos = data["photos"]
            if not photos:
                st.caption("暂无照片")
            else:
                for p in photos:
                    st.image(p["url"], caption=f"上传者：{p.get('uploader', '家人')}")
                    if st.button("删除照片", key=f"del_photo_{p['id']}"):
                        data["photos"] = [item for item in photos if item["id"] != p["id"]]
                        save_data(data)
                        st.rerun()
