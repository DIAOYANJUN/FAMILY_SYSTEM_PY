import streamlit as st
import pandas as pd
import json
import base64
import requests
import os
from datetime import datetime
from PIL import Image
import io
from streamlit_drawable_canvas import st_canvas
from streamlit_cookies_controller import CookieController

# ---------------- 0. 页面配置与 CSS 美化 ----------------
st.set_page_config(
    page_title="温馨家庭系统",
    page_icon="🏡",
    layout="wide"
)

# 初始化加密 Cookie 控制器
cookie_controller = CookieController()

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
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
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

DATA_FILE = "family_data.json"

# ---------------- 1. 核心数据读写与 GitHub API 同步逻辑 ----------------
def get_github_config():
    try:
        gh_token = st.secrets["github"]["token"]
        gh_repo = st.secrets["github"]["repo"]
        return gh_token, gh_repo
    except Exception:
        return None, None

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return get_default_data()

def save_data(data):
    content_str = json.dumps(data, ensure_ascii=False, indent=4)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(content_str)
    
    token, repo = get_github_config()
    if not token or not repo:
        return
    
    try:
        url = f"https://api.github.com/repos/{repo}/contents/{DATA_FILE}"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        
        res = requests.get(url, headers=headers, timeout=3)
        sha = res.json().get("sha", "") if res.status_code == 200 else ""
        
        content_encoded = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
        payload = {
            "message": f"Sync family data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "content": content_encoded,
            "sha": sha
        }
        requests.put(url, headers=headers, json=payload, timeout=3)
    except Exception:
        pass

def get_default_data():
    return {
        "checkins": {},
        "photos": [],
        "messages": [],
        "mailboxes": {"baba": [], "mama": [], "erzi": [], "meimei": []}
    }

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

# ---------------- 2. 稳如磐石的 Cookie 登录态维持逻辑 ----------------
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# 🌟 核心修改：从浏览器的加密 Cookie 中读取登录状态（不再暴露在网址里）
cookie_user = cookie_controller.get("family_logged_user")
if cookie_user in users and not st.session_state.logged_in_user:
    st.session_state.logged_in_user = cookie_user

current_user = st.session_state.logged_in_user

if not current_user:
    st.markdown("<h2 style='text-align: center; color: #ff7b93;'>🏡 温馨家庭系统登录</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_img, col_login = st.columns([1, 1], gap="large")
    with col_img:
        st.markdown("### 🐾 守护精灵欢迎你！")
        if os.path.exists("lulu.jpeg"):
            st.image("lulu.jpeg", width=200, caption="噜噜")
        if os.path.exists("bubu.jpeg"):
            st.image("bubu.jpeg", width=200, caption="布布")
            
    with col_login:
        st.markdown("### 🚀 请输入家人账号密码")
        with st.form("login_form"):
            username_input = st.text_input("账号 (baba / mama / erzi / meimei)")
            password_input = st.text_input("密码", type="password")
            submit = st.form_submit_button("登 录 系统", use_container_width=True)
            if submit:
                if username_input in users and users[username_input]["pass"] == password_input:
                    st.session_state.logged_in_user = username_input
                    
                    # 🌟 核心修改：登录成功后，将身份加密存入 Cookie（有效期 7 天）
                    cookie_controller.set("family_logged_user", username_input, max_age=60*60*24*7)
                    
                    st.success("登录成功！正在进入...")
                    st.rerun()
                else:
                    st.error("账号或密码错误！")
    st.stop()

user_info = users[current_user]

if "selected_pet" not in st.session_state:
    st.session_state.selected_pet = None
if "canvas_reset_counter" not in st.session_state:
    st.session_state.canvas_reset_counter = 0

data = load_data()
today_date_str = datetime.now().strftime("%Y-%m-%d")

# ---------------- 3. 侧边栏与动态时钟 ----------------
clock_html = """
<div style="font-family: sans-serif; font-size: 13px; font-weight: bold; color: #ff5c8a; background: #fff0f3; padding: 8px; border-radius: 8px; text-align: center; border: 1px solid #ffe6eb;">
    🕒 <span id="clock">获取时间中...</span>
</div>
<script>
function updateClock() {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, '0');
    const d = String(now.getDate()).padStart(2, '0');
    const h = String(now.getHours()).padStart(2, '0');
    const min = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    const el = document.getElementById('clock');
    if (el) el.innerText = `${y}-${m}-${d} ${h}:${min}:${s}`;
}
setInterval(updateClock, 1000);
updateClock();
</script>
"""

with st.sidebar:
    st.components.v1.html(clock_html, height=45)
    st.markdown(f"👤 **当前成员**：`{user_info['emoji']} {user_info['name']}`")
    st.markdown("---")
    
    st.markdown("### 🌟 家庭守护精灵")
    if os.path.exists("lulu.jpeg"):
        st.image("lulu.jpeg", width=120, caption="✨ 噜噜")
    if st.button("查看 噜噜 档案", use_container_width=True):
        st.session_state.selected_pet = "lulu"
        st.rerun()

    st.markdown("---")
    if os.path.exists("bubu.jpeg"):
        st.image("bubu.jpeg", width=120, caption="✨ 布布")
    if st.button("查看 布布 档案", use_container_width=True):
        st.session_state.selected_pet = "bubu"
        st.rerun()

    st.markdown("---")
    if os.path.exists("yier.jpeg"):
        st.image("yier.jpeg", width=120, caption="✨ 一二")
    if st.button("查看 一二 档案", use_container_width=True):
        st.session_state.selected_pet = "yier"
        st.rerun()

    st.markdown("---")
    if st.button("🔄 刷新并同步数据", type="primary", use_container_width=True):
        st.toast("已成功从云端仓库同步最新状态！", icon="✅")
        st.rerun()

    if st.button("🚪 退出登录", use_container_width=True):
        # 🌟 核心修改：退出时安全销毁 Cookie
        cookie_controller.remove("family_logged_user")
        st.session_state.logged_in_user = None
        st.rerun()

# 精灵档案弹窗逻辑
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

# 左右两侧悬浮宠物渲染
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

# ---------------- 4. 主体系统界面（双栏布局） ----------------
st.markdown("<h2 style='color: #ff7b93; margin:0;'>🏡 温馨家庭系统 (云端共享)</h2>", unsafe_allow_html=True)
st.markdown("---")

left_col, right_col = st.columns(2)

with left_col:
    # 模块 1：生日倒计时
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

    # 模块 2：专属信箱
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

    # 模块 3：家庭留言板
    st.markdown("### 💬 家庭留言板")
    target_mode = st.radio("发送给谁？", ["全家人 (公开)", "指定家人"], horizontal=True)
    selected_targets = []
    if target_mode == "指定家人":
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
    # 模块 4：家庭涂鸦与赠送板
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
            img = Image.fromarray(img_arr.astype('uint8'), 'RGB').convert('RGB')
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

    # 模块 5：每日全家打卡
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

    # 模块 6：公共家庭相册
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

    photos = data.get("photos", [])
    if not photos:
        st.caption("暂无照片")
    else:
        for p in photos:
            st.image(p["url"], caption=f"上传者：{p.get('uploader', '家人')}")
            if st.button("删除照片", key=f"del_photo_{p['id']}"):
                data["photos"] = [item for item in photos if item["id"] != p["id"]]
                save_data(data)
                st.rerun()
