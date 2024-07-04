from supabase_client import *
from fastapi import FastAPI, HTTPException
from datetime import datetime
import logging

def prepare_attendance_to_db(attendance_array: list, employee_details:list):
    try:
        prepared_records = []
        for item in attendance_array:
            timestamp_dt = datetime.strptime(item['timestamp'], '%Y-%m-%d %H:%M:%S')
            date_str = timestamp_dt.date().isoformat()
            employe_id , company_id , branch_id = get_employee_id(item['user_id'], employee_details)
            if(employe_id):
                record = {
                    "branch_id": branch_id,
                    "company_id": company_id,
                    "employee_id": employe_id,
                    "user_name" :  item['user_name'],
                    "event_type": item['event_type'],
                    "date": date_str,
                    "event_time":item['timestamp'],
                }
                prepared_records.append(record)

        print("prepared_records", prepared_records)
        if len(prepared_records) > 0: 
            preapared_attendance_data=[]
            check_in_details , check_out_details , break_in_details , break_out_details , Unknown_events = filter_events_by_type(prepared_records)
            if len(check_in_details) > 0:
                preapared_attendance_data.append({ 'event_type' : 'check-in', 'details': check_in_details}) 
            if len(check_out_details) > 0:
                preapared_attendance_data.append({ 'event_type' : 'check-out', 'details': check_out_details}) 
            if len(break_in_details) > 0:
                preapared_attendance_data.append({ 'event_type' : 'break-in', 'details': break_in_details}) 
            if len(break_out_details) > 0:
                preapared_attendance_data.append({ 'event_type' : 'break-out', 'details': break_out_details})
            if len(Unknown_events) > 0:
                preapared_attendance_data.append({ 'event_type' : 'Unknown_events', 'details': Unknown_events})
            return preapared_attendance_data
        else:
            return "No Data To Insert"
        
    except Exception as e:
        return {"error": str(e)}

 

def get_employee_id(user_id: str, employee_details: list):
    try:
         
        for employee in employee_details:
            if employee['machineUserId'] == user_id:
                employee_id = employee['employee_id']
                company_id = employee.get('company', "")
                branch_id = employee.get('branch', "")
                return employee_id, company_id, branch_id
        return "" ,"", ""
    except Exception as e:
        logging.error(f"Error during get_employee_id: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during get_employee_id")

def filter_events_by_type(prepared_records: list):
    try:
       check_in_events  = []
       check_out_events = []
       break_in_events  = []
       break_out_events = []
       Unknown_events   = []
      
       for record in prepared_records:
           if(record['event_type'] == 'check-in'):
                check_in_events.append(record)
           elif(record['event_type'] == 'break-in'):
               break_in_events.append(record)     
           elif(record['event_type'] == 'break-out'):
               break_out_events.append(record)
           elif(record['event_type'] == 'check-out'):
               check_out_events.append(record)   
           else: 
              Unknown_events.append(record)  

       return check_in_events, check_out_events , break_in_events , break_out_events , Unknown_events

    except Exception as e:
        logging.error(f"Error during filter_events_by_type info from DB details: {str(e)}")
        raise HTTPException(status_code=500, detail="Error during filter_events_by_type info from DB details")