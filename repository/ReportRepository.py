from sqlalchemy.orm import Session
from models.ReportModel import Report, Store

class ReportRepository:
      
    def create_report(self, db: Session, report: Report) -> bool:
        db.add(report)
        db.commit()
        return True
    
    def get_all_stores(self):
        return self.db.get(
            Store,
        )
    
    def update_report(self, db : Session, report: Report) -> bool:
          db.merge(report)
          db.commit()
    
    def get_report(self, db: Session, report_id) -> Report:
        return db.query(Report).filter(Report.report_id == report_id).first() 