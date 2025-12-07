import streamlit as st
import app.data.tickets as tickets
import plotly.express as exp


def Debug(*args) -> None:
    """
        ONLY USED FOR DEVELOPMENT
        For easy debugging, using f-string formatting. 
    """
    for arg in args:
        print(f"{arg=}")
        
        
def CheckLogIn() -> None: 
    """
        Check if user is in logged in state
        If not display appropriate error and switch to Home page
    """
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    if not st.session_state.logged_in:
        st.error("You must be logged in to view the dashboard.")
        if st.button("Go to login page"):
            st.switch_page("Home.py")   #Back to the home page
        st.stop()
        

def RowColumnCnt():
    """
        Displays number of rows in the bar chart filtered output
    """
    st.divider()
    rowCnt = tickets.TotalTickets(filterQuery)
    st.text(f"Row Count: {rowCnt}")
    

def BarChart(df):
    """_summary_
    Explanation: Creates a bar chart displaying subject column from df
    Args:
        df (_DataFrame_): DataFrame consisting of query output from IT_Tickets Table
    """
    bar = exp.bar(df, x = "subject")
    st.subheader("IT Tickets")
    st.plotly_chart(bar)


def FilterQuery(idStart: str, idStop: str, title: tuple, severity :tuple, status: tuple, dateStart :str, dateStop: str) -> str:
    """_summary_
        Explanation: 
            Checks which filter widgets are filled and creates SQL query based off them
            If multiple checkboxes ticked, creates a tuple and uses IN Operator to filter through all selected
        Args:
            idStart (_str_): Start range of ID
            idStop (_str_): Stop range of ID
            title (_tuple_): Titles to check for
            severity (_tuple_): Severity to check for
            status (_tuple_): Status to check for
            dateStart (_str_): Start range of date
            dateStop (_str_): Stop range of date
    """
    queries: tuple = tuple()
    if idStart and idStop: #Both selected by default
        queries += (f"id BETWEEN {idStart} AND {idStop}", )
    if title:
        if len(title) == 1:
            queries += (f"subject = '{title[0]}'", )
        else:
            queries += (f"subject IN {title}", )  
    if severity:
        if len(severity) == 1:
            queries += (f"priority = '{severity[0]}'", )
        else:
            queries += (f"priority IN {severity}", )
    if status:
        if len(severity) == 1:
            queries += (f"status = '{status[0]}'", )
        else:
            queries += (f"status IN {status}", )
    if dateStart: #Selected as today by default
        queries += (f"created_date BETWEEN '{dateStart}' AND '{dateStop}'", )

    query: str = ""
    noQueries: int = len(queries)
    Debug(queries)
    if len(queries) == 1:
        query = queries[0]
    for i in range(noQueries - 1): #To make sure last query doesn't have "AND" at the end
        query += queries[i] + " AND "
    if len(queries) > 1:
        query += queries[-1]    
    
    global filterQuery
    filterQuery = query
    return query
    

def Filters() -> None:
    """
        Creates widgets for filters which include textboxes, checkboxes, and date inputs
        When apply filters button clicked, pass user input values to FilterQuery()
    """
    with st.sidebar:
        st.title("Filters")
        
        with st.expander("**ID**"):
            idStart: str = str(st.text_input("Start Value"))
            idStop: str = str(st.text_input("Stop Value"))
            
        with st.expander("**Subject**"):
            titleFil: tuple = tuple(st.multiselect("Subject", ("Printer not working", "Password reset request", "VPN connection issue", "Network outage", "Access request", "Software installation needed", "Malware alert", "Laptop not booting", "System Crash", "Email not syncing")))

        with st.expander("**Priority**"):
            prioFil: tuple = tuple(st.multiselect("Priority", ("low", "medium", "high", "urgent")))
            
        with st.expander("**Status**"):
            statusFil: tuple = tuple(st.multiselect("Status", ("open", "in progress", "resolved")))
        
        with st.expander("**Date**"):
            dateStart = st.date_input("Start Value", value = "2020-01-01")
            dateStop = st.date_input("Stop Value")
            
        if st.button("Apply Filters"):
            FilterQuery(idStart, idStop, titleFil, prioFil, statusFil, str(dateStart), str(dateStop))
            global filterApply
            filterApply = True
            


def BarCheck() -> None:
    """
        Checks if filter has applied and updates chart everytime button is pressed
        It then calls BarChart() with 
    """
    if filterApply:
        data = tickets.GetAllTickets(filterQuery)
        print(data)
        BarChart(data)
    else:
        data = tickets.GetAllTickets(None)
        print(data)
        BarChart(data)


def PromptTicketInfo() -> tuple:
    """
        Creates text input widgets for id, subject, date, priority, and status
        Returns variables containing user input for each column
    """
    tId: str = st.text_input("Ticket ID")
    subjectType: str = st.selectbox("Incident Type", ("Printer not working", "Password reset request", "VPN connection issue", "Network outage", "Access request", "Software installation needed", "Malware alert", "Laptop not booting", "System Crash", "Email not syncing"))
    date: str = str(st.date_input("Date"))
    priority: str = st.selectbox("Priority", ("low", "medium", "high", "urgent"))
    status: str = st.selectbox("Status", ("open", "resolved", "in progress"))
    return tId, subjectType, date, priority, status


def CUDTicket():
    """
        Contains functions for creating, updating, and deleting tickets
    """
    st.divider()
    st.subheader("CUD Operations")
    cudChoice: str = st.selectbox("Operation", ("Create Ticket", "Update Ticket", "Delete Ticket"))
    
    st.subheader(cudChoice)
    if cudChoice == "Create Ticket":
        tId, subjectType, date, priority, status = PromptTicketInfo()
    else:
        tId: str = st.text_input("Ticket ID") #Only require id for delete and update
    
    if cudChoice == "Update Ticket": #Creating seperate widgets for update ticket since using PromptTicketInfo raises streamlit.errors.StreamlitDuplicateElementId
        st.markdown("**Updated Values**")
        newId: str = st.text_input("Ticket ID ")
        newSub: str = st.selectbox("Incident Type ", ("Printer not working", "Password reset request", "VPN connection issue", "Network outage", "Access request", "Software installation needed", "Malware alert", "Laptop not booting", "System Crash", "Email not syncing"))
        newDate: str = str(st.date_input("Date "))
        newPrio: str = st.selectbox("Priority ", ("low", "medium", "high", "urgent"))
        newStat: str = st.selectbox("Status ", ("open", "resolved", "in progress"))
        
    if st.button(cudChoice):
        #Calling necessary functions for each CUD Operation
        match cudChoice:
            case "Create Ticket":
                tickets.InsertTicket(tId, subjectType, priority, status, date) # type: ignore
                st.success("Ticket Created!")
            case "Update Ticket":
                tickets.UpdateTicket(tId, newId, newSub, newPrio, newStat, newDate)# type: ignore
                st.success("Ticket Updated!")
            case "Delete Ticket":
                tickets.DeleteTicket(tId) # type: ignore
                st.success("Ticket Deleted!")
            
    
def LogOut():
    st.divider()
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.info("You have been logged out.")
        st.switch_page("Home.py")
    
    
if __name__ == "__main__":
    #Global Variables
    filterApply = False 
    filterQuery = ""
    widgetKey: str = ""
    
    #Preliminary Checks for login
    CheckLogIn()
    st.title("IT TICKETS")
    
    #Widgets and UI
    Filters() 
    RowColumnCnt()
    BarCheck()
    CUDTicket()
    LogOut()