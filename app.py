from flask import Flask, render_template_string, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'family_data.json'

# 初始化或加载云端 JSON 数据
def load_data():
    if not os.path.exists(DATA_FILE):
        initial_data = {
            "checkins": {},
            "photos": [],
            "mailboxes": {"baba": [], "mama": [], "erzi": [], "meimei": []}
        }
        save_data(initial_data)
        return initial_data
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 前端与后端完美整合的 HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>温馨家庭系统 - Python 云端共享版</title>
    <style>
        :root {
            --primary-color: #ff7b93;
            --primary-hover: #ff5c77;
            --bg-color: #fff9fa;
            --card-bg: #ffffff;
            --text-main: #333333;
            --text-sub: #777777;
            --border-color: #ffe6eb;
        }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 0; }

        /* 登录页面 */
        #login-container { display: flex; justify-content: center; align-items: center; height: 100vh; background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%); }
        .login-card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); width: 320px; text-align: center; }
        .login-card h2 { color: var(--primary-color); margin-bottom: 20px; }
        .login-card input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        .login-card button { width: 100%; padding: 12px; background-color: var(--primary-color); color: white; border: none; border-radius: 8px; cursor: pointer; }

        /* 主界面 */
        #app-wrapper { display: none; position: relative; max-width: 1150px; margin: 0 auto; padding: 20px; }
        
        /* 两侧宠物装饰 */
        .side-decoration { position: fixed; top: 50%; transform: translateY(-50%); display: flex; flex-direction: column; gap: 20px; align-items: center; z-index: 10; }
        .left-side { left: 20px; }
        .right-side { right: 20px; }
        .pet-card-container { text-align: center; cursor: pointer; transition: transform 0.2s; }
        .pet-card-container:hover { transform: scale(1.1); }
        .side-pet { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid var(--primary-color); box-shadow: 0 4px 10px rgba(0,0,0,0.1); background: white; }
        .pet-name { font-size: 0.8rem; color: var(--text-sub); font-weight: bold; margin-top: 2px; }
        @media (max-width: 1250px) { .side-decoration { display: none; } }

        header { display: flex; justify-content: space-between; align-items: center; background: white; padding: 15px 25px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }
        header h1 { color: var(--primary-color); margin: 0; font-size: 1.5rem; }
        .action-btn { padding: 6px 14px; border-radius: 20px; color: white; border: none; cursor: pointer; font-size: 0.9rem; }
        .refresh-btn { background-color: #1890ff; }
        .logout-btn { background-color: #ff4d4f; }

        .grid-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 768px) { .grid-layout { grid-template-columns: 1fr; } }

        .panel { background: var(--card-bg); border-radius: 16px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .panel h3 { margin-top: 0; color: var(--primary-color); border-bottom: 2px solid var(--border-color); padding-bottom: 10px; }

        .birthday-item, .checkin-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px dashed #eee; font-size: 0.95rem; }
        .birthday-countdown { color: var(--primary-color); font-weight: bold; font-size: 0.85rem; background: #ffe6eb; padding: 2px 8px; border-radius: 10px; }
        .checkin-btn { background-color: #52c41a; color: white; border: none; padding: 6px 14px; border-radius: 15px; cursor: pointer; }
        .checkin-btn:disabled { background-color: #d9d9d9; }
        .streak-badge { color: #faad14; font-weight: bold; }

        .drawing-box { border: 2px solid #ddd; border-radius: 10px; background: #fff; width: 100%; height: 180px; cursor: crosshair; touch-action: none; }
        .tool-bar { display: flex; gap: 10px; align-items: center; margin: 8px 0; }
        .send-panel { display: flex; gap: 10px; margin-top: 10px; align-items: center; }
        .send-panel select { flex: 1; padding: 8px; border-radius: 8px; border: 1px solid #ddd; }
        .send-btn { background-color: var(--primary-color); color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; }

        .mailbox-grid, .photo-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 10px; max-height: 250px; overflow-y: auto; }
        .mail-card, .photo-card { position: relative; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); aspect-ratio: 1; background: #fafafa; border: 1px solid #eee; }
        .mail-card img, .photo-card img { width: 100%; height: 100%; object-fit: cover; }
        .mail-sender { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.6); color: white; font-size: 0.75rem; padding: 2px 4px; text-align: center; }
        .delete-btn { position: absolute; top: 4px; right: 4px; background: rgba(255, 77, 79, 0.85); color: white; border: none; border-radius: 50%; width: 22px; height: 22px; cursor: pointer; display: flex; align-items: center; justify-content: center; }

        /* 弹窗 */
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: white; padding: 30px; border-radius: 24px; text-align: center; max-width: 350px; width: 90%; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .modal-btn { background: var(--primary-color); color: white; border: none; padding: 10px 25px; border-radius: 20px; cursor: pointer; margin-top: 15px; }
    </style>
</head>
<body>

    <!-- 登录界面 -->
    <div id="login-container">
        <div class="login-card">
            <h2>🏡 家庭系统登录</h2>
            <input type="text" id="username" placeholder="请输入账号 (baba/mama/erzi/meimei)">
            <input type="password" id="password" placeholder="请输入密码">
            <button onclick="handleLogin()">登 录</button>
            <div id="error-msg" style="color:#ff4d4f; font-size:0.85rem; margin-top:10px; display:none;">账号或密码错误！</div>
        </div>
    </div>

    <!-- 主界面 -->
    <div id="app-wrapper">
        <!-- 左侧宠物 -->
        <div class="side-decoration left-side">
            <div class="pet-card-container" onclick="showPetModal('lulu')">
                <img src="/static/lulu.jpeg" class="side-pet" alt="噜噜">
                <div class="pet-name">噜噜 🐾</div>
            </div>
            <div class="pet-card-container" onclick="showPetModal('bubu')">
                <img src="/static/bubu.jpeg" class="side-pet" alt="布布">
                <div class="pet-name">布布 🐾</div>
            </div>
        </div>
        <!-- 右侧宠物 -->
        <div class="side-decoration right-side">
            <div class="pet-card-container" onclick="showPetModal('yier')">
                <img src="/static/yier.jpeg" class="side-pet" alt="一二">
                <div class="pet-name">一二 🐾</div>
            </div>
        </div>

        <header>
            <h1>🏡 温馨家庭系统 (Python云端版)</h1>
            <div style="display:flex; align-items:center; gap:10px;">
                <span id="welcome-user">欢迎您！</span>
                <button class="action-btn refresh-btn" onclick="syncData()">🔄 同步云端</button>
                <button class="action-btn logout-btn" onclick="handleLogout()">退出</button>
            </div>
        </header>

        <div class="grid-layout">
            <div>
                <div class="panel">
                    <h3>🎂 家人生日倒计时</h3>
                    <div id="birthday-list"></div>
                </div>
                <div class="panel">
                    <h3>📬 我的专属信箱 (<span id="mailbox-owner"></span>)</h3>
                    <div class="mailbox-grid" id="mailbox-grid"></div>
                </div>
            </div>
            <div>
                <div class="panel">
                    <h3>🎨 家庭涂鸦与赠送板</h3>
                    <canvas id="paint-canvas" class="drawing-box"></canvas>
                    <div class="tool-bar">
                        <input type="color" id="draw-color" value="#ff7b93" style="width:30px; height:30px; border:none; border-radius:50%; cursor:pointer;">
                        <button onclick="clearCanvas()" style="padding:5px 10px; border:none; border-radius:6px; cursor:pointer;">清空</button>
                    </div>
                    <div class="send-panel">
                        <select id="recipient-select">
                            <option value="all">公开到全家相册 🌍</option>
                            <option value="baba">赠送给：爸爸 👨</option>
                            <option value="mama">赠送给：妈妈 👩</option>
                            <option value="erzi">赠送给：儿子 👦</option>
                            <option value="meimei">赠送给：妹妹 👧</option>
                        </select>
                        <button class="send-btn" onclick="sendDrawing()">发送 💌</button>
                    </div>
                </div>
                <div class="panel">
                    <h3>✨ 每日全家打卡</h3>
                    <div id="checkin-list" style="margin-bottom: 20px;"></div>
                    <h3>📸 公共家庭相册</h3>
                    <input type="file" accept="image/*" id="photo-file" onchange="uploadPhoto(event)" style="margin-bottom:10px; font-size:0.9rem;">
                    <div class="photo-grid" id="photo-grid"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- 宠物弹窗 -->
    <div id="pet-modal" class="modal-overlay">
        <div class="modal-content">
            <img id="pet-modal-img" src="" style="width:100px; height:100px; border-radius:50%; object-fit:cover; border:3px solid var(--primary-color);">
            <h2 id="pet-modal-name" style="color:var(--primary-color); margin:10px 0;"></h2>
            <p id="pet-modal-desc" style="color:var(--text-sub); line-height:1.5; font-size:0.95rem;"></p>
            <button class="modal-btn" onclick="closeModal('pet-modal')">摸摸它 🥰</button>
        </div>
    </div>

    <script>
        const users = {
            "baba": { pass: "baba123456", name: "爸爸", birthday: "12-23" },
            "mama": { pass: "mama123456", name: "妈妈", birthday: "07-15" },
            "erzi": { pass: "erzi123456", name: "儿子", birthday: "05-03" },
            "meimei": { pass: "meimei123456", name: "妹妹", birthday: "01-09" }
        };

        const petsInfo = {
            "lulu": { name: "噜噜 🐾", img: "/static/lulu.jpeg", desc: "我是噜噜！家里最活泼的小可爱，每天负责卖萌和迎接大家回家，最喜欢吃好吃的零食！" },
            "bubu": { name: "布布 🐾", img: "/static/bubu.jpeg", desc: "我是布布！性格温顺又粘人，是大家的贴心小棉袄，最喜欢在阳光下懒洋洋地睡大觉。" },
            "yier": { name: "一二 🐾", img: "/static/yier.jpeg", desc: "我是一二！行事雷厉风行，是家庭里的快乐源泉，每天都在元气满满地巡视领地！" }
        };

        let currentUser = null;

        function showPetModal(key) {
            const pet = petsInfo[key];
            document.getElementById('pet-modal-img').src = pet.img;
            document.getElementById('pet-modal-name').innerText = pet.name;
            document.getElementById('pet-modal-desc').innerText = pet.desc;
            document.getElementById('pet-modal').style.display = 'flex';
        }

        function closeModal(id) { document.getElementById(id).style.display = 'none'; }

        function handleLogin() {
            const u = document.getElementById('username').value.trim();
            const p = document.getElementById('password').value.trim();
            if (users[u] && users[u].pass === p) {
                currentUser = u;
                localStorage.setItem('current_user', u);
                showApp();
            } else {
                document.getElementById('error-msg').style.display = 'block';
            }
        }

        function handleLogout() {
            localStorage.removeItem('current_user');
            currentUser = null;
            document.getElementById('app-wrapper').style.display = 'none';
            document.getElementById('login-container').style.display = 'flex';
        }

        function showApp() {
            document.getElementById('login-container').style.display = 'none';
            document.getElementById('app-wrapper').style.display = 'block';
            document.getElementById('welcome-user').innerText = `欢迎，${users[currentUser].name}！`;
            document.getElementById('mailbox-owner').innerText = users[currentUser].name;
            syncData();
            initCanvas();
        }

        async function syncData() {
            const res = await fetch('/api/get_data');
            const data = await res.json();
            renderBirthdays();
            renderCheckins(data.checkins);
            renderPhotos(data.photos);
            renderMailbox(data.mailboxes);
        }

        async function doCheckin(username) {
            await fetch('/api/checkin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username })
            });
            syncData();
        }

        function renderBirthdays() {
            const container = document.getElementById('birthday-list');
            container.innerHTML = '';
            Object.keys(users).forEach(key => {
                const user = users[key];
                const [m, d] = user.birthday.split('-');
                container.innerHTML += `<div class="birthday-item"><span><b>${user.name}</b> (${m}月${d}日)</span><span class="birthday-countdown">已记录</span></div>`;
            });
        }

        function renderCheckins(checkins) {
            const container = document.getElementById('checkin-list');
            container.innerHTML = '';
            Object.keys(users).forEach(username => {
                const data = checkins[username] || { streak: 0, checkedToday: false };
                const isCurrent = (username === currentUser);
                let btn = isCurrent ? 
                    (data.checkedToday ? `<button class="checkin-btn" disabled>已打卡</button>` : `<button class="checkin-btn" onclick="doCheckin('${username}')">点击打卡</button>`) : 
                    `<span>${data.checkedToday ? '已打卡' : '未打卡'}</span>`;
                container.innerHTML += `<div class="checkin-row"><span><b>${users[username].name}</b></span> <span class="streak-badge">🔥 ${data.streak}天</span> ${btn}</div>`;
            });
        }

        let canvas, ctx, isDrawing = false;
        function initCanvas() {
            canvas = document.getElementById('paint-canvas');
            ctx = canvas.getContext('2d');
            canvas.width = canvas.offsetWidth;
            canvas.height = 180;
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            canvas.onmousedown = (e) => { isDrawing = true; ctx.beginPath(); ctx.moveTo(e.offsetX, e.offsetY); };
            canvas.onmousemove = (e) => { if (!isDrawing) return; ctx.lineTo(e.offsetX, e.offsetY); ctx.strokeStyle = document.getElementById('draw-color').value; ctx.lineWidth = 3; ctx.lineCap = 'round'; ctx.stroke(); };
            canvas.onmouseup = () => isDrawing = false;
        }
        function clearCanvas() { ctx.fillStyle = "#ffffff"; ctx.fillRect(0, 0, canvas.width, canvas.height); }

        async function sendDrawing() {
            const url = canvas.toDataURL('image/png');
            const recipient = document.getElementById('recipient-select').value;
            await fetch('/api/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, recipient, sender: users[currentUser].name })
            });
            clearCanvas();
            syncData();
            alert("发送成功！💌");
        }

        async function uploadPhoto(event) {
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = async function(e) {
                await fetch('/api/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: e.target.result, recipient: 'all', sender: users[currentUser].name })
                });
                syncData();
            };
            reader.readAsDataURL(file);
        }

        function renderPhotos(photos) {
            const grid = document.getElementById('photo-grid');
            grid.innerHTML = photos.length ? '' : '<p style="grid-column:1/-1; text-align:center; color:var(--text-sub); font-size:0.85rem;">暂无照片</p>';
            photos.forEach(p => {
                grid.innerHTML += `<div class="photo-card"><img src="${p.url}"><button class="delete-btn" onclick="deleteItem('photos', ${p.id})">×</button></div>`;
            });
        }

        function renderMailbox(mailboxes) {
            const myMail = mailboxes[currentUser] || [];
            const grid = document.getElementById('mailbox-grid');
            grid.innerHTML = myMail.length ? '' : '<p style="grid-column:1/-1; text-align:center; color:var(--text-sub); font-size:0.85rem;">信箱空空的，快让家人送你一幅画吧！</p>';
            myMail.forEach(m => {
                grid.innerHTML += `<div class="mail-card"><img src="${m.url}"><div class="mail-sender">来自：${m.sender}</div><button class="delete-btn" onclick="deleteMail(${m.id})">×</button></div>`;
            });
        }

        async function deleteItem(type, id) {
            await fetch('/api/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id })
            });
            syncData();
        }

        async function deleteMail(id) {
            await fetch('/api/delete_mail', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user: currentUser, id })
            });
            syncData();
        }

        window.onload = function() {
            const saved = localStorage.getItem('current_user');
            if (saved && users[saved]) { currentUser = saved; showApp(); }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/get_data')
def get_data():
    return jsonify(load_data())

@app.route('/api/checkin', methods=['POST'])
def checkin():
    username = request.json.get('username')
    data = load_data()
    checkins = data['checkins']
    if username not in checkins:
        checkins[username] = {"streak": 0, "checkedToday": False}
    if not checkins[username]['checkedToday']:
        checkins[username]['checkedToday'] = True
        checkins[username]['streak'] += 1
        save_data(data)
    return jsonify({"status": "success"})

@app.route('/api/send', methods=['POST'])
def send():
    req = request.json
    url, recipient, sender = req.get('url'), req.get('recipient'), req.get('sender')
    data = load_data()
    item = {"id": int(os.times()[4] * 1000000), "url": url, "sender": sender}
    if recipient == 'all':
        data['photos'].insert(0, item)
    else:
        if recipient in data['mailboxes']:
            data['mailboxes'][recipient].insert(0, item)
    save_data(data)
    return jsonify({"status": "success"})

@app.route('/api/delete', methods=['POST'])
def delete_item():
    item_id = request.json.get('id')
    data = load_data()
    data['photos'] = [p for p in data['photos'] if p['id'] != item_id]
    save_data(data)
    return jsonify({"status": "success"})

@app.route('/api/delete_mail', methods=['POST'])
def delete_mail():
    req = request.json
    user, item_id = req.get('user'), req.get('id')
    data = load_data()
    if user in data['mailboxes']:
        data['mailboxes'][user] = [m for m in data['mailboxes'][user] if m['id'] != item_id]
        save_data(data)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(host='0.0.0.0', port=5000, debug=True)