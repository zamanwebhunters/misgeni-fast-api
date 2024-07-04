from supabase_client import *
from machine import get_attendance_data
from prepare_attendance import prepare_attendance_to_db
from datetime import datetime
from fastapi import FastAPI, HTTPException
import logging
import json

def fetch_org_info_from_db():
    try:
        client = get_supabase_client_for_operation_portal()
        response = (
            client.table("attendance_machine_configuration")
            .select("*")
            .execute()
        )
        if response.data:
           return data_from_db(response.data)
        else:
            return {
              'from': 'supabase client',
              'error' : response 
            }
                
    except Exception as e:
        logging.error(f"Error fetching organization info from DB: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching organization info from DB")

def data_from_db(org_data: list):
    detailed_res = []
    attendance_details_to_insert =[]
    for org_info in org_data:
        if(org_info['machine_status']):
             
            if not org_info['last_time_update']:
               start_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
               
               start_time_str = datetime.strptime(org_info['last_time_update'], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            try:
                start_time_str =  start_time_str
                end_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                organization_id = org_info['organization_id']
                ip = org_info['ip']
                port = int(org_info['port'])
                status_codes = org_info['status_codes']
                employee_details = org_info['employee_id']
                temp_res="Organization data destructuring"
               
                attendance_data = get_attendance_data(ip, port, start_time_str, end_time_str, status_codes)
                if attendance_data:
                    cleaned_machine_data = cleaning_machine_data_for_db(attendance_data, organization_id ,employee_details)
                    attendance_details_to_insert.append({
                         "org_id": organization_id, 
                         "temp_res": cleaned_machine_data
                    })
                else:
                    temp_res = f"No data to insert for {str(organization_id)} from machine"
                    detailed_res.append({
                    'org_id': organization_id,
                    'temp_res' : temp_res
                    })   

           
            except Exception as e:
                logging.error(f"Error processing organization{str(e)}")
    if(len(attendance_details_to_insert) > 0):
       supabase_insertion_res= call_handle_attendance(attendance_details_to_insert) 
       detailed_res.append({
           "supabase_insertion_res": supabase_insertion_res
           })
     
    else:
        detailed_res.append({
           "supabase_insertion_res":  "nothing to insert"
           })
    return detailed_res


def cleaning_machine_data_for_db(attendance_data: list, organization_id: str, employee_details :list):
    try:
        if attendance_data:
            attendance_details = prepare_attendance_to_db(attendance_data, employee_details)
            if len(attendance_details) > 0:
                return attendance_details
            else:
                return "No Event to insert after Prepare Attendance"    
    except Exception as e:
        logging.error(f"Error inserting attendance data for organization {organization_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error inserting attendance data for organization {organization_id}")


def call_handle_attendance(json_input):
    try:
        
        client = get_supabase_public_client()
        response = client.rpc("handle_attendance", {"json_input": json_input}).execute()
        return {
                'from': 'supabase client insertion',
                'data': response
        }
    except Exception as e:
        logging.error(f"Error calling handle_attendance function: {str(e)}")
        raise HTTPException(status_code=500, detail="Error calling handle_attendance function")


