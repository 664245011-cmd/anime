import os
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
                # รูปอยู่โฟลเดอร์เดียวกับ app.py
                # เช่น app.py + A001.png
                # =================================================
                image_path = os.path.join(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    ),
                    f"{anime_id}.png",
                )

                if os.path.exists(image_path):
                    st.image(
                        image_path,
                        use_container_width=True,
                    )
                else:
                    st.warning(
                        f"ไม่พบรูป {anime_id}.png"
                    )

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

    result = pd.DataFrame(
        search_anime(keyword)
    )

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
                a,import pandas as pd
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
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AnimeGraph Recommendation",
    page_icon="🎌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# ANIME IMAGE URLS
# ใช้รูปออนไลน์โดยตรง ไม่ต้องใช้ A001.png - A010.png
# =========================================================
ANIME_IMAGES = {
    "A001": "https://cdn.myanimelist.net/images/anime/1244/138851l.jpg",  # One Piece
    "A002": "https://cdn.myanimelist.net/images/anime/1141/142503l.jpg",  # Naruto
    "A003": "https://cdn.myanimelist.net/images/anime/1286/99889l.jpg",   # Demon Slayer
    "A004": "https://cdn.myanimelist.net/images/anime/10/47347l.jpg",     # Attack on Titan
    "A005": "https://cdn.myanimelist.net/images/anime/1171/109636l.jpg",  # Jujutsu Kaisen
    "A006": "https://cdn.myanimelist.net/images/anime/10/78745l.jpg",     # My Hero Academia
    "A007": "https://cdn.myanimelist.net/images/anime/1079/138100l.jpg",  # Death Note
    "A008": "https://cdn.myanimelist.net/images/anime/7/76014l.jpg",      # Haikyuu!!
    "A009": "https://cdn.myanimelist.net/images/anime/12/76049l.jpg",     # One Punch Man
    "A010": "https://cdn.myanimelist.net/images/anime/6/73245l.jpg",      # Dragon Ball
}

# ชื่อสำรอง เผื่อ Neo4j คืน title มาแต่ไม่มี anime_id
ANIME_TITLE_IMAGES = {
    "one piece": ANIME_IMAGES["A001"],
    "naruto": ANIME_IMAGES["A002"],
    "demon slayer": ANIME_IMAGES["A003"],
    "kimetsu no yaiba": ANIME_IMAGES["A003"],
    "attack on titan": ANIME_IMAGES["A004"],
    "shingeki no kyojin": ANIME_IMAGES["A004"],
    "jujutsu kaisen": ANIME_IMAGES["A005"],
    "my hero academia": ANIME_IMAGES["A006"],
    "boku no hero academia": ANIME_IMAGES["A006"],
    "death note": ANIME_IMAGES["A007"],
    "haikyuu": ANIME_IMAGES["A008"],
    "haikyuu!!": ANIME_IMAGES["A008"],
    "one punch man": ANIME_IMAGES["A009"],
    "one-punch man": ANIME_IMAGES["A009"],
    "dragon ball": ANIME_IMAGES["A010"],
}


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Prompt', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(100, 80, 180, 0.14), transparent 30%),
        radial-gradient(circle at bottom right, rgba(30, 100, 180, 0.10), transparent 30%),
        #0b0f17;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 28px 30px;
    border-radius: 24px;
    background: linear-gradient(
        135deg,
        rgba(255,255,255,0.09),
        rgba(255,255,255,0.035)
    );
    border: 1px solid rgba(255,255,255,0.10);
    margin-bottom: 24px;
}

.hero h1 {
    margin: 0;
    font-size: 34px;
    font-weight: 800;
}

.hero p {
    margin-top: 8px;
    opacity: 0.72;
}

.metric-card {
    padding: 20px;
    border-radius: 18px;
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.08);
}

.metric-number {
    font-size: 28px;
    font-weight: 800;
}

.metric-label {
    opacity: 0.65;
    font-size: 14px;
}

