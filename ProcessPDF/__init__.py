import azure.functions as func
import logging
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("ProcessPDF function called")
    
    pdf_url = req.params.get('pdf_url')
    if not pdf_url:
        return func.HttpResponse(
            "Missing pdf_url parameter",
            status_code=400
        )
    
    endpoint = "https://test-document-shivam.cognitiveservices.azure.com/"
    key = "a92eb119460b4e04b9bb01604bbf986d"

    if not endpoint or not key:
        logging.error("Azure Document Intelligence credentials not found")
        return func.HttpResponse(
            "Azure Document Intelligence credentials not found",
            status_code=500
        )

    # Create a Document Analysis client
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    try:
        # Analyze the document
        poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-read", pdf_url)
        analysis_result = poller.result()
        logging.info(f"Analysis result: {analysis_result}")
        
        # Convert the result to a JSON-serializable dictionary
        output = {
            "content": analysis_result.content,
            "pages": [
                {
                    "page_number": page.page_number,
                    "width": page.width,
                    "height": page.height,
                    "lines": [
                        {
                            "content": line.content,
                            "spans": [
                                {
                                    "offset": span.offset,
                                    "length": span.length
                                } for span in line.spans
                            ]
                        } for line in page.lines
                    ]
                } for page in analysis_result.pages
            ]
        }

        # Return the JSON response
        return func.HttpResponse(
            json.dumps(output, indent=2),
            mimetype="application/json",
            status_code=200
        )
    except ResourceNotFoundError:
        logging.error("The PDF file could not be found or accessed")
        return func.HttpResponse(
            "The PDF file could not be found or accessed.",
            status_code=404
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return func.HttpResponse(
            f"An error occurred: {str(e)}",
            status_code=500
        )