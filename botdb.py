import sqlite3

def setupdb():
    global cur
    global con
    con = sqlite3.connect('../coronastats.db')
    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS `server_settings` (`guild_id` VARCHAR(20),`prefix` VARCHAR(7));")
    con.commit()
    print("Database: Ready")

def closecon():
    con.close()

def getcon():
    return con

def getcur():
    return cur

def execute(query):
    return cur.execute(query)

def select(table, data_vars):
    cur.execute(f"SELECT {data_vars} FROM {table}")
    return cur.fetchall()

def selectwhere(table, data_vars, wheretxt):
    cur.execute(f"SELECT {data_vars} FROM {table} WHERE {wheretxt}")
    return cur.fetchall()


def insert(table, data_args, data_value):
    cur.execute(f"INSERT INTO {table} ({data_args}) VALUES ({data_value})")
    con.commit()

def insertwhere(table, data_args, data_value, wheretxt):
    cur.execute(f"INSERT INTO {table} ({data_args}) VALUES ({data_value}) WHERE {wheretxt}")
    con.commit()

def update(table, datatxt):
    cur.execute(f"UPDATE {table} SET {datatxt}")
    con.commit()

def updatewhere(table, datatxt, wheretxt):
    cur.execute(f"UPDATE {table} SET {datatxt} WHERE {wheretxt}")
    con.commit()

def check(table, datavar):
    cur.execute(f"SELECT {datavar} FROM {table} LIMIT 1")
    if cur.fetchall() == []:
        return False
    else:
        return True

def checkwhere(table, datavar, wheretxt):
    cur.execute(f"SELECT 1 FROM {table} WHERE {wheretxt}")
    if cur.fetchall() == []:
        return False
    else:
        return True