from app.services.Database_Manager import DatabaseManager
from models.it_ticket import ITTicket
from pathlib import Path
from typing import Any
import pandas as pd
import pickle
from os import remove


def TransferFromDB():
    dbMgr = DatabaseManager(str(Path("DATA") / "intelligence_platform.db"))
    df = dbMgr.FetchAll("SELECT * FROM IT_Tickets ORDER BY ticket_id")
    itTickets: list[ITTicket] = []
    ids: list[str] = df["ticket_id"].tolist() #Converted to int later
    subs: list[str] = df["subject"].tolist()
    prios: list[str] = df["priority"].tolist()
    stats: list[str] = df["status"].tolist()
    crDates: list[str] = df["created_date"].tolist()
    for i in range(len(df)):
        ticket: ITTicket = ITTicket(int(ids[i]), subs[i], prios[i], stats[i], crDates[i])
        itTickets.append(ticket)
    
    return itTickets


def GetColumn(col: str, ticket: ITTicket):
    match col:
        case "ticket_id":
            return ticket.GetID()
        case "subject":
            return ticket.GetSub()
        case "priority":
            return ticket.GetPrio()
        case "status":
            return ticket.GetStatus()
        case "created_date":
            return ticket.GetCrDate()
        case _: # * = "All"
            return ticket.GetAll()


def CheckFilters(filters: dict | None, ticket: ITTicket):
    """
        filters Example: {"ticket_id": lambda x: x < 100 and x > 20} which checks if ticket_id between 20 and 100
    """
    if not filters:
        return True
    check: bool = True
    for column in filters:
        if not filters[column](GetColumn(column, ticket)): #type: ignore
            check = False
            break
    
    return check


def AddCnt(hash: dict, col: Any):
    if col in hash["column"]:
        index: int = hash["column"].index(col)
        hash["vals"][index] += 1
    else:
        hash["column"].append(col)
        hash["vals"].append(1)


def GetRows(filters: dict) -> pd.DataFrame:
    """
        Takes filters and column name returns all rows fulfilling filters
    """
    tickets: list[ITTicket] = GetTickets()
    allRows: list = []
    for ticket in tickets:
        if CheckFilters(filters, ticket):
            allRows.append(GetColumn("*", ticket))
    
    df: pd.DataFrame = pd.DataFrame(allRows, columns = ["ticket_id", "subject", "priority", "status", "created_date"])
    return df


def GetColCount(filters: dict, col: str):
    """
        Takes filters and column name, returns each distinct column along with number of occurances
        Mimics GROUP BY HAVING
    """
    tickets: list[ITTicket] = GetTickets()
    subjects: dict[str, list[str | int]] = {"column": [], "vals": []} #Dict of form column: ["columns"], vals: [1,2,3]
    priorities: dict[str, list[str | int]] = {"column": [], "vals": []}
    statusS: dict[str, list[str | int]] = {"column": [], "vals": []}
    dates: dict[str, list[str | int]] = {"column": [], "vals": []}
    noTickets: int = len(tickets)
    dfToReturn = {}
    for i in range(noTickets):
        ticket = tickets[i]
        if not CheckFilters(filters, ticket):
            continue
        
        column = GetColumn(col, ticket)
        match col:
            case "subject":
                AddCnt(subjects, column)
            case "priority":
                AddCnt(priorities, column)
            case "status":
                AddCnt(statusS, column)
            case "created_date":
                AddCnt(dates, column)
                
    match col:
        case "subject":
                dfToReturn = subjects
        case "priority":
                dfToReturn = priorities
        case "status":
                dfToReturn = statusS
        case "created_date":
                dfToReturn = dates
    
    df = pd.DataFrame(dfToReturn)
    print("-" * 30, df)
    return df


def GetRowCnt(filter: dict):
    tickets: list[ITTicket] = GetTickets()
    cnt: int = 0
    for ticket in tickets:
        if CheckFilters(filter, ticket):
            cnt += 1
    
    return cnt


def GetIDs(tickets: list[ITTicket]) -> list[int]:
    ids: list[int] = []
    for ticket in tickets:
        ids.append(ticket.GetID())
    return ids


def CheckID(tickets: list[ITTicket], id: int) -> bool:
    return False if id in GetIDs(tickets) else True


