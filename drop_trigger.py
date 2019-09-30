import sqlite3

conn = sqlite3.connect("parking.db")

cur = conn.cursor()
#홈페이지에서 사용자가 특정 주차장을 선택하고 예약을 눌럿다고 가정 아래 query 는 임의로 사용자와 주차장을 선택하여 쿼리함
cur.execute("drop trigger ytrigger")
cur.execute("drop trigger ntrigger")

conn.commit()
conn.close()
