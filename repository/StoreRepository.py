from datetime import timedelta
from sqlalchemy.orm import Session
from sqlalchemy import exists, and_ , or_
from models.ReportModel import Store, StoreTimezone, BusinessHours


class StoreRepository:
    
    def get_all_stores(self, db : Session):
       return db.query(StoreTimezone).all()
    
    
    def get_store_hour_logs(self, db: Session, store_id,time_utc) :
        return db.query(Store).filter(Store.timestamp>=time_utc - timedelta(hours=1), Store.store_id == store_id).order_by(Store.timestamp).all()  
        
    def get_store_day_logs(self, db: Session, store_id, time_utc) :
        return db.query(Store).filter(and_(Store.timestamp>=time_utc - timedelta(days=1), Store.timestamp<=time_utc, Store.store_id == store_id)).order_by(Store.timestamp).all()
        
    def get_store_hour_status(self, db : Session, store_id, current_day : int, current_time):
        newrep=db.query(exists().where(
                                and_(
                                    BusinessHours.store_id == store_id, 
                                    BusinessHours.day == current_day,
                                    BusinessHours.start_time_local <= current_time,
                                    BusinessHours.end_time_local >= current_time
                                )
                            )).scalar()
        if newrep : 
            return True
        return False
    
    def get_store_business_hour(self, db : Session, store_id, current_day : int, current_time):
        return db.query(BusinessHours).filter(
                                and_(
                                    BusinessHours.store_id == store_id, 
                                    BusinessHours.day == current_day,
                                    BusinessHours.start_time_local <= current_time,
                                    BusinessHours.end_time_local >= current_time
                                )
                            ).first()


    def get_store_day_status(self, db : Session, store_id, previous_day : int, current_day, current_time):
        return db.query(exists().where(and_(BusinessHours.store_id==store_id,
                                                 or_(
                                                       and_(BusinessHours.day == previous_day, BusinessHours.end_time_local >= current_time),
                                                       and_(BusinessHours.day == current_day, BusinessHours.start_time_local <= current_time))
                                              ))).scalar()
        

    def get_store_week_status(self, db : Session, store_id, previous_week_day : int, current_day, current_time):
       return db.query(exists().where(and_(BusinessHours.store_id==store_id,
                                                 or_(
                                                       and_(BusinessHours.day == previous_week_day, BusinessHours.end_time_local >= current_time),
                                                       and_(BusinessHours.day == current_day, BusinessHours.start_time_local <= current_time))
                                              ))).scalar()

    def check_business_hours(self, db, log : Store) : 
        newrep = db.query(exists().where(
                                  and_(
                                      BusinessHours.store_id == log.store_id,
                                      BusinessHours.day == log.timestamp.weekday(),
                                      BusinessHours.start_time_local <= log.timestamp.time(),
                                      BusinessHours.end_time_local >= log.timestamp.time()
                                  )
                              )).scalar()
        if newrep : 
             return True
        return False
    
    def get_store_week_logs(self, db: Session, store_id, time_utc) :
        return db.query(Store).filter(Store.timestamp>=time_utc - timedelta(days=7),Store.timestamp<=time_utc, Store.store_id == store_id).order_by(Store.timestamp).all()
        