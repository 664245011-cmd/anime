from textwrap import dedent
from neo4j_service import (
    get_users,
    get_dashboard_metrics,
    get_profile,
    recommend_anime,
    search_anime,
    record_watched,
    graph_neighborhood,
    seed_demo_data,
    query,
)
import pandas as pd
import streamlit as st

# =========================================================
# Anime image URLs
# =========================================================
ANIME_IMAGES = {
    "A001": "https://cdn.myanimelist.net/images/anime/1244/138851l.jpg",  # One Piece
    "A002": "https://cdn.myanimelist.net/images/anime/1141/142503l.jpg",  # Naruto
    "A003": "https://cdn.myanimelist.net/images/anime/1286/99889l.jpg",  # Demon Slayer
    "A004": "https://cdn.myanimelist.net/images/anime/10/47347l.jpg",  # Attack on Titan
    "A005": (
        "https://huggingface.co/datasets/deepghs/fancaps_animes/resolve/main/images/40748__jujutsu_kaisen.jpg"
    ),  # Jujutsu Kaisen
    "A006": "https://cdn.myanimelist.net/images/anime/10/78745l.jpg",  # My Hero Academia
    "A007": "https://cdn.myanimelist.net/images/anime/1079/138100l.jpg",  # Death Note
    "A008": "https://cdn.myanimelist.net/images/anime/7/76014l.jpg",  # Haikyuu!!
    "A009": "https://cdn.myanimelist.net/images/anime/12/76049l.jpg",  # One Punch Man
    "A010": "https://cdn.myanimelist.net/images/anime/6/73245l.jpg",  # Dragon Ball
}

