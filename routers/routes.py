import secrets
from fastapi import APIRouter,  HTTPException, Query, Response, Depends, responses
from services.report import ReportService
from repository.ReportRepository import ReportRepository
from sqlalchemy.orm import Session
import json
import constants
from configs.database import (
    get_db_connection,
)

ReportRouter = APIRouter(
    prefix="/api/report"
)

@ReportRouter.post("/trigger_report", response_model=dict)
def trigger_report(db: Session = Depends(get_db_connection)):
    try:
        report_repository = ReportRepository()
        report_service = ReportService(report_repository)
        report_id = secrets.token_urlsafe(16) 
        report_service.create_report(db ,report_id)
        response_content_json = json.dumps({'report_id':report_id, 'message': 'Success'})
        return Response(status_code=200, content=response_content_json,  media_type='application/json')
    except Exception as e:
        raise HTTPException(status_code=500, detail="something went bad, server error")



@ReportRouter.get("/get_report", response_class=responses.FileResponse, response_model=dict)
def get_report(report_id: str = Query(..., min_length=1),  db: Session = Depends(get_db_connection)): 
    try:
        if not report_id:
            response_content_json = json.dumps({'message':"missing report_id"})
            return Response(status_code=400, content=response_content_json,  media_type='application/json')
        report =  ReportService(ReportRepository()).get_report(db, report_id)
        if not report.status:
            response_content_json = json.dumps({'message':"invalid report_id"})
            return Response(status_code=200, content=response_content_json,  media_type='application/json')
        if report.status == constants.RUNNING:
            response_content_json = json.dumps({'message' : "success", 'status': "Running"})
            return Response(status_code=200, content=response_content_json,  media_type='application/json')
        elif report.status == constants.COMPLETE:
            if report.path:
                try:
                  resp =  responses.FileResponse(report.path, media_type="text/csv")
                  resp.headers["Content-Disposition"] = "attachment; filename=report.csv"
                  return resp
                except FileNotFoundError:
                    return {"error": "File not found"}
            else:
                response_content_json = json.dumps({'message':"unable to retrieve report path"})
                return Response(status_code=200, content=response_content_json,  media_type='application/json')
        else:
            response_content_json = json.dumps({'message':"invalid report status"})
            return Response(status_code=200, content=response_content_json,  media_type='application/json')
    except Exception as e:
        raise HTTPException(status_code=500, detail="something went bad, server error")

