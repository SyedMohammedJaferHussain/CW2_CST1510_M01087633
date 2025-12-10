class ITTicket:
    def __init__(self, id: int, sub: str, prio: str, status: str, createdDate: str) -> None:
        self.__id = id
        self.__sub = sub
        self.__prio = prio
        self.__status = status
        self.__crDate = createdDate
    
    
    def __str__(self):
        return f"ID: {self.__id}, Subject: {self.__sub}, Priority: {self.__prio}, Status: {self.__status}, Created Date: {self.__crDate}"
       
        
    #Get Functions
    def GetID(self):
        return self.__id
    def GetSub(self):
        return self.__sub
    def GetPrio(self):
        return self.__prio
    def GetStatus(self):
        return self.__status
    def GetCrDate(self):
        return self.__crDate