# =========================================================
# Page Config
# =========================================================
st.set_page_config(
    page_title="AnimeGraph Recommendation",
    page_icon="🎌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CSS
# =========================================================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    .hero {
        padding: 24px 28px;
        border-radius: 22px;
        background: linear-gradient(
            135deg,
            #111827,
            #312e81 55%,
            #581c87
        );
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 12px 35px rgba(0,0,0,.12);
    }

    .hero h1 {
        margin: 0 0 6px;
        font-size: 2.25rem;
    }

    .hero p {
        margin: 0;
        opacity: .85;
    }

    .card {
        padding: 18px;
        border: 1px solid rgba(128,128,128,.22);
        border-radius: 18px;
        background: rgba(255,255,255,.03);
        margin-bottom: 12px;
    }

    .anime-card {
        overflow: hidden;
        border-radius: 16px;
        border: 1px solid rgba(128,128,128,.20);
        background: linear-gradient(145deg, rgba(99,102,241,.10), rgba(168,85,247,.06));
        margin-top: 8px;
        margin-bottom: 18px;
    }

    .anime-card-image {
        width: 100%;
        height: 260px;
        object-fit: cover;
        display: block;
        border-radius: 0;
    }

    .anime-card-body {
        padding: 14px 16px 16px;
    }

    .anime-card-title {
        font-size: 1.08rem;
        font-weight: 700;
        margin: 9px 0 6px;
    }

    .anime-card-score {
        font-size: 1.35rem;
        font-weight: 800;
        margin: 5px 0 8px;
    }

    .anime-card-friends {
        font-size: .88rem;
        opacity: .75;
        line-height: 1.45;
    }

    .anime-title {
        font-size: 1.08rem;
        font-weight: 700;
        margin: 8px 0;
    }

    .score {
        font-size: 1.45rem;
        font-weight: 800;
        margin: 4px 0 8px;
    }

    .small {
        font-size: .84rem;
        opacity: .72;
    }

    .pill {
        display: inline-block;
        padding: 4px 9px;
        border-radius: 999px;
        background: rgba(99,102,241,.14);
        font-size: .78rem;
        margin-right: 5px;
    }

    .rank-card {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 14px 16px;
        margin: 10px 0;
        background: rgba(255,255,255,.045);
        border: 1px solid rgba(255,255,255,.09);
        border-radius: 16px;
    }

    .rank-no {
        min-width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        background: #25204d;
        color: #d8d0ff;
        font-weight: 700;
    }

    .rank-info {
        flex: 1;
        min-width: 0;
    }

    .rank-title {
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .rank-friends {
        color: #9ca3af;
        font-size: 13px;
        margin-bottom: 9px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .rank-track {
        height: 7px;
        background: #272a35;
        border-radius: 99px;
        overflow: hidden;
    }

    .rank-fill {
        height: 100%;
        background: linear-gradient(
            90deg,
            #8b5cf6,
            #a78bfa
        );
        border-radius: 99px;
    }

    .rank-score {
        min-width: 64px;
        text-align: right;
    }

    .rank-score b {
        display: block;
        font-size: 22px;
        color: #fff;
    }

    .rank-score span {
        color: #9ca3af;
        font-size: 12px;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.65rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Connect Neo4j
# =========================================================
try:
    users = get_users()
    stats = get_dashboard_metrics()
except Exception as e:
    st.error(
        "เชื่อมต่อ Neo4j ไม่สำเร็จ "
        "กรุณาตรวจสอบ .streamlit/secrets.toml"
    )
    st.exception(e)
    st.stop()

# =========================================================
# No Users
# =========================================================
if not users:
    st.markdown(
        """
        <div class="hero">
            <h1>🎌 AnimeGraph</h1>
            <p>ระบบแนะนำอนิเมะด้วย Graph Database</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning("ยังไม่มีข้อมูลในฐานข้อมูล")

    if st.button(
        "🚀 โหลดข้อมูลตัวอย่าง 10 User / 10 Anime",
        use_container_width=True,
    ):
        seed_demo_data()
        st.rerun()

    st.stop()

# =========================================================
# Users
# =========================================================
names = {u["user_id"]: u["name"] for u in users}

# =========================================================
# Sidebar
# =========================================================
with st.sidebar:
    st.markdown("## 🎌 AnimeGraph")
    st.caption("Anime Recommendation System")

    uid = st.selectbox(
        "👤 ผู้ใช้งาน",
        list(names),
        format_func=lambda i: f"{names[i]}  ·  {i}",
    )

    limit = st.slider(
        "จำนวน Anime ที่แนะนำ",
        3,
        10,
        5,
    )

    st.divider()

    st.caption("Graph overview")

    st.metric(
        "👤 Users",
        stats["users"],
    )

    st.metric(
        "🎬 Anime",
        stats["anime"],
    )

    st.metric(
        "🔗 Friendships",
        stats["friendships"],
    )

    st.metric(
        "👁️ Watched",
        stats["watched"],
    )

# =========================================================
# Hero
# =========================================================
st.markdown(
    f"""
    <div class="hero">
        <h1>🎌 Anime Recommendation</h1>
        <p>
            สวัสดี <b>{names[uid]}</b>
            — ค้นหาอนิเมะจากความสัมพันธ์ในกราฟของคุณ
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Dashboard Metrics
# =========================================================
m1, m2, m3, m4 = st.columns(4)

m1.metric("Users", stats["users"])
m2.metric("Anime", stats["anime"])
m3.metric("Watched", stats["watched"])
m4.metric("Friendships", stats["friendships"])

st.write("")

# =========================================================
# Tabs
# =========================================================
tab_rec, tab_graph, tab_profile, tab_search, tab_manage = st.tabs([
    "✨ แนะนำสำหรับคุณ",
    "🕸️ Anime Graph",
    "👤 โปรไฟล์",
    "🔎 ค้นหา Anime",
    "⚙️ จัดการข้อมูล",
])

# =========================================================
# Recommendation
# =========================================================
with tab_rec:
    st.subheader("✨ Anime ที่น่าจะเหมาะกับคุณ")

    st.caption(
        "คะแนนมาจากจำนวนเพื่อนที่คุณเชื่อมโยงด้วย "
        "และเคยดู Anime เรื่องนั้น"
    )

    df = pd.DataFrame(recommend_anime(uid, limit))

    if df.empty:
        st.info(
            "ยังไม่มีคำแนะนำสำหรับผู้ใช้นี้ "
            "ลองเพิ่ม WATCHED ให้เพื่อนก่อน"
        )
    else:
        cols = st.columns(min(3, len(df)))

        for i, row in df.iterrows():
            with cols[i % len(cols)]:
                anime_id = str(row["anime_id"])
                title = str(row["title"])
                score = row["score"]
                image_url = ANIME_IMAGES.get(anime_id)

                friends = row.get("watched_by_friends", [])
                if friends is None:
                    friends = []
                if not isinstance(friends, (list, tuple)):
                    friends = [str(friends)]

                friend_text = (
                    ", ".join(str(x) for x in friends[:3])
                    if friends
                    else "ยังไม่มีข้อมูล"
                )

                if image_url:
                    image_html = (
                        f'<img class="anime-card-image" src="{image_url}" '
                        f'alt="{title}" loading="lazy">'
                    )
                else:
                    image_html = (
                        '<div class="anime-card-image" style="display:flex;'
                        'align-items:center;justify-content:center;">'
                        "🎌 ไม่พบรูป Anime</div>"
                    )

                card_html = f"""
                        <div class="anime-card">
                            {image_html}
                            <div class="anime-card-body">
                                <span class="pill">{anime_id}</span>
                                <div class="anime-card-title">🎬 {title}</div>
                                <div class="anime-card-score">{score} <span class="small">คะแนน</span></div>
                                <div class="anime-card-friends">👥 เพื่อนที่เคยดู: {friend_text}</div>
                            </div>
                        </div>
                        """

                st.markdown(card_html, unsafe_allow_html=True)

        st.write("")
        st.markdown("### 📊 อันดับ Anime ที่แนะนำ")
        st.caption(
            "เรียงตามจำนวนเพื่อนที่คุณเชื่อมโยงด้วย "
            "เคยดู Anime เรื่องนั้น"
        )

        max_score = max(1, int(df["score"].max()))

        for rank, (_, rec) in enumerate(df.iterrows(), start=1):
            title = str(rec["title"])
            score = int(rec["score"])
            percent = max(0, min(100, int((score / max_score) * 100)))

            friends = rec.get("watched_by_friends", [])
            if not isinstance(friends, (list, tuple)):
                friends = []
            friend_text = (
                ", ".join(map(str, friends[:3])) if friends else "ไม่มีข้อมูล"
            )

            html = f"""<div class="rank-card">
<div class="rank-no">#{rank}</div>
<div class="rank-info">
<div class="rank-title">🎬 {title}</div>
<div class="rank-friends">👥 เพื่อนที่เคยดู: {friend_text}</div>
<div class="rank-track"><div class="rank-fill" style="width:{percent}%;"></div></div>
</div>
<div class="rank-score"><b>{score}</b><span>คะแนน</span></div>
</div>"""

            st.markdown(html, unsafe_allow_html=True)

# =========================================================
# Anime Graph
# =========================================================
with tab_graph:
    st.subheader("🕸️ กราฟความสัมพันธ์ของคุณ")

    st.caption(
        "โหนดสีม่วง = User · "
        "โหนดสีเหลือง = Anime · "
        "เส้นแสดง FRIEND_OF / WATCHED"
    )

    rows = graph_neighborhood(uid)

    if rows:
        nodes = {}
        edges = []

        for r in rows:
            source_name = r["source_name"]
            target_name = r["target_name"]

            source_label = r["source_label"]
            target_label = r["target_label"]

            nodes[source_name] = source_label
            nodes[target_name] = target_label

            edges.append((
                source_name,
                target_name,
                r["relationship"],
            ))

        def esc(value):
            return str(value).replace(
                '"',
                "'",
            )

        dot = [
            "graph G {",
            ('graph [rankdir=LR, bgcolor="transparent", pad="0.3"];'),
            (
                'node [fontname="Arial", style="filled", color="#cbd5e1",'
                " penwidth=1.5];"
            ),
            (
                'edge [fontname="Arial", color="#94a3b8", fontcolor="#64748b",'
                " penwidth=1.4];"
            ),
        ]

        for node_name, label in nodes.items():
            if label == "User":
                fill = "#ddd6fe" if node_name != names[uid] else "#a78bfa"

                dot.append(
                    f'"{esc(node_name)}" [shape=circle, fillcolor="{fill}",'
                    f' label="{esc(node_name)}"];'
                )
            else:
                dot.append(
                    f'"{esc(node_name)}" [shape=box, style="rounded,filled",'
                    f' fillcolor="#fef3c7", label="{esc(node_name)}"];'
                )

        for source, target, relationship in edges:
            dot.append(
                f'"{esc(source)}" -- "{esc(target)}" [label="{esc(relationship)}"];'
            )

        dot.append("}")

        st.graphviz_chart(
            "\n".join(dot),
            use_container_width=True,
        )

        with st.expander("ดูข้อมูลเส้นความสัมพันธ์"):
            st.dataframe(
                pd.DataFrame(rows),
                hide_index=True,
                use_container_width=True,
            )

    else:
        st.info("ยังไม่มีเส้นทางในกราฟ")

# =========================================================
# Profile
# =========================================================
with tab_profile:
    p = get_profile(uid)

    left, right = st.columns([1, 2])

    with left:
        with st.container(border=True):
            st.caption("USER ID")
            st.subheader(p["user_id"])
            st.caption("ชื่อผู้ใช้")
            st.subheader(f"👤 {p['name']}")

    with right:
        watched = pd.DataFrame(p.get("watched", []))
        st.subheader("📺 ประวัติการดู")

        if watched.empty:
            st.info("ยังไม่มีประวัติการดู")
        else:
            watched = watched.rename(
                columns={
                    "anime_id": "รหัส",
                    "title": "Anime",
                }
            )
            st.dataframe(
                watched,
                hide_index=True,
                use_container_width=True,
            )

# =========================================================
# Search Anime
# =========================================================
with tab_search:
    st.subheader("🔎 ค้นหา Anime")

    keyword = st.text_input(
        "พิมพ์ชื่อ Anime",
        placeholder="เช่น Naruto, One Piece...",
    )

    if keyword.strip():
        result = pd.DataFrame(search_anime(keyword.strip()))

        st.dataframe(
            result.rename(
                columns={
                    "anime_id": "รหัส",
                    "title": "Anime",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("พิมพ์ชื่อ Anime เพื่อค้นหา")

# =========================================================
# Manage Data
# =========================================================
with tab_manage:
    st.subheader("⚙️️ จัดการข้อมูล")

    with st.expander("🚀 โหลดข้อมูลตัวอย่าง"):
        st.write(
            "สร้างข้อมูล User 10 คน, Anime 10 เรื่อง และความสัมพันธ์ สำหรับทดลองระบบ"
        )

        if st.button(
            "โหลด / อัปเดต Demo Data",
            use_container_width=True,
        ):
            seed_demo_data()
            st.success("โหลดข้อมูลเรียบร้อย")
            st.rerun()

    st.markdown("---")

    # 1. บันทึกประวัติการดูสำหรับ User
    anime_rows = search_anime("")
    amap = (
        {item["anime_id"]: item["title"] for item in anime_rows}
        if anime_rows
        else {}
    )

    with st.form("watch_form"):
        st.markdown(f"### 📺 เพิ่ม Anime ที่ดูแล้ว (สำหรับ {names[uid]})")

        if amap:
            a = st.selectbox(
                "Anime",
                list(amap),
                format_func=lambda x: f"{x} — {amap[x]}",
            )
        else:
            a = None
            st.info("ยังไม่มีรายการ Anime ในระบบ")

        d = st.date_input("วันที่ดู")

        if st.form_submit_button("บันทึก WATCHED", use_container_width=True):
            if a:
                record_watched(
                    uid,
                    a,
                    str(d),
                )
                st.success("บันทึกข้อมูลแล้ว")
                st.rerun()
            else:
                st.warning("กรุณาเลือก Anime ก่อนบันทึก")

    st.markdown("---")

    # 2. ระบบจัดการ User และ Anime สำหรับ Admin
    st.markdown("### 🛠️ จัดการข้อมูล Node & ความสัมพันธ์ ใน Neo4j (สำหรับ Admin)")

    admin_pass = st.secrets.get("neo4j", {}).get("ADMIN_PASSWORD", "1234")
    admin_input = st.text_input(
        "🔑 กรอกรหัสผ่าน Admin เพื่อเปิดเมนูจัดการ Node",
        type="password",
        key="admin_purple_manage_key",
    )

    if admin_input == str(admin_pass):
        st.success("🔓 สิทธิ์ Admin ถูกต้อง")

        tab_add_user, tab_add_node, tab_del_node = st.tabs([
            "👤➕ เพิ่ม User ใหม่ & เชื่อมความสัมพันธ์",
            "➕ เพิ่ม Anime ใหม่",
            "🗑 ลบ Anime ถาวร",
        ])

        # --- เพิ่ม User ใหม่ + เชื่อม FRIEND_OF + เชื่อม WATCHED ---
        with tab_add_user:
            with st.form("add_user_form"):
                st.markdown("#### 👤 1. ข้อมูลผู้ใช้ใหม่")
                new_uid = st.text_input("User ID (เช่น U011):")
                new_uname = st.text_input("ชื่อผู้ใช้งาน (เช่น Alice):")

                st.markdown("#### 🔗 2. เชื่อมความเป็นเพื่อน (FRIEND_OF)")
                selected_friends = st.multiselect(
                    "เลือกเพื่อนสนิทในระบบ:",
                    options=list(names.keys()),
                    format_func=lambda x: f"{names[x]} · {x}",
                )

                st.markdown("#### 📺 3. เชื่อมการดูอนิเมะเรื่องเดียวกัน (WATCHED)")
                selected_animes = st.multiselect(
                    "เลือก Anime ที่เคยดู:",
                    options=list(amap.keys()),
                    format_func=lambda x: f"{x} — {amap[x]}",
                )
                watch_date = st.date_input("วันที่ดู", key="new_user_watch_date")

                if st.form_submit_button("➕ บันทึก User ใหม่และเชื่อมความสัมพันธ์", use_container_width=True):
                    clean_uid = new_uid.strip()
                    clean_uname = new_uname.strip()

                    if clean_uid and clean_uname:
                        # 1. สร้าง Node User
                        q_create_user = """
                        MERGE (u:User {user_id: $uid})
                        SET u.name = $name
                        """
                        query(q_create_user, {"uid": clean_uid, "name": clean_uname}, write=True)

                        # 2. สร้างความสัมพันธ์ FRIEND_OF แบบสองทาง
                        for fid in selected_friends:
                            q_friend = """
                            MATCH (u1:User {user_id: $uid})
                            MATCH (u2:User {user_id: $fid})
                            MERGE (u1)-[:FRIEND_OF]->(u2)
                            MERGE (u2)-[:FRIEND_OF]->(u1)
                            """
                            query(q_friend, {"uid": clean_uid, "fid": fid}, write=True)

                        # 3. สร้างความสัมพันธ์ WATCHED
                        for aid in selected_animes:
                            record_watched(clean_uid, aid, str(watch_date))

                        st.success(f"เพิ่มผู้ใช้ {clean_uname} ({clean_uid}) และสร้างความสัมพันธ์เรียบร้อย!")
                        st.rerun()
                    else:
                        st.warning("กรุณากรอก User ID และ ชื่อผู้ใช้งาน ให้ครบถ้วน")

        # --- เพิ่ม Node Anime ---
        with tab_add_node:
            with st.form("add_anime_node_purple"):
                new_aid = st.text_input("Anime ID (เช่น A011):")
                new_title = st.text_input("ชื่อเรื่อง Anime:")

                if st.form_submit_button(
                    "➕ บันทึกอนิเมะเข้า Neo4j", use_container_width=True
                ):
                    if new_aid.strip() and new_title.strip():
                        q_add = """
                        MERGE (a:Anime {anime_id: $aid})
                        SET a.title = $title
                        """
                        query(
                            q_add,
                            {"aid": new_aid.strip(), "title": new_title.strip()},
                            write=True,
                        )
                        st.success(
                            f"เพิ่มอนิเมะ '{new_title}' ({new_aid}) เรียบร้อยแล้ว!"
                        )
                        st.rerun()
                    else:
                        st.warning("กรุณากรอกข้อมูล ID และชื่อเรื่องให้ครบถ้วน")

        # --- ลบ Node Anime ---
        with tab_del_node:
            if amap:
                del_target = st.selectbox(
                    "เลือก Anime ที่ต้องการลบ:",
                    list(amap),
                    format_func=lambda x: f"{x} — {amap[x]}",
                    key="del_anime_select",
                )

                if st.button(
                    "🗑️ ยืนยันลบ Anime Node",
                    type="primary",
                    use_container_width=True,
                ):
                    q_del = "MATCH (a:Anime {anime_id: $aid}) DETACH DELETE a"
                    query(q_del, {"aid": del_target}, write=True)
                    st.success(f"ลบ Anime {del_target} ออกจากระบบแล้ว!")
                    st.rerun()
            else:
                st.info("ไม่มีรายการ Anime ให้ลบ")

    elif admin_input != "":
        st.error("❌ รหัสผ่าน Admin ไม่ถูกต้อง")
    else:
        st.info(
            "🔒 กรุณากรอกรหัสผ่าน Admin "
            " เพื่อเพิ่มหรือลบ Node และความสัมพันธ์"
        )
