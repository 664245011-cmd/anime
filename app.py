import pandas as pd
import streamlit as st
from neo4j_service import (get_users, get_dashboard_metrics, get_profile, recommend_anime,
                           search_anime, record_watched, graph_neighborhood, seed_demo_data, query)

st.set_page_config(page_title='Anime Recommendation', page_icon='🎌', layout='wide')
st.title('🎌 Anime Recommendation System')
st.caption('Graph Database · Neo4j Aura · Cypher — แนะนำอนิเมะจากเครือข่ายเพื่อน')

try:
    users = get_users()
    stats = get_dashboard_metrics()
except Exception as e:
    st.error('เชื่อมต่อ Neo4j ไม่สำเร็จ ตรวจสอบ .streamlit/secrets.toml')
    st.exception(e)
    st.stop()

if not users:
    st.warning('ยังไม่มีข้อมูล User ในฐานข้อมูล')
    if st.button('โหลดข้อมูลตัวอย่าง (10 User / 10 Anime)'):
        seed_demo_data(); st.rerun()
    st.stop()

with st.sidebar:
    st.header('ตั้งค่า')
    names = {u['user_id']:u['name'] for u in users}
    uid = st.selectbox('เลือกผู้ใช้', list(names), format_func=lambda i:f'{i} — {names[i]}')
    limit = st.slider('จำนวนอนิเมะที่แนะนำ',1,10,5)
    st.divider()
    c1,c2=st.columns(2)
    c1.metric('Nodes', stats['users']+stats['anime'])
    c2.metric('Relationships', stats['watched']+stats['friendships'])

st.subheader(f'ผลการแนะนำสำหรับ {names[uid]}')
tab_rec, tab_profile, tab_search, tab_manage, tab_graph = st.tabs(['🎌 อนิเมะที่แนะนำ','👤 โปรไฟล์','🔎 ค้นหา Anime','🛠️ จัดการข้อมูล','🕸️ กราฟเครือข่าย'])

df = pd.DataFrame(recommend_anime(uid,limit))
with tab_rec:
    if df.empty: st.info('ไม่พบอนิเมะที่แนะนำ — ลองเพิ่มข้อมูล WATCHED ของเพื่อน')
    else:
        show=df.copy(); show['watched_by_friends']=show['watched_by_friends'].apply(lambda x:', '.join(x) if x else '-')
        show=show.rename(columns={'anime_id':'รหัส','title':'อนิเมะ','score':'คะแนน','watched_by_friends':'เพื่อนที่เคยดู'})
        st.dataframe(show,hide_index=True,use_container_width=True)
        st.bar_chart(df.set_index('title')['score'])

with tab_profile:
    p=get_profile(uid)
    st.write(f"**User:** {p['name']} ({p['user_id']})")
    watched=pd.DataFrame(p['watched'])
    if watched.empty: st.info('ยังไม่มีประวัติการดู')
    else: st.dataframe(watched.rename(columns={'anime_id':'รหัส','title':'อนิเมะ'}),hide_index=True,use_container_width=True)

with tab_search:
    keyword=st.text_input('ค้นหาชื่อ Anime')
    result=pd.DataFrame(search_anime(keyword))
    st.dataframe(result.rename(columns={'anime_id':'รหัส','title':'อนิเมะ'}),hide_index=True,use_container_width=True)

with tab_manage:
    with st.expander('โหลดข้อมูลตัวอย่าง (10 User / 10 Anime / relationships)'):
        if st.button('โหลดข้อมูลตัวอย่าง'): seed_demo_data(); st.success('โหลดข้อมูลแล้ว'); st.rerun()
    st.markdown('**บันทึก Anime ที่ User ดูแล้ว**')
    anime_rows=search_anime('')
    amap={x['anime_id']:x['title'] for x in anime_rows}
    with st.form('watch_form'):
        a=st.selectbox('Anime',list(amap),format_func=lambda x:f'{x} — {amap[x]}')
        d=st.date_input('วันที่ดู')
        if st.form_submit_button('บันทึก WATCHED'):
            record_watched(uid,a,str(d)); st.success('บันทึกแล้ว'); st.rerun()

with tab_graph:
    rows=graph_neighborhood(uid)
    if rows:
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    else: st.info('ยังไม่มีเส้นทางในกราฟสำหรับ User นี้')
