from fastapi import APIRouter
from fastapi.responses import FileResponse
import multiprocessing
import decimal, datetime

from config.db import connection
from models.index import report_table, StatusEnum
from services.generate_report import generate_report


report_router = APIRouter()


@report_router.get("/get_report")
async def get_report(report_id):
    query = report_table.select().where(report_table.c.id == int(report_id))
    report = connection.execute(query).mappings().first()

    if report == None:
        return "Invalid Report Id"

    if report.status == StatusEnum.running:
        return "Running"

    file_path = "./reports/" + report.file_name

    response = FileResponse(file_path, media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={report.file_name}"

    return response


@report_router.post("/trigger_report")
async def trigger_report():
    timestamp = datetime.datetime.now().timestamp()
    file_name = f"{timestamp}.csv"

    multiprocessing.Process(target=generate_report, args=(file_name,)).start()

    query = report_table.insert().values(
        status=StatusEnum.running, file_name=file_name
    )
    response = connection.execute(query)
    connection.commit()

    return response.inserted_primary_key[0]
