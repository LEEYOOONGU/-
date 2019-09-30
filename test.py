import sqlite3
import time
import datetime


conn = sqlite3.connect("parking.db")

cur = conn.cursor()


def freeslot(lotnumber, start_time, end_time):
    cur.execute('select 주차구획수 from 전국주차장표준데이터 where 주차장관리번호 = ?', (lotnumber,))
    max_slot = int(cur.fetchone()[0])

    cur.execute('select * from 예약 where 주차장관리번호 = :number and ((주차시작시간 <= :start and :start <= 주차종료시간) or (주차시작시간 <= :end and :end <= 주차종료시간))',
                {
                    "number": lotnumber,
                    "start": int(start_time.timestamp()),
                    "end": int(end_time.timestamp())
                })
    used_slot = len(cur.fetchall())
    return max_slot-used_slot

def printlot(row, start_time, end_time):
    print("주차장명 : {0}, 도로명주소 : {1}, 남은자리 : {2}/{3}".format(row[1], row[4], freeslot(row[0], start_time, end_time), row[6]))


def printlot(row):
    print("주차장명 : {0}, 도로명주소 : {1}".format(row[1], row[4]))

def printview(row):
    print("주차장명 : {0}, 주차장구분: {1}, 도로명주소 : {2}, 기본요금: {3}, 추가요금: {4}".format(row[1], row[2],row[4],row[19],row[21]))
def usingtime():
    while True:
        print("이용할 시간을 입력해주세요.")
        start_time_str = input("시작시간을 입력해주세요(YYYY-MM-DD HH:MM) : ")
        start_time_obj = datetime.datetime.strptime(start_time_str, '%Y-%m-%d %H:%M')
        end_time_str = input("종료시간을 입력해주세요(YYYY-MM-DD HH:MM) : ")
        end_time_obj = datetime.datetime.strptime(end_time_str, '%Y-%m-%d %H:%M')

        if (start_time_obj - end_time_obj).total_seconds() > 0:
            print("종료시간이 시작시간보다 앞설 수 없습니다.")
            continue
        break
    return start_time_obj, end_time_obj


def calc_fee(row_park, start_time, end_time):
    base_time = int(row_park[18])
    base_fee = int(row_park[19])
    additional_time = int(row_park[20])
    additional_fee = int(row_park[21])
    return calc_fee1(base_time, base_fee, additional_time, additional_fee, start_time, end_time)


def calc_fee1(base_time, base_fee, additional_time, additional_fee, start_time, end_time):
    usage_minutes_total = int((end_time - start_time).total_seconds() / 60)  # minute
    fee = base_fee
    usage_minutes_additional = usage_minutes_total - base_time
    if usage_minutes_additional > 0:
        if additional_time == 0:
            return fee
    else:
        fee += int(usage_minutes_additional / additional_time) * additional_fee
        if usage_minutes_additional % additional_time > 0:
            fee += additional_fee
    return fee



def print_reservation(user_id):
    print("{0} 님의 예약목록 : ".format(credential_id))
    cur.execute("select * from 예약 natural join 전국주차장표준데이터 where 사용자ID=?", (credential_id,))
    rows = cur.fetchall()

    i = 0
    for row in rows:
        print("{0}. 예약번호:{1}, 주차장명:{2}, {3} ~ {4}".format(i + 1, row[0], row[6],
                                                          datetime.datetime.fromtimestamp(row[3]).strftime('%Y-%m-%d %H:%M'),
                                                          datetime.datetime.fromtimestamp(row[4]).strftime('%Y-%m-%d %H:%M')))
        i += 1
    return rows


