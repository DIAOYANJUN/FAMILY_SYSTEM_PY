import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import io
import base64
from streamlit_drawable_canvas import st_canvas
import streamlit.components.v1 as components

# 页面基础配置
st.set_page_config(page_title="温馨家庭系统", page_icon="🏡", layout="wide")

# 注入温馨粉色主题与悬浮精灵 CSS
st.markdown("""
    <style>
        .stApp { background-color: #fff9fa; }
        
        .side-decoration {
            position: fixed;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            flex-direction: column;
            gap: 15px;
            align-items: center;
            z-index: 999;
        }
        .left-side { left: 15px; }
        .right-side { right: 15px; }
        .side-pet-box {
            text-align: center;
            background: white;
            padding: 8px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border: 2px solid #ffe6eb;
            width: 100px;
        }
        .side-pet {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid #ff7b93;
            display: block;
            margin: 0 auto;
        }
        .pet-name {
            font-size: 0.8rem;
            color: #ff5c8a;
            font-weight: bold;
            margin-top: 5px;
        }
        @media (max-width: 1300px) { .side-decoration { display: none; } }

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
            "messages": [],
            "mailboxes": {"baba": [], "mama": [], "erzi": [], "meimei": []}
        }
        save_data(initial)
        return initial
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "checkins": {},
            "photos": [],
            "messages": [],
            "mailboxes": {"baba": [], "mama": [], "erzi": [], "meimei": []}
        }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

users = {
    "baba": {"name": "爸爸", "role": "父亲", "birthday": "12-23", "emoji": "👨", "pass": "baba123456"},
    "mama": {"name": "妈妈", "role": "母亲", "birthday": "07-15", "emoji": "👩", "pass": "mama123456"},
    "erzi": {"name": "儿子", "role": "儿子", "birthday": "05-03", "emoji": "👦", "pass": "erzi123456"},
    "meimei": {"name": "妹妹", "role": "妹妹", "birthday": "01-09", "emoji": "👧", "pass": "meimei123456"}
}

pets = {
    "lulu": {
        "name": "噜噜", 
        "img": "lulu.jpeg", 
        "desc": "我是精灵·噜噜！家里最活泼的小可爱，每天负责卖萌和迎接大家回家，最喜欢吃好吃的零食！✨",
        "quotes": {
            "2026-10-26": "今天是个好天气，噜噜在门口等大家回家吃好吃的零食哦！🐾",
            "2026-10-25": "昨天噜噜抓到了一只蝴蝶，开心得转了好几个圈！🦋",
            "2026-10-24": "大家今天都要开开心心的，噜噜给你们加油鸭！💪"
        }
    },
    "bubu": {
        "name": "布布", 
        "img": "bubu.jpeg", 
        "desc": "我是精灵·布布！性格温顺又粘人，是大家的贴心小棉袄，最喜欢在阳光下懒洋洋地睡大觉。💤",
        "quotes": {
            "2026-10-26": "阳光暖洋洋的，布布在沙发上找到了最舒服的睡觉姿势~ ☀️",
            "2026-10-25": "今天布布有乖乖看家哦，求夸奖！🥰",
            "2026-10-24": "晚上记得盖好被子，布布陪大家做个好梦。🌙"
        }
    },
    "yier": {
        "name": "一二", 
        "img": "yier.jpeg", 
        "desc": "我是一二精灵！行事雷厉风行，是家庭里的快乐源泉，每天都在元气满满地巡视领地！⚡",
        "quotes": {
            "2026-10-26": "一二已经把家里巡视完毕啦！今天一切安全，大家冲呀！🚀",
            "2026-10-25": "今天跑得有点快，差点把自己的尾巴追到了... 🙈",
            "2026-10-24": "元气满满的一天开始啦，大家今天也要加油冲鸭！🌟"
        }
    }
}

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# --- 前端 sessionStorage 绝对隔离机制 ---
# 原理：同标签页刷新时，sessionStorage 有记录，自动带参数恢复；
# 复制到新浏览器或新标签页时，sessionStorage 为空，不带参数，直接强制要求重新登录。
session_guard_js = """
<script>
    const activeUser = sessionStorage.getItem("family_tab_user");
    const urlParams = new URLSearchParams(window.parent.location.search);
    const hasToken = urlParams.get("tab_auth");

    if (activeUser && !hasToken) {
        // 同标签页刷新：自动在后台补全参数，实现不掉登录
        const separator = window.parent.location.search ? "&" : "?";
        window.parent.location.href = window.parent.location.href + separator + "tab_auth=" + activeUser;
    } else if (!activeUser && hasToken) {
        // 如果是新标签页/新浏览器（sessionStorage为空但网址带了参数），立刻清除网址参数拦截！
        window.parent.location.href = window.parent.location.origin + window.parent.location.pathname;
    }
</script>
"""
components.html(session_guard_js, height=0)

query_params = st.query_params
url_token = query_params.get("tab_auth", None)

if url_token in users and not st.session_state.logged_in_user:
    st.session_state.logged_in_user = url_token

current_user = st.session_state.logged_in_user

if "selected_pet" not in st.session_state:
    st.session_state.selected_pet = None

if "canvas_reset_counter" not in st.session_state:
    st.session_state.canvas_reset_counter = 0

data = load_data()
today_date_str = datetime.now().strftime("%Y-%m-%d")

# --- 登录界面 ---
if not current_user:
    st.markdown("<h2 style='text-align: center; color: #ff7b93;'>🏡 温馨家庭系统登录</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username_input = st.text_input("账号 (baba / mama / erzi / meimei)")
        password_input = st.text_input("密码", type="password")
        if st.button("登 录", use_container_width=True):
            if username_input in users and users[username_input]["pass"] == password_input:
                st.session_state.logged_in_user = username_input
                # 登录成功：写入当前标签页的 sessionStorage，并带参数重载
                login_js = f"""
                <script>
                    sessionStorage.setItem("family_tab_user", "{username_input}");
                    window.parent.location.href = window.parent.location.origin + window.parent.location.pathname + "?tab_auth={username_input}";
                </script>
                """
                components.html(login_js, height=0)
            else:
                st.error("账号或密码错误！")
else:
    user_info = users[current_user]

    # --- 精灵点击弹窗 ---
    if st.session_state.selected_pet:
        p_key = st.session_state.selected_pet
        p_info = pets[p_key]
        today_quote = p_info["quotes"].get(today_date_str, "今天也是充满元气的一天！✨")
        
        @st.dialog(f"✨ 精灵档案：{p_info['name']}")
        def pet_dialog():
            if os.path.exists(p_info["img"]):
                st.image(p_info["img"], width=220)
            
            st.markdown(f"**【精灵简介】**\n{p_info['desc']}")
            st.markdown(f"**【今日语录 ({today_date_str})】**\n> *\"{today_quote}\" 🌸*")
            
            if "show_history" not in st.session_state:
                st.session_state.show_history = False

            if st.button("📖 查看历史语录档案"):
                st.session_state.show_history = not st.session_state.show_history

            if st.session_state.get("show_history", False):
                st.markdown("---")
                st.markdown("### 📜 历史语录记录")
                for date_s, q_text in sorted(p_info["quotes"].items(), reverse=True):
                    st.markdown(f"- **`{date_s}`**: {q_text}")

            st.write("")
            if st.button("关闭档案"):
                st.session_state.selected_pet = None
                st.session_state.show_history = False
                st.rerun()
        pet_dialog()

    # --- 渲染左右两侧固定展示的精灵图片 ---
    lulu_b64 = base64.b64encode(open(pets["lulu"]["img"], "rb").read()).decode() if os.path.exists(pets["lulu"]["img"]) else ""
    bubu_b64 = base64.b64encode(open(pets["bubu"]["img"], "rb").read()).decode() if os.path.exists(pets["bubu"]["img"]) else ""
    yier_b64 = base64.b64encode(open(pets["yier"]["img"], "rb").read()).decode() if os.path.exists(pets["yier"]["img"]) else ""

    st.markdown(f"""
        <div class="side-decoration left-side">
            <div class="side-pet-box">
                <img src="data:image/jpeg;base64,{lulu_b64}" class="side-pet">
                <div class="pet-name">✨ 噜噜</div>
            </div>
            <div class="side-pet-box">
                <img src="data:image/jpeg;base64,{bubu_b64}" class="side-pet">
                <div class="pet-name">✨ 布布</div>
            </div>
        </div>
        <div class="side-decoration right-side">
            <div class="side-pet-box">
                <img src="data:image/jpeg;base64,{yier_b64}" class="side-pet">
                <div class="pet-name">✨ 一二</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 左侧栏：精灵照片展示与档案入口 ---
    with st.sidebar:
        st.markdown("### 🌟 🌱 家庭守护精灵")
        st.caption("点击下方按钮查看精灵档案与历史语录：")
        
        if os.path.exists("lulu.jpeg"):
            st.image("lulu.jpeg", width=120, caption="✨ 噜噜")
        if st.button("查看 噜噜 档案"):
            st.session_state.selected_pet = "lulu"
            st.rerun()

        st.markdown("---")

        if os.path.exists("bubu.jpeg"):
            st.image("bubu.jpeg", width=120, caption="✨ 布布")
        if st.button("查看 布布 档案"):
            st.session_state.selected_pet = "bubu"
            st.rerun()

        st.markdown("---")

        if os.path.exists("yier.jpeg"):
            st.image("yier.jpeg", width=120, caption="✨ 一二")
        if st.button("查看 一二 档案"):
            st.session_state.selected_pet = "yier"
            st.rerun()

    # --- 顶部 Header ---
    col_top1, col_top2, col_top3, col_top4 = st.columns([5, 2, 1, 1])
    with col_top1:
        st.markdown("<h2 style='color: #ff7b93; margin:0;'>🏡 温馨家庭系统 (云端共享)</h2>", unsafe_allow_html=True)
    with col_top2:
        st.write(f"欢迎，**{user_info['name']}**！")
    with col_top3:
        if st.button("🔄 刷新数据"):
            st.query_params["tab_auth"] = current_user
            st.rerun()
    with col_top4:
        if st.button("退出登录"):
            logout_js = """
            <script>
                sessionStorage.removeItem("family_tab_user");
                window.parent.location.href = window.parent.location.origin + window.parent.location.pathname;
            </script>
            """
            components.html(logout_js, height=0)

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
            st.info(f"{u_val['emoji']} **{u_val['name']}** ({u_val['birthday'].replace('-', '月')}日)  ——  **{status}**")

        st.write("")

        # 2. 📬 专属信箱折叠抽屉
        my_mailbox = data["mailboxes"].get(current_user, [])
        mailbox_title = f"📬 打开我的专属信箱 ({user_info['name']}) — 共 {len(my_mailbox)} 封信件"
        
        with st.expander(mailbox_title):
            if not my_mailbox:
                st.caption("信箱空空的，快让家人送你一幅画吧！")
            else:
                for mail in my_mailbox:
                    st.image(mail["url"], caption=f"来自：{mail['sender']}")
                    if st.button("删除这封信", key=f"del_mail_{mail['id']}"):
                        data["mailboxes"][current_user] = [m for m in my_mailbox if m["id"] != mail["id"]]
                        save_data(data)
                        st.rerun()

        st.write("")

        # 3. 💬 家庭留言板
        st.markdown("### 💬 家庭留言板")
        
        target_mode = st.radio("发送给谁？", ["全家人 (公开)", "指定家人"], horizontal=True)
        selected_targets = []
        if target_mode == "指定家人":
            st.caption("可单选或多选：")
            cols_t = st.columns(4)
            for idx, (u_k, u_v) in enumerate(users.items()):
                if cols_t[idx].checkbox(u_v["name"], key=f"target_{u_k}"):
                    selected_targets.append(u_v["name"])

        new_msg = st.text_input("写下你想说的话...", key="msg_input")
        if st.button("发布留言 📢"):
            if new_msg.strip():
                if target_mode == "指定家人" and not selected_targets:
                    st.warning("请至少勾选一位接收对象！")
                else:
                    if "messages" not in data:
                        data["messages"] = []
                    
                    target_str = "全家人 🌍" if target_mode == "全家人 (公开)" or not selected_targets else " @".join(selected_targets)
                    if target_mode == "指定家人":
                        target_str = " @ " + target_str

                    data["messages"].insert(0, {
                        "id": int(datetime.now().timestamp() * 1000),
                        "sender": user_info["name"],
                        "target": target_str,
                        "text": new_msg,
                        "time": datetime.now().strftime("%m-%d %H:%M")
                    })
                    save_data(data)
                    st.success("留言发表成功！")
                    st.rerun()
        
        messages = data.get("messages", [])
        if not messages:
            st.caption("暂无留言，快来抢沙发吧~")
        else:
            for msg in messages:
                st.markdown(f"""
                    <div style="background: white; padding: 10px 15px; border-radius: 10px; margin-bottom: 8px; border-left: 4px solid #ff7b93; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                        <b>{msg['sender']}</b> <span style="color: #ff5c8a; font-size: 0.85rem;">(to: {msg.get('target', '全家人 🌍')})</span>
                        <span style="font-size: 0.75rem; color: #999; float: right;">{msg['time']}</span><br>
                        <span style="color: #333; font-size: 0.95rem; margin-top: 5px; display: block;">{msg['text']}</span>
                    </div>
                """, unsafe_allow_html=True)

    with right_col:
        # 4. 家庭涂鸦与赠送板
        st.markdown("### 🎨 家庭涂鸦与赠送板")
        stroke_color = st.color_picker("画笔颜色", "#ff7b93")
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=4,
            stroke_color=stroke_color,
            background_color="#ffffff",
            height=240,
            width=450,
            drawing_mode="freedraw",
            key=f"canvas_{st.session_state.canvas_reset_counter}",
        )
        
        col_btn1, col_btn2 = st.columns([1, 2])
        with col_btn1:
            if st.button("🗑️ 清除重画", use_container_width=True):
                st.session_state.canvas_reset_counter += 1
                st.rerun()
        with col_btn2:
            recipient = st.selectbox("选择发送对象", [
                ("all", "公开到全家相册 🌍"),
                ("baba", "赠送给：爸爸 👨"),
                ("mama", "赠送给：妈妈 👩"),
                ("erzi", "赠送给：儿子 👦"),
                ("meimei", "赠送给：妹妹 👧")
            ], format_func=lambda x: x[1], label_visibility="collapsed")

        if st.button("保存并发送画作 💌", use_container_width=True):
            if canvas_result.image_data is not None:
                img_arr = canvas_result.image_data
                img = Image.fromarray(img_arr.astype('uint8'), 'RGBA').convert('RGB')
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                img_str = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode()
                
                item = {"id": int(datetime.now().timestamp() * 1000), "url": img_str, "sender": user_info["name"]}
                rec_key = recipient[0]
                if rec_key == 'all':
                    data["photos"].insert(0, item)
                    st.success("已成功保存并分享到全家相册！🌍")
                else:
                    data["mailboxes"][rec_key].insert(0, item)
                    st.success(f"已成功发送到 [{users[rec_key]['name']}] 的专属信箱！💌")
                save_data(data)
                st.rerun()

        st.write("")

        # 5. 每日全家打卡
        st.markdown("### ✨ 每日全家打卡")
        today_str = today.strftime("%Y-%m-%d")
        checkins = data.get("checkins", {})

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
                        c_data["streak"] += 1
                        c_data["last_date"] = today_str
                        checkins[u_key] = c_data
                        data["checkins"] = checkins
                        save_data(data)
                        st.success("打卡成功！")
                        st.rerun()
                else:
                    cc3.button("今日已打卡", disabled=True, key=f"check_{u_key}")
            else:
                cc3.write("已打卡" if checked_today else "未打卡")

        st.write("")

        # 6. 公共家庭相册
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
