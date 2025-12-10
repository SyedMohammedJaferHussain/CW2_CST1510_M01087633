class SecurityIncident:
    def __init__(self, id: int, date: str, incidentType: str, severity: str, status: str):
        self.__id = id
        self.__date = date
        self.__incidentType = incidentType
        self.__severity = severity
        self.__status = status
        
    def GetID(self):
        return self.__id
    
    def GetDate(self):
        return self.__date
    
    def GetIncident(self):
        return self.__incidentType
    
    def GetSeverity(self):
        return self.__severity
    
    def GetStatus(self):
        return self.__status

    def GetSevLevel(self):
        match self.GetSeverity():
            case "low":
                return 4
            case "medium":
                return 3
            case "high":
                return 2
            case "critical":
                return 1
    
    def __str__(self):
        return f"ID: {self.__id}, Incident: {self.__incidentType}, Severity: {self.__severity}, Status: {self.__status}, Date: {self.__date}"