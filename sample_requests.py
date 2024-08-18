# Import the requests library
import requests
import sys
# Define the URL of the Azure Function
url = "https://pdfprocessorapi.azurewebsites.net/api/ProcessPDF"
code_param = sys.argv[1] #mention secret here
# Define the parameters to be sent with the request
params = {
    "code": code_param,  # The function key
    "pdf_url": "https://www.arvindguptatoys.com/arvindgupta/dyslexia.pdf"  # The URL of the PDF to be processed
}

# Send a POST request to the Azure Function
response = requests.post(url, params=params)

# Print the status code of the response for debugging
print(f"Status Code: {response.status_code}")

# Print the content of the response for debugging
print(f"Response Content: {response.text}")

# Try to parse the response content as JSON
try:
    response_json = response.json()
    print(response_json)  # Print the parsed JSON
except requests.exceptions.JSONDecodeError:
    # If the response content is not valid JSON, print an error message
    print("Response is not in JSON format")
    print(response.text)  # Print the raw response content