.anime-card {
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 20px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.anime-card:hover {
    transform: translateY(-4px);
    border-color: rgba(255,255,255,0.25);
}

.anime-image {
    width: 100%;
    height: 310px;
    overflow: hidden;
    background: #151923;
}

.anime-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

.anime-content {
    padding: 17px;
}

.anime-title {
    font-size: 21px;
    line-height: 1.25;
    font-weight: 700;
    margin-bottom: 8px;
}

.anime-id {
    opacity: 0.55;
    font-size: 13px;
}

.anime-score {
    margin-top: 12px;
    font-size: 17px;
    font-weight: 700;
}

.anime-friends {
    margin-top: 8px;
    font-size: 13px;
    opacity: 0.70;
}

.section-title {
    font-size: 25px;
    font-weight: 700;
    margin: 10px 0 16px 0;
}

.card {
    padding: 18px;
    border-radius: 18px;
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 14px;
}

.small {
    font-size: 13px;
    opacity: 0.65;
}

.rank-card {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 14px;
    border-radius: 16px;
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 10px;
}

.rank-no {
    font-size: 22px;
    font-weight: 800;
    width: 35px;
}

.rank-title {
    font-weight: 700;
}

.rank-info {
    flex: 1;
}

.rank-friends {
    font-size: 12px;
    opacity: 0.6;
}

.rank-score {
    font-weight: 800;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================
def clean_value(value, default=""):
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except Exception:
        pass
    return value


def get_anime_image(anime_id="", title=""):
    anime_id = str(clean_value(anime_id, "")).strip()
    title = str(clean_value(title, "")).strip().lower()

    if anime_id in ANIME_IMAGES:
        return ANIME_IMAGES[anime_id]

    return ANIME_TITLE_IMAGES.get(title)


def get_row_value(row, names, default=""):
    for name in names:
        if name in row.index:
            value = clean_value(row[name], default)
            if value != default:
                return value
    return default


def normalize_friends(value):
    if value is None:
        return []

    try:
        if pd.isna(value):
            return []
    except Exception:
        pass

    if isinstance(value, (list, tuple, set)):
        return [str(x) for x in value if x]

    if isinstance(value, str):
        if not value.strip():
            return []
        return [x.strip() for x in value.split(",") if x.strip()]

    return [str(value)]


# =========================================================
# CONNECT NEO4J
# =========================================================
try:
    users = get_users()
except Exception as e:
    st.error("ไม่สามารถเชื่อมต่อ Neo4j ได้")
    st.code(str(e))
    st.stop()

if not users:
    st.warning("ยังไม่มีข้อมูลผู้ใช้ในระบบ")
    st.info("ไปที่แท็บ Data Management เพื่อ Seed Demo Data")
    st.stop()


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 🎌 AnimeGraph")

    user_options = {}

    for user in users:
        if isinstance(user, dict):
            uid = (
                user.get("user_id")
                or user.get("id")
                or user.get("uid")
                or user.get("username")
            )
            name = (
                user.get("name")
                or user.get("username")
                or user.get("user_id")
                or uid
            )
        else:
            uid = str(user)
            name = str(user)

        if uid is not None:
            user_options[str(name)] = uid

    if not user_options:
        st.error("ไม่พบ User ที่ใช้งานได้")
        st.stop()

    selected_name = st.selectbox(
        "เลือก User",
        list(user_options.keys()),
    )

    selected_uid = user_options[selected_name]

    limit = st.slider(
        "จำนวน Anime ที่แนะนำ",
        min_value=3,
        max_value=10,
        value=10,
    )

    st.divider()

    st.caption("Anime images are loaded from online image URLs.")
    st.caption("ไม่จำเป็นต้องมี A001.png - A010.png")


# =========================================================
# HERO
# =========================================================
st.markdown(
    """
<div class="hero">
    <h1>🎌 AnimeGraph Recommendation</h1>
    <p>ระบบแนะนำ Anime ด้วยความสัมพันธ์ของ User, Anime และการรับชมใน Neo4j</p>
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# DASHBOARD METRICS
# =========================================================
try:
    metrics = get_dashboard_metrics()
except Exception:
    metrics = {}

if isinstance(metrics, dict):
    users_count = metrics.get("users", metrics.get("user_count", 0))
    anime_count = metrics.get("anime", metrics.get("anime_count", 0))
    friendships = metrics.get(
        "friendships",
        metrics.get("friendship_count", metrics.get("friends", 0)),
    )
    watched = metrics.get(
        "watched",
        metrics.get("watched_count", metrics.get("watch_count", 0)),
    )
else:
    users_count = anime_count = friendships = watched = 0

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-number">{users_count}</div>
            <div class="metric-label">Users</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-number">{anime_count}</div>
            <div class="metric-label">Anime</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-number">{friendships}</div>
            <div class="metric-label">Friendships</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-number">{watched}</div>
            <div class="metric-label">Watched</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.write("")


# =========================================================
# TABS
# =========================================================
tab_rec, tab_graph, tab_profile, tab_search, tab_manage = st.tabs(
    [
        "✨ Recommendations",
        "🕸️ Graph",
        "👤 Profile",
        "🔎 Search Anime",
        "⚙️ Data Management",
    ]
)


# =========================================================
# RECOMMENDATIONS
# =========================================================
with tab_rec:
    st.markdown(
        '<div class="section-title">✨ Anime Recommendations</div>',
        unsafe_allow_html=True,
    )

    try:
        recommendations = recommend_anime(selected_uid, limit)
        df = pd.DataFrame(recommendations)
    except Exception as e:
        st.error("เกิดข้อผิดพลาดในการโหลด Recommendation")
        st.code(str(e))
        df = pd.DataFrame()

    if df.empty:
        st.info("ยังไม่มี Anime ที่แนะนำสำหรับ User นี้")
    else:
        # แสดงเป็น 2 คอลัมน์
        for start in range(0, len(df), 2):
            cols = st.columns(2)

            for offset, col in enumerate(cols):
                index = start + offset

                if index >= len(df):
                    continue

                row = df.iloc[index]

                anime_id = get_row_value(
                    row,
                    ["anime_id", "id", "animeId", "AnimeID"],
                    "",
                )

                title = get_row_value(
                    row,
                    ["title", "anime_title", "name", "AnimeTitle"],
                    "Unknown Anime",
                )

                score = get_row_value(
                    row,
                    ["score", "recommendation_score", "similarity", "rating"],
                    0,
                )

                friends = normalize_friends(
                    get_row_value(
                        row,
                        ["friends", "friend_names", "friends_watched"],
                        [],
                    )
                )

                image_url = get_anime_image(anime_id, title)

                friend_text = (
                    "👥 Watched by: " + ", ".join(friends[:3])
                    if friends
                    else "👥 Recommended from your graph"
                )

                if image_url:
                    image_html = f"""
                    <div class="anime-image">
                        <img
                            src="{image_url}"
                            alt="{title}"
                            loading="lazy"
                            onerror="this.style.display='none';"
                        >
                    </div>
                    """
                else:
                    image_html = """
                    <div class="anime-image"
                         style="display:flex;align-items:center;justify-content:center;">
                        <span style="opacity:.5;">🎌 Anime</span>
                    </div>
                    """

                with col:
                    st.markdown(
                        f"""
                        <div class="anime-card">
                            {image_html}

                            <div class="anime-content">
                                <div class="anime-title">
                                    {title}
                                </div>

                                <div class="anime-id">
                                    Anime ID: {anime_id}
                                </div>

                                <div class="anime-score">
                                    ⭐ Score: {score}
                                </div>

                                <div class="anime-friends">
                                    {friend_text}
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


# =========================================================
# GRAPH
# =========================================================
with tab_graph:
    st.markdown(
        '<div class="section-title">🕸️ User Graph Neighborhood</div>',
        unsafe_allow_html=True,
    )

    try:
        graph_data = graph_neighborhood(selected_uid)
    except Exception as e:
        graph_data = None
        st.error("โหลด Graph ไม่สำเร็จ")
        st.code(str(e))

    if graph_data:
        st.write(graph_data)
    else:
        st.info("ยังไม่มีข้อมูล Graph สำหรับ User นี้")


# =========================================================
# PROFILE
# =========================================================
with tab_profile:
    st.markdown(
        '<div class="section-title">👤 User Profile</div>',
        unsafe_allow_html=True,
    )

    try:
        profile = get_profile(selected_uid)
    except Exception as e:
        profile = None
        st.error("โหลด Profile ไม่สำเร็จ")
        st.code(str(e))

    if isinstance(profile, dict):
        p1, p2 = st.columns(2)

        with p1:
            st.markdown(
                f"""
                <div class="card">
                    <div class="small">User ID</div>
                    <h3>{profile.get("user_id", selected_uid)}</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with p2:
            st.markdown(
                f"""
                <div class="card">
                    <div class="small">Name</div>
                    <h3>{profile.get("name", selected_name)}</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

        watched_data = (
            profile.get("watched")
            or profile.get("watched_anime")
            or profile.get("anime")
            or []
        )

        if watched_data:
            st.markdown("### 🎬 Watched Anime")
            st.dataframe(
                pd.DataFrame(watched_data),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("ยังไม่มีประวัติการรับชม")


# =========================================================
# SEARCH
# =========================================================
with tab_search:
    st.markdown(
        '<div class="section-title">🔎 Search Anime</div>',
        unsafe_allow_html=True,
    )

    keyword = st.text_input(
        "ค้นหาชื่อ Anime",
        placeholder="เช่น One Piece, Naruto, Demon Slayer...",
    )

    if keyword.strip():
        try:
            search_result = search_anime(keyword.strip())
            search_df = pd.DataFrame(search_result)
        except Exception as e:
            search_df = pd.DataFrame()
            st.error("ค้นหาไม่สำเร็จ")
            st.code(str(e))

        if search_df.empty:
            st.info("ไม่พบ Anime")
        else:
            st.dataframe(
                search_df,
                use_container_width=True,
                hide_index=True,
            )


# =========================================================
# DATA MANAGEMENT
# =========================================================
with tab_manage:
    st.markdown(
        '<div class="section-title">⚙️ Data Management</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="card">
            <b>Seed Demo Data</b><br>
            สร้างข้อมูลตัวอย่าง User, Anime, Friendship และ Watched
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🌱 Seed Demo Data", use_container_width=True):
        try:
            result = seed_demo_data()
            st.success("Seed Demo Data สำเร็จ")
            if result is not None:
                st.write(result)
            st.rerun()
        except Exception as e:
            st.error("Seed Demo Data ไม่สำเร็จ")
            st.code(str(e))

    st.divider()

    st.markdown("### ➕ เพิ่ม Anime ที่ User ดูแล้ว")

    watched_anime_id = st.selectbox(
        "Anime ID",
        list(ANIME_IMAGES.keys()),
        format_func=lambda x: f"{x} - " + {
            "A001": "One Piece",
            "A002": "Naruto",
            "A003": "Demon Slayer",
            "A004": "Attack on Titan",
            "A005": "Jujutsu Kaisen",
            "A006": "My Hero Academia",
            "A007": "Death Note",
            "A008": "Haikyuu!!",
            "A009": "One Punch Man",
            "A010": "Dragon Ball",
        }.get(x, x),
    )

    if st.button("➕ Record Watched", use_container_width=True):
        try:
            result = record_watched(
                selected_uid,
                watched_anime_id,
            )
            st.success("บันทึกการรับชมสำเร็จ")
            if result is not None:
                st.write(result)
        except Exception as e:
            st.error("บันทึกไม่สำเร็จ")
            st.code(str(e))


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(
    "AnimeGraph Recommendation • Neo4j + Streamlit • "
    "Anime poster images are loaded from remote CDN URLs."
)

                str(d),
            )

            st.success(
                "บันทึกข้อมูลแล้ว"
            )

            st.rerun()
