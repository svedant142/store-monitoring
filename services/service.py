from datetime import datetime
from models.ReportModel import Report
import os
import csv
from pytz import timezone as pytz_timezone
from repository.ReportRepository import ReportRepository
from repository.StoreRepository import StoreRepository
from sqlalchemy.orm import Session
import constants


def generate_report(db: Session, report_id: str) :
    report = ReportRepository().get_report(db, report_id)
    report_data = []
    store_repo = StoreRepository()
    stores = store_repo.get_all_stores(db)
    for store in stores : 
        #hard coded current time as max and calculating time based on timezones
        current_time = datetime.now()  
        zone_utc = pytz_timezone('UTC')
        time_utc = current_time.astimezone(zone_utc) 
        zone_tz = store.timezone_str or 'America/Chicago'
        zone_target = pytz_timezone(zone_tz)
        time_local = current_time.astimezone(zone_target)
        current_day = time_local.weekday()
        current_time = time_local.time()
        #separately computing last hour, day and week uptime, downtime
        hour_status= calculate_last_hour(db, store.store_id, time_utc, current_day, current_time, store_repo)
        day_status = calculate_last_day(db, store.store_id, time_utc, current_day, current_time,store_repo)
        week_status = calculate_last_week(db, store.store_id,time_utc, current_day, current_time,store_repo)
        row = []
        #adding rows for the csv file
        row.append(store.store_id)
        row.extend([hour_status["uptime"], day_status["uptime"], week_status["uptime"]])
        row.extend([hour_status["downtime"],day_status["downtime"],week_status["downtime"]])
        report_data.append(row)

    store_report(db, report, report_data)

def calculate_last_hour(db, store_id, time_utc, current_day, current_time, store_repo: StoreRepository) : 
    hour_status= {"uptime" : 0, "downtime" : 0}
    # gets business hours if store is open in the last hour
    business_hours = store_repo.get_store_business_hour(db, store_id, current_day, current_time)
    if business_hours is None:
        return hour_status
    #fetching the logs with current time - one hour
    last_hour_logs = store_repo.get_store_hour_logs(db, store_id, time_utc)
    if last_hour_logs:
        last_hour_log_status = last_hour_logs[0].status
        #if the status matches with 'active' uptime is calculated
        #else for 'inactive' case the downtime is calculated
        if last_hour_log_status == constants.ACTIVE:
            log_time = last_hour_logs[0].timestamp.time()                
            # Calculate the time difference in seconds, it helps in calculating up the minutes active in the last hour. It also uses business hours to handle the start_time condition
            # i.e,. when the difference between the log polling and the start_time is less than 60 minutes.
            time_difference_seconds = (log_time.hour * 3600 + log_time.minute * 60 + log_time.second) - business_hours.start_time_local.seconds
            if time_difference_seconds < 3600: 
                 hour_status["uptime"] = int(time_difference_seconds/60)
            else : 
                hour_status["uptime"] = 60
        else:
            #Similar to uptime, downtime is calculated
            log_time = last_hour_logs[0].timestamp.time()                
            time_difference_seconds = (log_time.hour * 3600 + log_time.minute * 60 + log_time.second) - business_hours.start_time_local.seconds
            if time_difference_seconds < 3600 : 
                 hour_status["downtime"] = int(time_difference_seconds/60)
            else : 
                hour_status["downtime"] = 60
    #hour_status is calculated in minutes
    return hour_status

def calculate_last_day(db, store_id, time_utc,  current_day, current_time, store_repo: StoreRepository) : 
    day_status= {"uptime" : 0, "downtime" : 0}
    previous_day = current_day - 1 if current_day > 0 else 6
    #checking availability of the store i.e, if it is open in the last day. 
    # Query in the reposiotory layer H=handles the case when it is available one day, but not available other day too.
    is_store_open = store_repo.get_store_day_status(db, store_id, previous_day, current_day, current_time)
    if not is_store_open:
        return day_status
    #fetching the logs(i.e, polling api timestamps, status) with current time - one day
    last_day_logs = store_repo.get_store_day_logs(db, store_id, time_utc)
    for log in last_day_logs :  
        #considering logs within the business hours of the store only.
        log_business_hours = store_repo.check_business_hours(db, log)
        if not log_business_hours:
            continue
        if log.status == constants.ACTIVE:
            day_status["uptime"] += 1
        else:
            day_status["downtime"]  += 1
    #day_status returned in hours
    return day_status

def calculate_last_week(db, store_id, time_utc, current_day, current_time, store_repo: StoreRepository) : 
    week_status= {"uptime" : 0, "downtime" : 0}
    previous_week_day = current_day - 7 if current_day > 0 else 0
    #checking availability of the store i.e, if it is open in the last week. 
    is_store_open = store_repo.get_store_week_status(db,store_id, previous_week_day, current_day, current_time)
    if not is_store_open:
        return week_status
    #fetching the logs(i.e, polling api timestamps, status) with current time - one week
    last_week_logs = store_repo.get_store_week_logs(db, store_id,time_utc)
    for log in last_week_logs :  
        #considering logs within the business hours of the store only.
        log_business_hours = store_repo.check_business_hours(db, log)
        if not log_business_hours:
            continue
        if log.status == constants.ACTIVE:
            week_status["uptime"] += 1
        else:
            week_status["downtime"] += 1
     #week_status returned in hours
    return week_status



def store_report(db: Session, report: Report, report_data) :
        #defining the storage path(here used local storage path, can be cloud path to support cloud storage like AWS S3).
        file_name = f"{report.report_id}.csv"
        temp_file_path = os.path.join("E:\\", file_name)
        with open(temp_file_path, "w", newline='') as csv_file:
            #writing rows in the csv file
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["store_id","uptime_last_hour",
                                 "uptime_last_day","uptime_last_week",
                                 "downtime_last_hour","downtime_last_day",
                                 "downtime_last_week"])
            for data in report_data:
                csv_writer.writerow(data)
        report.path=temp_file_path
        report.status = constants.COMPLETE
        report.completed_at = datetime.utcnow()
        #updating the path, status, completed_at of the record in the report table.
        ReportRepository().update_report(db, report)
