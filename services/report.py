import threading
from fastapi import Depends
from models.ReportModel import Report
from .service import generate_report
from sqlalchemy.orm import Session
from repository.ReportRepository import ReportRepository
import constants


class ReportService:
  reportRepository: ReportRepository

  def __init__(
        self, reportRepository: ReportRepository = Depends()
    ) -> None:
        self.reportRepository = reportRepository

  def create_report(self, db:Session,  report_id: str):
    report = Report(report_id=report_id, status=constants.RUNNING, path='')
    self.reportRepository.create_report(db, report)

    #separate thread to perform report generation
    thread = threading.Thread(target=generate_report, args=(db, report_id))
    thread.start()
   
  def get_report(self, db: Session, report_id: str) -> Report: 
     return self.reportRepository.get_report(
        db, report_id
     )