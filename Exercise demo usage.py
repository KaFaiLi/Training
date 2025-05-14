import requests

# Test the default endpoint
response_default = requests.get("http://127.0.0.1:5000/")
print(f"Request to /:")
print(f"Status Code: {response_default.status_code}")
print(f"Response Text: {response_default.text}")
print("-" * 20)

# Test the endpoint with a name parameter
name_to_test = "PythonClient"
response_with_name = requests.get(f"http://127.0.0.1:5000/?name={name_to_test}")
print(f"Request to /?name={name_to_test}:")
print(f"Status Code: {response_with_name.status_code}")
print(f"Response Text: {response_with_name.text}") 