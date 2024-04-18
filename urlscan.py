import requests
import json
import time

def submit_url_to_urlscan(url, logger):
    logger.debug("running submit url to urlscan")
    with open('keys.json') as keys_file:
        keys = json.load(keys_file)

    headers = {
        'API-Key': keys['URLSCAN_KEY'],
        'Content-Type': 'application/json',
    }
    data = {
        "url": url,
        "visibility": "private"  # Use "public" for shared scans, "unlisted" or "private" for more privacy
    }
    response = requests.post('https://urlscan.io/api/v1/scan/', headers=headers, json=data)

    logger.debug("RESPONSE RECEIVED")
    logger.debug("status code: " + str(response.status_code))

    # Poll for results until the scan is complete
    while True:
        if response.status_code == 200:
            result_data = response.json()
            
            logger.info("Scan Completed: " + json.dumps(response.json()))

            # Extract the UUID from the response
            uuid = result_data['uuid']
            results_link = result_data['result']
            result_url = result_data['api']

            # Wait for at least 10 seconds before starting to poll
            logger.info("10 second buffer before polling...")
            time.sleep(10)

            # Polling for results
            for _ in range(60):  # Adjust the range for longer polling
                result_response = requests.get(result_url, headers=headers)
                logger.info("Polling for Results")
                if result_response.status_code == 200:
                    try:
                        result_data = result_response.json()
                        logger.info("Poll Completed")
                        return format_scan_results(result_data, url, results_link, logger)
                    except json.JSONDecodeError as e:
                        logger.error("Failed to decode JSON from response: " + str(e))
                        return "Received data is not valid JSON."

                elif result_response.status_code == 404:
                    logger.info("Retrying poll...")
                    time.sleep(2)  # Poll every 2 seconds
                else:
                    logger.error("Error retrieving the results. Status code: {}".format(result_response.status_code))
                    return "Failed to retrieve scan results."

            return "Scan results timed out."
            
            # return response.json()['result']

        elif response.status_code == 404:
            # Scan is not yet ready, wait a bit before retrying
            time.sleep(10)
        else:
            return "Error submitting the URL."
        

def format_scan_results(data, url, results_url, logger):
    logger.info("Formatting Results...")
    # Extracting detailed information
    verdicts = data.get('verdicts', {}).get('urlscan', {})
    page_info = data.get('page', {})
    lists = data.get('lists', {})

    logger.info("\nVERDICTS:\n" + json.dumps(verdicts))
    logger.info("\nVERDICTS:\n" + json.dumps(data.get('verdicts', {})))
    # logger.info("\nVERDICTS:\n" + json.dumps(verdicts))

    formatted_result = {
        "Submitted URL" : url,
        "Results URL" : results_url,
        "Malicious Score": verdicts.get('score'),
        "Page Title": page_info.get('title'),
        "Primary URL": page_info.get('url'),
        "Redirected": page_info.get('redirected'),
        "IP Addresses": lists.get('ips'),
        "Countries": lists.get('countries'),
    }

    logger.info("Formatted Results: " + json.dumps(formatted_result, indent=4))

    return formatted_result  # Returning formatted JSON string