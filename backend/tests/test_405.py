import requests

BASE_URL = "http://localhost:8000"

def test_endpoint(method, url, json_data=None):
    print(f"Testing {method} {url}")
    headers = {"Origin": "http://localhost:3000"}
    if method == "OPTIONS":
        headers["Access-Control-Request-Method"] = "POST"
    
    try:
        if method == "POST":
            response = requests.post(url, json=json_data, headers=headers)
        elif method == "OPTIONS":
            response = requests.options(url, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)

if __name__ == "__main__":
    # Correct usage
    test_endpoint("POST", f"{BASE_URL}/charts/suggest", {
        "columns": {"age": "int"}, 
        "user_query": "plot age"
    })

    # Trailing slash
    test_endpoint("POST", f"{BASE_URL}/charts/suggest/", {
        "columns": {"age": "int"}, 
        "user_query": "plot age"
    })

    # GET request (Validation)
    test_endpoint("GET", f"{BASE_URL}/charts/suggest")

    # OPTIONS request (Preflight)
    test_endpoint("OPTIONS", f"{BASE_URL}/charts/suggest")
