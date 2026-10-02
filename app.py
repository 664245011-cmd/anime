import pandas as pd
import streamlit as st

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

# =========================================================
# Anime image URLs
# =========================================================
ANIME_IMAGES = {
    "A001": "https://cdn.myanimelist.net/images/anime/1244/138851l.jpg",  # One Piece
    "A002": "https://cdn.myanimelist.net/images/anime/1141/142503l.jpg",  # Naruto
    "A003": "https://cdn.myanimelist.net/images/anime/1286/99889l.jpg",   # Demon Slayer
    "A004": "https://cdn.myanimelist.net/images/anime/10/47347l.jpg",     # Attack on Titan
    "A005": "https://huggingface.co/datasets/deepghs/fancaps_animes/resolve/main/images/40748__jujutsu_kaisen.jpg",  # Jujutsu Kaisen
    "A006": "https://cdn.myanimelist.net/images/anime/10/78745l.jpg",     # My Hero Academia
    "A007": "https://cdn.myanimelist.net/images/anime/1079/138100l.jpg",  # Death Note
    "A008": "https://cdn.myanimelist.net/images/anime/7/76014l.jpg",      # Haikyuu!!
    "A009": "https://cdn.myanimelist.net/images/anime/12/76049l.jpg",     # One Punch Man
    "A010": "https://cdn.myanimelist.net/images/anime/6/73245l.jpg",      # Dragon Ball
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
        padding: 16px 18px;
        border-radius: 16px;
        border: 1px solid rgba(128,128,128,.20);
        background: linear-gradient(
            145deg,
            rgba(99,102,241,.10),
            rgba(168,85,247,.06)
        );
        min-height: 150px;
        margin-top: -4px;
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

    /* ปรับขนาดรูป Anime */
    [data-testid="stImage"] img {
        width: 100%;
        height: 260px;
        object-fit: cover;
        border-radius: 14px;
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
names = {
    u["user_id"]: u["name"]
    for u in users
}

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
tab_rec, tab_graph, tab_profile, tab_search, tab_manage = st.tabs(
    [
        "✨ แนะนำสำหรับคุณ",
        "🕸️ Anime Graph",
        "👤 โปรไฟล์",
        "🔎 ค้นหา Anime",
        "⚙️ จัดการข้อมูล",
    ]
)

# =========================================================
# Recommendation
# =========================================================
with tab_rec:
    st.subheader("✨ Anime ที่น่าจะเหมาะกับคุณ")

    st.caption(
        "คะแนนมาจากจำนวนเพื่อนที่คุณเชื่อมโยงด้วย "
        "และเคยดู Anime เรื่องนั้น"
    )

    df = pd.DataFrame(
        recommend_anime(uid, limit)
    )

    if df.empty:
        st.info(
            "ยังไม่มีคำแนะนำสำหรับผู้ใช้นี้ "
            "ลองเพิ่ม WATCHED ให้เพื่อนก่อน"
        )

    else:
        cols = st.columns(
            min(3, len(df))
        )

        for i, row in df.iterrows():

            with cols[i % len(cols)]:

                anime_id = str(
                    row["anime_id"]
                )

                # =================================================
                # รูป Anime
                # ใช้ URL ออนไลน์โดยตรง ไม่ต้องมี A001.png - A010.png
                # =================================================
                image_url = ANIME_IMAGES.get(anime_id)

                if image_url:
                    st.image(
                        image_url,
                        use_container_width=True,
                    )
                else:
                    st.info(f"ยังไม่มี URL รูปสำหรับ {anime_id}")

                # =================================================
                # ข้อมูลเพื่อน
                # =================================================
                friends = (
                    row.get(
                        "watched_by_friends"
                    )
                    or []
                )

                friend_text = (
                    ", ".join(
                        friends[:3]
                    )
                    if friends
                    else "ยังไม่มีข้อมูล"
                )

                # =================================================
                # Card
                # ใช้ Streamlit แยกส่วน
                # ป้องกัน HTML แสดงเป็นข้อความ
                # =================================================
                st.markdown(
                    '<div class="anime-card">',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f'<span class="pill">{anime_id}</span>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"**🎬 {row['title']}**"
                )

                st.markdown(
                    f"### {row['score']} "
                    f"<span class='small'>คะแนน</span>",
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"👥 เพื่อนที่เคยดู: {friend_text}"
                )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True,
                )

        # =====================================================
        # Ranking
        # =====================================================
        st.write("")

        st.markdown(
            "### 📊 อันดับ Anime ที่แนะนำ"
        )

        st.caption(
            "เรียงตามจำนวนเพื่อนที่คุณเชื่อมโยงด้วย "
            "เคยดู Anime เรื่องนั้น"
        )

        max_score = max(
            1,
            int(df["score"].max()),
        )

        for rank, (_, rec) in enumerate(
            df.iterrows(),
            start=1,
        ):
            title = str(
                rec["title"]
            )

            score = int(
                rec["score"]
            )

            percent = int(
                (score / max_score) * 100
            )

            friends = (
                rec.get(
                    "watched_by_friends"
                )
                or []
            )

            friend_text = (
                ", ".join(
                    friends[:3]
                )
                if friends
                else "ไม่มีข้อมูล"
            )

            html = f"""
            <div class="rank-card">
                <div class="rank-no">
                    #{rank}
                </div>

                <div class="rank-info">
                    <div class="rank-title">
                        🎬 {title}
                    </div>

                    <div class="rank-friends">
                        👥 เพื่อนที่เคยดู:
                        {friend_text}
                    </div>

                    <div class="rank-track">
                        <div
                            class="rank-fill"
                            style="width:{percent}%"
                        ></div>
                    </div>
                </div>

                <div class="rank-score">
                    <b>{score}</b>
                    <span>คะแนน</span>
                </div>
            </div>
            """

            st.markdown(
                html,
                unsafe_allow_html=True,
            )

# =========================================================
# Anime Graph
# =========================================================
with tab_graph:
    st.subheader(
        "🕸️ กราฟความสัมพันธ์ของคุณ"
    )

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

            edges.append(
                (
                    source_name,
                    target_name,
                    r["relationship"],
                )
            )

        def esc(value):
            return str(value).replace(
                '"',
                "'",
            )

        dot = [
            "graph G {",
            (
                'graph [rankdir=LR, '
                'bgcolor="transparent", '
                'pad="0.3"];'
            ),
            (
                'node [fontname="Arial", '
                'style="filled", '
                'color="#cbd5e1", '
                'penwidth=1.5];'
            ),
            (
                'edge [fontname="Arial", '
                'color="#94a3b8", '
                'fontcolor="#64748b", '
                'penwidth=1.4];'
            ),
        ]

        for node_name, label in nodes.items():

            if label == "User":

                fill = (
                    "#ddd6fe"
                    if node_name != names[uid]
                    else "#a78bfa"
                )

                dot.append(
                    f'"{esc(node_name)}" '
                    f'[shape=circle, '
                    f'fillcolor="{fill}", '
                    f'label="{esc(node_name)}"];'
                )

            else:

                dot.append(
                    f'"{esc(node_name)}" '
                    f'[shape=box, '
                    f'style="rounded,filled", '
                    f'fillcolor="#fef3c7", '
                    f'label="{esc(node_name)}"];'
                )

        for source, target, relationship in edges:

            dot.append(
                f'"{esc(source)}" -- '
                f'"{esc(target)}" '
                f'[label="{esc(relationship)}"];'
            )

        dot.append("}")

        st.graphviz_chart(
            "\n".join(dot),
            use_container_width=True,
        )

        with st.expander(
            "ดูข้อมูลเส้นความสัมพันธ์"
        ):
            st.dataframe(
                pd.DataFrame(rows),
                hide_index=True,
                use_container_width=True,
            )

    else:
        st.info(
            "ยังไม่มีเส้นทางในกราฟ"
        )

# =========================================================
# Profile
# =========================================================
with tab_profile:

    p = get_profile(uid)

    left, right = st.columns(
        [1, 2]
    )

    with left:

        st.markdown(
            f"""
            <div class="card">
                <div class="small">
                    USER ID
                </div>

                <h2>
                    {p["user_id"]}
                </h2>

                <div class="small">
                    ชื่อผู้ใช้
                </div>

                <h3>
                    👤 {p["name"]}
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:

        watched = pd.DataFrame(
            p["watched"]
        )

        st.subheader(
            "📺 ประวัติการดู"
        )

        if watched.empty:

            st.info(
                "ยังไม่มีประวัติการดู"
            )

        else:

            st.dataframe(
                watched.rename(
                    columns={
                        "anime_id": "รหัส",
                        "title": "Anime",
                    }
                ),
                hide_index=True,
                use_container_width=True,
            )

# =========================================================
# Search Anime
# =========================================================
with tab_search:

    st.subheader(
        "🔎 ค้นหา Anime"
    )

    keyword = st.text_input(
        "พิมพ์ชื่อ Anime",
        placeholder=(
            "เช่น Naruto, One Piece..."
        ),
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

    st.subheader(
        "⚙️ จัดการข้อมูล"
    )

    with st.expander(
        "🚀 โหลดข้อมูลตัวอย่าง"
    ):

        st.write(
            "สร้างข้อมูล User 10 คน, "
            "Anime 10 เรื่อง และความสัมพันธ์ "
            "สำหรับทดลองระบบ"
        )

        if st.button(
            "โหลด / อัปเดต Demo Data",
            use_container_width=True,
        ):

            seed_demo_data()

            st.success(
                "โหลดข้อมูลเรียบร้อย"
            )

            st.rerun()

    anime_rows = search_anime("")

    amap = {
        item["anime_id"]: item["title"]
        for item in anime_rows
    }

    with st.form(
        "watch_form"
    ):

        st.markdown(
            "### 📺 เพิ่ม Anime ที่ดูแล้ว"
        )

        a = st.selectbox(
            "Anime",
            list(amap),
            format_func=lambda x:
                f"{x} — {amap[x]}",
        )

        d = st.date_input(
            "วันที่ดู"
        )

        if st.form_submit_button(
            "บันทึก WATCHED",
            use_container_width=True,
        ):

            record_watched(
                uid,
                a,
                str(d),
            )

            st.success(
                "บันทึกข้อมูลแล้ว"
            )

            st.rerun()
