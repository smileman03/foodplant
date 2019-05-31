#!/usr/bin/python
# -*- coding: utf-8
import MySQLdb
import string

# соединяемся с базой данных
db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="kormoceh4", charset='utf8')
# формируем курсор
cursor = db.cursor()

# запрос к БД
sql = """SELECT * FROM bunker"""
# выполняем запрос
cursor.execute(sql)
# получаем результат выполнения запроса
data =  cursor.fetchall()
# перебираем записи
for row in data:
    # выводим информацию
    print  (row[0])
    print  (row[1])
# закрываем соединение с БД
db.close()