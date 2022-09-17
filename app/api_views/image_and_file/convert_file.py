import json

import time
from app.utils.convert_file_utils.convert_file import remove_file
from configs.logger import logger
from starlette.responses import JSONResponse
from configs.settings import app
    
from fastapi.encoders import jsonable_encoder
from fastapi import UploadFile, File, BackgroundTasks, Body, Query
from fastapi.responses import FileResponse
from models.request.question import DATA_Export

@app.post("/export_word")
async def export_word(
    background_tasks: BackgroundTasks,
    data: DATA_Export,
    # file: UploadFile = File(...,description="file as UploadFile"),
):
    
    from htmldocx import HtmlToDocx
    import uuid    
    file_name = uuid.uuid4().hex

    import pypandoc
    pypandoc.convert_text(data.content, 'docx', format='html', outputfile=f'file_export/{file_name}.docx')
    # new_parser = HtmlToDocx()
    # # new_parser.parse_html_file('Questions.html', 'out')
    # # file.file.read()
    # docx = new_parser.parse_html_string(data.content)
    # docx.save(f'file_export/{file_name}.docx')
    some_file_path = f'file_export/{file_name}.docx'
    background_tasks.add_task(remove_file, some_file_path)
    return FileResponse(some_file_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename='q.docx')



@app.post("/export_pdf")
async def export_pdf(
    background_tasks: BackgroundTasks,
    data: DATA_Export,
    # content: str = Query(...,description="file as UploadFile"),
    # file: UploadFile = File(...,description="file as UploadFile"),
):
    import pdfkit
    import uuid    
    file_name = uuid.uuid4().hex

    pdfkit.from_string(data.content, f'file_export/{file_name}.pdf')
    some_file_path = f'file_export/{file_name}.pdf'
    background_tasks.add_task(remove_file, some_file_path)
    return FileResponse(some_file_path, media_type='application/pdf', filename='p.pdf')

