import sqlite3

conn = sqlite3.connect("parking.db")

cur = conn.cursor()
#홈페이지에서 사용자가 특정 주차장을 선택하고 예약을 눌럿다고 가정 아래 query 는 임의로 사용자와 주차장을 선택하여 쿼리함

cur.execute("create trigger ytrigger after delete on 예약 BEGIN update 사용자 set 예약여부='N' where 사용자ID=old.사용자ID and not exists(select * from 예약 where 사용자ID=old.사용자ID); end")
cur.execute("create trigger ntrigger after insert on 예약 BEGIN update 사용자 set 예약여부='Y' where 사용자ID= new.사용자ID; end")

#
conn.commit
conn.close()
