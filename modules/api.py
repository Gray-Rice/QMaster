import requests

# Test code for registering
# url = "http://127.0.0.1:5000/register"  # Flask API URL
# data = {
#     "username": "api",
#     "password": "api",
#     "fullname": "Api Tester",
#     "qualification": "api",
#     "dob":"2020-2-2"
# }

# response = requests.post(url, json=data)  # Sending JSON request
# print(response.status_code)  # Should print 201 (Created)
# print(response.json())  # Prints the response JSON


# JSON response
# if request.content_type == 'application/json':
#     data = request.json
#     user_data = [
#         data.get('username'),
#         data.get('password'),
#         data.get('fullname'),
#         data.get('qualification'),
#         data.get('dob')
#     ]
#     status = dbm.add_user(user_data)
#     return jsonify({"status": status})