import csv
from pathlib import Path
import app.data.db as db
import pandas as pd


def TransferCSV():
    conn = db.connect_database()
    cursor = conn.cursor()
    with open(Path("DATA/it_tickets.csv")) as itFile:
        reader = csv.reader(itFile)
        header: bool = True
        for row in reader:
            if header == False:
                header = False
                continue
            cursor.execute("INSERT INTO It_Tickets (ticket_id, subject, priority, status, created_date) VALUES (?, ?, ?, ?, ?)", (row[0], row[1], row[2], row[3], row[4]))
        
    conn.commit()
    conn.close()
    

def GetQuery(filter) -> str:
    if filter:
        return f"SELECT subject FROM IT_Tickets WHERE {filter}"
    else:
        return "SELECT subject from IT_Tickets"


def GetAllTickets(filter):
    conn = db.connect_database()
    df = pd.read_sql_query(GetQuery(filter), conn)
    conn.close()
    
    return df


def TotalTickets(filter: str) -> int:
    conn = db.connect_database()
    query = GetQuery(filter)
    totalInc = pd.read_sql_query(query, conn)
    
    return len(totalInc)


def InsertTicket(tID: str, sub: str, prio: str, status: str, crDate: str):
    conn = db.connect_database()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO It_Tickets (ticket_id, subject, priority, status, created_date) 
                      VALUES (?, ?, ?, ?, ?)""", (tID, sub, prio, status, crDate))
    conn.commit()
    conn.close()
    

def UpdateTicket(id: str, newId: str, newSub: str, newPrio: str, newStat :str, newDate: str):
    conn = db.connect_database()
    cursor = conn.cursor()
    cursor.execute(f"""UPDATE IT_Tickets
                    SET ticket_id = ?, subject = ?, priority = ?, status = ?, created_date = ?
                    WHERE ticket_id = ?""", (newId, newSub, newPrio, newStat, newDate, id))
    cursor.execute("SELECT * FROM IT_Tickets ORDER BY id desc")
    print(cursor.fetchone())
    conn.commit()
    conn.close()


def DeleteTicket(id: str):
    conn = db.connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM It_Tickets WHERE ticket_id = ?", (id, ))
    cursor.execute("SELECT * FROM IT_Tickets WHERE ticket_id = '36'")
    print(cursor.fetchone())
    conn.commit()
    conn.close()