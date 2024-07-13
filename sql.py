import sqlite3 as sql

## Connect to sqlite
connection = sql.connect("student.db")

## Create a cursor to perform CRUD operation
cursor = connection.cursor()

## Create table
table = """CREATE TABLE STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25), SECTION VARCHAR(25), MARKS INT);"""

cursor.execute(table)
cursor.execute('''Insert into STUDENT values ('Shubhank','Computer Science','A','90')''')
cursor.execute('''Insert into STUDENT values ('Vinita','Computer Science','B','88')''')
cursor.execute('''Insert into STUDENT values ('Kunal','Maths','A','81')''')
cursor.execute('''Insert into STUDENT values ('Kavya','Maths','B','78')''')

## Display all the records
print("The inserted records are")

data = cursor.execute('''SELECT * from STUDENT''')

for row in data:
    print(row)

## Close the connection
connection.commit()
connection.close()