while True:
    menu = input('''
메뉴를 선택하세요
1. 로그인
2. 회원가입
3. 종료
''')

    if menu =='1':
        #signin
        credential_id = input("아이디를 입력하세요 : ")
        credential_password = input("비밀번호를 입력하세요 : ")
        cur.execute("select * from 사용자 where 사용자ID = ? and 비밀번호 = ?", (credential_id, credential_password))
        row = cur.fetchone()
        if row is None:
            print("그러한 계정이 없거나 비밀번호가 틀렸습니다.")
            continue

    elif menu == '2':
        #signup
        credential_id = input("사용할 아이디를 입력하세요 : ")
        cur.execute("select * from 사용자 where 사용자ID = ?", (credential_id,))
        if cur.fetchone() is not None:
            print("이미 사용중인 아이디입니다.")
            continue

        credential_password = input("사용할 비밀번호를 입력하세요 : ")
        #TODO hash
        cur.execute("insert into 사용자 values (?,?, null)", (credential_id, credential_password))
        conn.commit()
        print("회원가입이 완료되었습니다.")
        continue
    else:
        break

    while True:
        menu = input('''
메뉴를 선택하세요
1. 주차장검색
2. 예약하기
3. 예약확인
4. 예약연장
5. 예약취소
6. 종료
''')

        if menu == '1':
            menu = input('''
1. 이름검색
2. 지역검색
3. 종료
''')

            if menu == '1':
                target = input("검색할 주차장이름을 입력해주세요 : ")
                target = '%'+target+'%'
                cur.execute("select * from 전국주차장표준데이터 where 주차장명 like ?", (target,))
                rows = cur.fetchall()
                print("해당 검색어가 포함된 주차장 목록입니다.")
                for row in rows:
                    printlot(row)
            elif menu == '2':
                target = input("검색할 지역을 선택해주세요\n1. 서울\n2. 경기도\n3. 부산\n : ")
                if target == '1':
                     print("해당 지역에 위치한 주차장 목록입니다.")
                     cur.execute("select * from seoul group by 주차기본요금, 추가단위요금")
                     rows = cur.fetchall()
                     for row in rows:
                        printview(row)
                if target == '2':
                    print("해당 지역에 위치한 주차장 목록입니다.")
                    cur.execute("select * from kyoungki group by 주차기본요금, 추가단위요금")
                    rows = cur.fetchall()
                    for row in rows:
                        printview(row)
                if target == '3':
                    print("해당 지역에 위치한 주차장 목록입니다.")
                    cur.execute("select * from busan group by 주차기본요금, 추가단위요금")
                    rows = cur.fetchall()
                    for row in rows:
                        printview(row)
            elif menu == '3':
                pass

        #예약하기
        elif menu == '2':
            start_time_obj, end_time_obj = usingtime()
            name = input("주차장명을 입력해주세요 : ")
            cur.execute('select * from 전국주차장표준데이터 where 주차장명 = ?', (name,))
            target = cur.fetchone()
            if target is None:
                print("해당 이름의 주차장이 존재하지 않습니다.")
                continue

            if freeslot(target[0], start_time_obj, end_time_obj) <= 0:
                print("남은 자리가 없어 예약할 수 없습니다.")
                continue

            fee = calc_fee(target, start_time_obj, end_time_obj)

            if input("결제 요금은 {0}원입니다. 예약하시겠습니까? (Y/N)".format(fee)) != 'Y':
                continue

            cur.execute('insert into 예약 values (?,?,?,?,?,?)', (int(datetime.datetime.now().timestamp()), credential_id, target[0], int(start_time_obj.timestamp()), int(end_time_obj.timestamp()), fee))
            conn.commit()
            print("예약이 완료되었습니다.")
        #예약확인
        elif menu == '3':
            cur.execute('select * from 예약 where 사용자ID = ?', (credential_id,))
            rows = cur.fetchall()
            if len(rows) <= 0:
                print("예약된 주차장이 없습니다.")
                continue
            rows = print_reservation(credential_id)
        elif menu == '4':
            rows = print_reservation(credential_id)

            number_select = int(input("연장할 예약을 선택하세요 : ")) - 1
            hour, min = input("연장시간 입력(HH:MM) : ").split(':')
            hour = int(hour)
            min = int(min)
            additional_minutes = hour * 60 + min

            original_start_time = datetime.datetime.fromtimestamp(rows[number_select][3])
            original_end_time = datetime.datetime.fromtimestamp(rows[number_select][4])
            new_end_time = datetime.datetime.fromtimestamp(original_end_time.timestamp() + additional_minutes * 60)
            new_fee = calc_fee1(rows[number_select][23], rows[number_select][24], rows[number_select][25], rows[number_select][26], original_start_time, new_end_time)
            original_fee = int(rows[number_select][5])
            if input("추가요금은 {0}원 입니다. 연장하시겠습니까? (Y/N)".format((new_fee-original_fee))) != 'Y':
                continue

            cur.execute("update 예약 set 주차종료시간 = ?, 이용요금 = ? where 예약번호 = ?", (new_end_time.timestamp(), new_fee, rows[number_select][0]))
            conn.commit()
            print("연장이 완료되었습니다.")
        elif menu == '5':
            rows = print_reservation(credential_id)
            a = int(input ("취소할 예약을 선택하세요 : "))
            cur.execute("delete from 예약 where 예약번호=?", (rows[a-1][0],))
            conn.commit()
            #입력받은 번호 = 예약번호인 row delete
            print("예약취소가 완료되었습니다.")

        else:
            conn.close()
            exit(0)

conn.close()
