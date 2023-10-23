from fastapi import FastAPI
from routers.routes import ReportRouter


def create_app():
   app = FastAPI()
   app.include_router(ReportRouter)
   
   return app