def InsertTicket(tID: int, sub: str, prio: str, status: str, crDate: str) -> None | bool:
    tickets: list[ITTicket] = GetTickets()
    ticket: ITTicket = ITTicket(tID, sub, prio, status, crDate)
    if not CheckID(tickets, tID):
        return False
    tickets.append(ticket)
    WriteTickets(tickets)


def GetIndex(lst: list[ITTicket], target: int) -> int:
    low: int = 0
    high: int = len(lst) - 1
    while low <= high:
        mid: int = low + (high - low) // 2
        if lst[mid].GetID() == target:
            return mid
        elif int(lst[mid].GetID()) < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


def UpdateTicket(id: int, newId: int, newSub: str, newPrio: str, newStat :str, newDate: str):
    tickets: list[ITTicket] = GetTickets()
    index: int = GetIndex(tickets, int(id))
    tickets[index] = ITTicket(newId, newSub, newPrio, newStat, newDate)
    WriteTickets(tickets)


def DeleteTicket(id: str):
    tickets: list[ITTicket] = GetTickets()
    index: int = GetIndex(tickets, int(id))
    tickets.remove(tickets[index])
    WriteTickets(tickets)


def IncCount(column: str, dictionary: dict):
    if column in dictionary:
        dictionary[column] += 1 #type: ignore
    else:
        dictionary[column] = 1 #type: ignore


def GetMaxMin(dictionary: dict[str, str | int]) -> None: 
    firstKey: str = list(dictionary.keys())[0]
    dictionary["MaxCol"] = firstKey
    dictionary["MinCol"] = firstKey
    dictionary["MaxVal"] = dictionary[firstKey]
    dictionary["MinVal"] = dictionary[firstKey]
    for col in dictionary:
        if col in ("MaxVal", "MaxCol", "MinVal", "MinCol"):
            break
        count: int = dictionary[col] #type: ignore
        if count > dictionary["MaxVal"]: #type: ignore
            dictionary["MaxVal"] = count
            dictionary["MaxCol"] = col
        elif count < dictionary["MinVal"]: #type: ignore
            dictionary["MinVal"] = count
            dictionary["MinCol"] = col
    

def Metrics():
    """
        Creates 3 dictionaries (subjects, priorities, statusS) of form dict[str, str | int]
        The keys will be columnName/MaxVal/MaxCol/MinVal/MinCol
        The values will be Count/Values containing max and min values/Columns containing max and min values
    """
    tickets: list[ITTicket] = GetTickets()
    
    subjects: dict[str, str | int] = dict() #Dict of form subjectName : dict["Count": 0]
    priorities: dict[str, str | int]  = dict()
    statusS: dict[str, str | int]  = dict()

    for i in range(len(tickets)):
        ticket = tickets[i]
        
        subject: str = ticket.GetSub()
        priority: str = ticket.GetPrio()
        status: str = ticket.GetStatus()
        IncCount(subject, subjects) #type: ignore
        IncCount(priority, priorities) #type: ignore
        IncCount(status, statusS) #type: ignore
    
    GetMaxMin(subjects)
    GetMaxMin(priorities)
    GetMaxMin(statusS)

    return subjects, priorities, statusS


def GetTickets() -> list[ITTicket]:
    with open(Path("DATA") / "tickets.bin", "rb") as ticketsObjs:
        tickets = pickle.load(ticketsObjs) 
    return tickets


def WriteTickets(tickets: list[ITTicket]):
    with open(Path("DATA") / "tickets.bin", "wb") as ticketsObjs:
        pickle.dump(tickets, ticketsObjs)
        

def Commit():
    tickets = GetTickets()
    remove(Path("DATA") / "tickets.bin")
    dbMgr = DatabaseManager(str(Path("DATA") / "intelligence_platform.db"))
    dbMgr.Exec("DELETE FROM IT_Tickets")
    for ticket in tickets:
        dbMgr.Exec("INSERT INTO IT_Tickets (ticket_id, subject, priority, status, created_date) VALUES (?, ?, ?, ?, ?)", (str(ticket.GetID()), ticket.GetSub(), ticket.GetPrio(), ticket.GetStatus(), ticket.GetCrDate()) )
    
    dbMgr.Close()