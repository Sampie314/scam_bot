import requests
import json

def check_url_with_google_safe_browsing(url, logger):
    logger.debug("running submit url to Google Safe Browsing")
    with open('keys.json') as keys_file:
        keys = json.load(keys_file)

    endpoint = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "client": {
            "clientId": "ScamBot",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION", "THREAT_TYPE_UNSPECIFIED"],
            "platformTypes": ["WINDOWS", "LINUX", "ANDROID", "OSX", "IOS", "ANY_PLATFORM", "ALL_PLATFORMS", "CHROME", "PLATFORM_TYPE_UNSPECIFIED"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [
                {"url": url}
            ]
        }
    }
    api_key = keys['GOOGLE_KEY']
    response = requests.post(f"{endpoint}?key={api_key}", headers=headers, json=payload)
    result = response.json()
    
    # Check if the response contains threat matches
    if 'matches' in result:
        logger.info("Threats found: Processing results.")
        logger.info(json.dumps(result))
        return result  # Return the entire JSON to be processed by another function
    else:
        logger.info("No threats detected.")
        return {"matches": []}  # Return an empty 'matches' list if no threats are found
    
