import csv
from pathlib import Path
from app.services.Database_Manager import DatabaseManager


def TransferCSV():
    DB_PATH: str = str(Path("DATA") / "intelligence_platform.db")
    dbMgr = DatabaseManager(DB_PATH)
    with open(Path("DATA/it_tickets.csv")) as itFile:
        reader = csv.reader(itFile)
        header: bool = True
        for row in reader:
            if header == False:
                header = False
                continue
            dbMgr.Exec("INSERT INTO It_Tickets (ticket_id, subject, priority, status, created_date) VALUES (?, ?, ?, ?, ?)", (row[0], row[1], row[2], row[3], row[4]))
        
    dbMgr.Close()


def GetQuerySimple(filter, column) -> str:
    if filter:
        return f"SELECT {column} FROM IT_Tickets WHERE {filter}"
    else:
        return f"SELECT {column} from IT_Tickets"


def GetQueryGroup(filter, column) -> str:
    if filter:
        return f"SELECT {column}, Count(*) FROM IT_Tickets GROUP BY {column} HAVING {filter}"
    else:
        return f"SELECT {column}, Count(*) from IT_Tickets GROUP BY {column}"


def GetFilterTickets(filter: str, col: str):
    DB_PATH: str = str(Path("DATA") / "intelligence_platform.db")
    dbMgr = DatabaseManager(DB_PATH)
    query = GetQueryGroup(filter, col)
    print(f"{query=}")
    return dbMgr.FetchAll(query)


def GetTable(filter: str):
    DB_PATH: str = str(Path("DATA") / "intelligence_platform.db")
    dbMgr = DatabaseManager(DB_PATH)
    df = dbMgr.FetchAll(GetQuerySimple(filter, "*"))
        
    return df
    

def InsertTicket(tID: str, sub: str, prio: str, status: str, crDate: str) -> None:
    DB_PATH: str = str(Path("DATA") / "intelligence_platform.db")
    dbMgr = DatabaseManager(DB_PATH)
    dbMgr.Exec("""INSERT INTO It_Tickets (ticket_id, subject, priority, status, created_date) 
                      VALUES (?, ?, ?, ?, ?)""", (tID, sub, prio, status, crDate))
    

def UpdateTicket(id: str, newId: str, newSub: str, newPrio: str, newStat :str, newDate: str):
    DB_PATH: str = str(Path("DATA") / "intelligence_platform.db")
    dbMgr = DatabaseManager(DB_PATH)
    dbMgr.Exec("""UPDATE IT_Tickets
                  SET ticket_id = ?, subject = ?, priority = ?, status = ?, created_date = ?
                  WHERE ticket_id = ?""", (newId, newSub, newPrio, newStat, newDate, id))


def Metrics() -> tuple:
    DB_PATH: str = str(Path("DATA") / "intelligence_platform.db")
    dbMgr = DatabaseManager(DB_PATH)
    queryScript = [
                      "SELECT subject, Count(*) FROM IT_Tickets GROUP BY subject ORDER BY subject desc",
                      "SELECT subject, Count(*) FROM IT_Tickets GROUP BY subject ORDER BY subject asc",
                      "SELECT priority, Count(*) FROM IT_Tickets GROUP BY priority ORDER BY priority desc",
                      "SELECT priority, Count(*) FROM IT_Tickets GROUP BY priority ORDER BY priority asc",
                      "SELECT status, Count(*) FROM IT_Tickets GROUP BY status ORDER BY status desc",
                      "SELECT status, Count(*) FROM IT_Tickets GROUP BY status ORDER BY status asc"]

    maxSub, minSub, maxPrio, minPrio, maxStat, minStat = dbMgr.FetchScript(queryScript)
    return maxSub, minSub, maxPrio, minPrio, maxStat, minStat


def DeleteTicket(id: str):
    DB_PATH: str = str(Path("DATA") / "intelligence_platform.db")
    dbMgr = DatabaseManager(DB_PATH)
    dbMgr.Exec("DELETE FROM It_Tickets WHERE ticket_id = ?", (id, ))