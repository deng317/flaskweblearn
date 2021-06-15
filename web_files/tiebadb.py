import pymysql
import bleach
dbname='tieba'

def get_posts():
    db_conn = pymysql.connect(user='root',passwd='DWY0317lj.',host='1.116.63.141',port=3306,db=dbname)
    cursor=db_conn.cursor()
    cursor.execute('SELECT time,content,title,username FROM tbtieba ORDER BY time DESC')
    posts=cursor.fetchall()
    db_conn.close()
    return posts

def add_post(post_time,title,content,username):
    db_conn = pymysql.connect(user='root',passwd='DWY0317lj.',host='1.116.63.141',port=3306,db=dbname)
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO tbtieba (time,title,content,username) VALUE(\'{}\',\'{}\',\'{}\',\'{}\')".format(post_time,bleach.clean(title),bleach.clean(content),username))
    db_conn.commit()
    db_conn.close()

def delete_post(time,title):
    db_conn = pymysql.connect(user='root',passwd='DWY0317lj.',host='1.116.63.141',port=3306,db=dbname)
    cursor = db_conn.cursor()
    cursor.execute(f"DELETE FROM tbtieba WHERE time = \'{time}\' AND title = \'{title}\'")
    db_conn.commit()
    db_conn.close()

def save_user_info(username,email,password):
    db_conn = pymysql.connect(user='root',passwd='DWY0317lj.',host='1.116.63.141',port=3306,db=dbname)
    cursor = db_conn.cursor()
    cursor.execute(f"INSERT INTO user_info (user_name,email,password) VALUE(\'{username}\',\'{email}\',\'{password}\')")
    db_conn.commit()
    db_conn.close()

def read_password(email):
    db_conn = pymysql.connect(user='root',passwd='DWY0317lj.',host='1.116.63.141',port=3306,db=dbname)
    cursor = db_conn.cursor()
    cursor.execute(f"SELECT password FROM user_info WHERE email = \'{email}\'")
    password=cursor.fetchall()[-1][0]
    db_conn.close()
    return password