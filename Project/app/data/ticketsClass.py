from app.services.Database_Manager import DatabaseManager
from models.it_ticket import ITTicket
from pathlib import Path
from Home import tickets
from typing import Any
import pandas as pd


def TransferFromDB():
    dbMgr = DatabaseManager(str(Path("DATA") / "intelligence_platform.db"))
    df = dbMgr.FetchAll("SELECT ? FROM IT_Tickets", ("*", ))
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


def CheckFilters(filters: dict[str, function], ticket: ITTicket):
    """
        filters Example: {"ticket_id": lambda x: x < 100 and x > 20} which checks if ticket_id between 20 and 100
    """
    check: bool = True
    for column, func in filters:
        if not func(GetColumn(column, ticket)): #type: ignore
            check = False
            break
            
    return check


def AddCnt(hash: dict, value: Any):
    if value in hash:
        hash[column] += 1 #type: ignore
    else:
        hash[column] = 0 #type: ignore


def GetRows(filters: dict[str, function]) -> pd.DataFrame:
    """
        Takes filters and column name returns all rows fulfilling filters
    """
    allRows: list = []
    for ticket in tickets:
        if CheckFilters(filters, ticket):
            allRows.append(GetColumn("*", ticket))
    
    df: pd.DataFrame = pd.DataFrame(allRows, columns = ["ticket_id", "subject", "priority", "status", "created_date"])
    return df


def GetColCount(filters: dict[str, function], col: str):
    """
        Takes filters and column name, returns each distinct column along with number of occurances
        Mimics GROUP BY HAVING
    """
    subjects: dict[str, int] = dict() #Dict of form subjectName : count
    priorities: dict[str, int] = dict()
    statusS: dict[str, int] = dict()
    dates: dict[str, int] = dict()
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
    
    return pd.DataFrame(dfToReturn)
    
    
def GetFilterTickets(filter: dict[str, function], col: str):
    return GetColCount(filter, col)


def GetTable(filter: dict[str, function]):
    return GetRows(filter)
    

def InsertTicket(tID: int, sub: str, prio: str, status: str, crDate: str) -> None:
    tickets.append(ITTicket(tID, sub, prio, status, crDate))


def GetIndex(lst: list[ITTicket], target: Any) -> int:
    low: int = 0
    high: int = len(lst) - 1
    while low <= high:
        mid: int = low + (high - low) // 2
        if lst[mid].GetID() == target:
            return mid
        elif lst[mid].GetID() < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


def UpdateTicket(id: int, newId: int, newSub: str, newPrio: str, newStat :str, newDate: str):
    index: int = GetIndex(tickets, id)
    tickets[index] = ITTicket(newId, newSub, newPrio, newStat, newDate)


def DeleteTicket(id: str):
    index: int = GetIndex(tickets, id)
    tickets.remove(tickets[index])


def IncCount(column: str, dictionary: dict):
    if column in dictionary:
        dictionary["Count"] += 1 #type: ignore
    else:
        dictionary["Count"] = 0 #type: ignore


def GetMaxMin(dictionary: dict[str, dict[str, int]]) -> tuple[int, int]: 
    max = min = 0 #class = int
    for sub in dictionary:
        count: int = dictionary[sub]["Count"]
        if count > max:
            max = count
        elif count < min:
            min = count
            
    return max, min

def Metrics(filters: dict[str, function]):
    subjects: dict[str, dict[str, int]] = dict() #Dict of form subjectName : dict["Count": 0]
    priorities: dict[str, dict[str, int]]  = dict()
    statusS: dict[str, dict[str, int]]  = dict()

    for i in range(len(tickets)):
        ticket = tickets[i]
        if not CheckFilters(filters, ticket):
            continue
        
        subject: str = ticket.GetSub()
        priority: str = ticket.GetPrio()
        status: str = ticket.GetStatus()
        IncCount(subject, subjects) #type: ignore
        IncCount(priority, priorities) #type: ignore
        IncCount(status, statusS) #type: ignore
    
    maxSub, minSub = GetMaxMin(subjects)
    maxPrio, minPrio = GetMaxMin(priorities)
    maxStat, minStat = GetMaxMin(statusS)

    return {"Subjects": (maxSub, minSub), "Priority": (maxPrio, minPrio), "Status": (maxStat, minStat)} #Improve output