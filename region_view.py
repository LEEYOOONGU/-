import sqlite3

conn = sqlite3.connect("parking.db")

cur = conn.cursor()

cur.execute("create view busan as select * from 전국주차장표준데이터 where 소재지도로명주소 like '%부산%'")
cur.execute("create view seoul as select * from 전국주차장표준데이터 where 소재지도로명주소 like '%서울특별시%'")
cur.execute("create view kyoungki as select * from 전국주차장표준데이터 where 소재지도로명주소 like '%경기도%'")


conn.commit()
conn.close()
