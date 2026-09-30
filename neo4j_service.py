from __future__ import annotations
from typing import Any
import streamlit as st
from neo4j import GraphDatabase, RoutingControl

def _config() -> tuple[str, str, str, str]:
    cfg = st.secrets['neo4j']
    return cfg['uri'], cfg['username'], cfg['password'], cfg.get('database', 'neo4j')

@st.cache_resource(show_spinner=False)
def get_driver():
    uri, username, password, _ = _config()
    driver = GraphDatabase.driver(uri, auth=(username, password))
    driver.verify_connectivity()
    return driver

def query(cypher: str, parameters: dict[str, Any] | None = None, *, write: bool = False) -> list[dict[str, Any]]:
    _, _, _, database = _config()
    records, _, _ = get_driver().execute_query(cypher, parameters_=parameters or {}, database_=database,
                                               routing_=RoutingControl.WRITE if write else RoutingControl.READ)
    return [record.data() for record in records]

def ping() -> bool:
    rows = query('RETURN 1 AS ok')
    return bool(rows and rows[0]['ok'] == 1)

def create_schema() -> None:
    for stmt in [
        'CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE',
        'CREATE CONSTRAINT anime_id_unique IF NOT EXISTS FOR (a:Anime) REQUIRE a.anime_id IS UNIQUE',
    ]:
        query(stmt, write=True)

def seed_demo_data() -> None:
    create_schema()
    users = [
        {'user_id':'U001','name':'Mint'}, {'user_id':'U002','name':'Non'},
        {'user_id':'U003','name':'Fah'}, {'user_id':'U004','name':'Ton'},
        {'user_id':'U005','name':'Bank'}, {'user_id':'U006','name':'Aom'},
        {'user_id':'U007','name':'Beam'}, {'user_id':'U008','name':'Nene'},
        {'user_id':'U009','name':'Game'}, {'user_id':'U010','name':'Palm'},
    ]
    anime = [
        {'anime_id':'A001','title':'One Piece'}, {'anime_id':'A002','title':'Naruto'},
        {'anime_id':'A003','title':'Demon Slayer'}, {'anime_id':'A004','title':'Attack on Titan'},
        {'anime_id':'A005','title':'Jujutsu Kaisen'}, {'anime_id':'A006','title':'My Hero Academia'},
        {'anime_id':'A007','title':'Haikyuu!!'}, {'anime_id':'A008','title':'Spy x Family'},
        {'anime_id':'A009','title':'Death Note'}, {'anime_id':'A010','title':'Dragon Ball'},
    ]
    friendships = [(1,2),(1,3),(1,4),(2,5),(2,6),(3,7),(3,8),(4,9),(5,10),(6,7),(8,9),(9,10)]
    watched = [
        ('U001','A001','2026-08-01'),('U001','A005','2026-08-04'),
        ('U002','A002','2026-08-02'),('U002','A003','2026-08-05'),('U002','A009','2026-08-09'),
        ('U003','A003','2026-08-03'),('U003','A004','2026-08-07'),
        ('U004','A005','2026-08-06'),('U004','A006','2026-08-10'),
        ('U005','A007','2026-08-08'),('U005','A010','2026-08-11'),
        ('U006','A006','2026-08-12'),('U006','A008','2026-08-14'),
        ('U007','A003','2026-08-13'),('U007','A007','2026-08-15'),
        ('U008','A008','2026-08-16'),('U008','A009','2026-08-18'),
        ('U009','A004','2026-08-17'),('U009','A010','2026-08-19'),
        ('U010','A002','2026-08-20'),('U010','A009','2026-08-21'),
    ]
    query('UNWIND $rows AS row MERGE (u:User {user_id:row.user_id}) SET u.name=row.name', {'rows':users}, write=True)
    query('UNWIND $rows AS row MERGE (a:Anime {anime_id:row.anime_id}) SET a.title=row.title', {'rows':anime}, write=True)
    query('UNWIND $rows AS row MATCH (a:User {user_id:row[0]}),(b:User {user_id:row[1]}) MERGE (a)-[:FRIEND_OF]->(b)', {'rows':friendships}, write=True)
    query('UNWIND $rows AS row MATCH (u:User {user_id:row[0]}),(a:Anime {anime_id:row[1]}) MERGE (u)-[r:WATCHED]->(a) SET r.watch_date=date(row[2])', {'rows':watched}, write=True)

def get_users() -> list[dict[str, Any]]:
    return query('MATCH (u:User) RETURN u.user_id AS user_id,u.name AS name ORDER BY user_id')

def get_dashboard_metrics() -> dict[str,int]:
    rows=query('MATCH (u:User) WITH count(u) AS users MATCH (a:Anime) WITH users,count(a) AS anime MATCH ()-[w:WATCHED]->() WITH users,anime,count(w) AS watched MATCH ()-[f:FRIEND_OF]->() RETURN users,anime,watched,count(f) AS friendships')
    return rows[0] if rows else {'users':0,'anime':0,'watched':0,'friendships':0}

def get_profile(user_id:str):
    rows=query('MATCH (u:User {user_id:$user_id}) OPTIONAL MATCH (u)-[:WATCHED]->(a:Anime) RETURN u.user_id AS user_id,u.name AS name,collect(DISTINCT {anime_id:a.anime_id,title:a.title}) AS watched',{'user_id':user_id})
    if not rows:return None
    rows[0]['watched']=[x for x in rows[0]['watched'] if x.get('anime_id')]
    return rows[0]

def recommend_anime(user_id:str, limit:int=8):
    return query('''MATCH (u:User {user_id:$user_id}) MATCH (a:Anime) WHERE NOT (u)-[:WATCHED]->(a)
OPTIONAL MATCH (u)-[:FRIEND_OF]-(f:User)-[:WATCHED]->(a)
WITH a,count(DISTINCT f) AS friend_count,collect(DISTINCT f.name) AS friend_names
WHERE friend_count > 0
RETURN a.anime_id AS anime_id,a.title AS title,friend_count AS score,[x IN friend_names WHERE x IS NOT NULL][0..3] AS watched_by_friends
ORDER BY score DESC,title LIMIT $limit''',{'user_id':user_id,'limit':int(limit)})

def search_anime(keyword:str=''):
    return query('MATCH (a:Anime) WHERE $keyword="" OR toLower(a.title) CONTAINS toLower($keyword) RETURN a.anime_id AS anime_id,a.title AS title ORDER BY a.title',{'keyword':keyword.strip()})

def record_watched(user_id:str, anime_id:str, watch_date:str):
    query('MATCH (u:User {user_id:$user_id}),(a:Anime {anime_id:$anime_id}) MERGE (u)-[r:WATCHED]->(a) SET r.watch_date=date($watch_date)',{'user_id':user_id,'anime_id':anime_id,'watch_date':watch_date},write=True)

def graph_neighborhood(user_id:str, limit:int=40):
    return query('''MATCH (u:User {user_id:$user_id}) OPTIONAL MATCH p=(u)-[:FRIEND_OF|WATCHED*1..2]-(x)
WITH collect(p)[0..$limit] AS paths UNWIND paths AS p UNWIND relationships(p) AS r
WITH DISTINCT startNode(r) AS s,r,endNode(r) AS t
RETURN elementId(s) AS source_id,labels(s)[0] AS source_label,coalesce(s.name,s.title,s.user_id,s.anime_id) AS source_name,type(r) AS relationship,elementId(t) AS target_id,labels(t)[0] AS target_label,coalesce(t.name,t.title,t.user_id,t.anime_id) AS target_name LIMIT $limit''',{'user_id':user_id,'limit':int(limit)})
