import azure.functions as func
import logging
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function App to process a PDF document using Azure's Document Analysis Client.
    The function is triggered by an HTTP request and expects a 'pdf_url' parameter in the request.

    :param req: The HTTP trigger request object.
    :return: An HTTP response object. The response body contains the analysis result in JSON format.
    """

    # Log that the function was called
    logging.info("ProcessPDF function called")
    
    # Get the URL of the PDF document from the request parameters
    pdf_url = req.params.get('pdf_url')
    if not pdf_url:
        # If the 'pdf_url' parameter is missing, return a 400 response
        return func.HttpResponse(
            "Missing pdf_url parameter",
            status_code=400
        )

    # Get the Azure Document Intelligence credentials from environment variables
    endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
    key = os.getenv("FORM_RECOGNIZER_KEY")

    if not endpoint or not key:
        # If the credentials are not found, log an error and return a 500 response
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

        # Log the analysis result
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
        # If the PDF file could not be found or accessed, log an error and return a 404 response
        logging.error("The PDF file could not be found or accessed")
        return func.HttpResponse(
            "The PDF file could not be found or accessed.",
            status_code=404
        )
    except Exception as e:
        # If an error occurred, log the error and return a 500 response
        logging.error(f"An error occurred: {str(e)}")
        return func.HttpResponse(
            f"An error occurred: {str(e)}",
            status_code=500
        )