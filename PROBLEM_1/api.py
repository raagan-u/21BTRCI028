from flask import Flask,jsonify
from dotenv import load_dotenv
import os
import requests as r
import time

load_dotenv()

num_w = []
number_set = set()
MAX_SIZE = 10
prev_state = []

c_id = os.getenv("CLIENT_ID")
c_secret = os.getenv("CLIENT_SECRET")

current_token = None
token_expiry = None

app = Flask(__name__)

def fetch_new_token():
	global current_token,token_expiry
	creds = {
    "companyName": "Jain University",
    "clientID": f"{c_id}",
    "clientSecret": f"{c_secret}",
    "ownerName": "Raagan U",
    "ownerEmail": "raaganuthayaargn@gmail.com",
    "rollNo": "21BTRCI028"
	}
	resp = r.post("http://20.244.56.144/test/auth", headers={"Content-Type": "application/json"}, json=creds)
	print(creds)
	if resp.status_code == 201:
		token_data = resp.json()
		current_token = token_data['access_token']
		token_expiry = time.time() + token_data.get('expires_in', 3600) - 60
		return True
	else:
		print(resp.status_code)
		print(resp.text)
		return False

def get_numbers(num_type):
	global current_token,token_expiry
	if not current_token or time.time() > token_expiry:
		print(fetch_new_token())
	
	print("token", current_token)
	qualifiers = {'p': 'primes', 'f':'fibo', 'e':'even', 'r':'rand'}
	headers = {
	"Authorization": f"Bearer {current_token}",
	"Content-Type": "application/json"
	}
	url = "http://20.244.56.144/test/"+qualifiers[num_type]
	resp = r.get(url, headers=headers)
	if resp.status_code == 200:
		resp = resp.json()
		return resp["numbers"]
	else:
		print(resp.text)
		return []

@app.route("/numbers/<string:numberid>")
def handler(numberid):
	if numberid not in ['p', 'f', 'e', 'r']:
		return jsonify({"error": "invalid number type"}), 400
	print(numberid)
	nums = get_numbers(numberid)
	if len(nums) == 0:
		return jsonify({"err": "nums_not_received"}), 400
	for num in nums:
		if num not in number_set:
			if len(num_w) > MAX_SIZE:
				oldest = num_w.pop(0)
				number_set.remove(oldest)
			num_w.append(num)
			number_set.add(num)
	avg = sum(num_w)/len(num_w)
	global prev_state
	response = {
		"numbers": nums,
		"windowPrevState": prev_state,
		"windowCurrState": num_w,
		"avg": avg

	}
	prev_state = num_w
	return jsonify(response), 200

if __name__ == "__main__":
	app.run(debug=True)