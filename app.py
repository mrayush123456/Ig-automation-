from flask import Flask, request, render_template_string, redirect, url_for, flash
import os
import time
from instagram_private_api import Client, ClientError

app = Flask(__name__)
app.secret_key = "your_secret_key"

# HTML Template for the form
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Automation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f8ff;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            max-width: 400px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }
        label {
            font-weight: bold;
            margin: 10px 0 5px;
            display: block;
        }
        input, select, button {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .info {
            font-size: 12px;
            color: gray;
        }
        .success {
            color: green;
            text-align: center;
        }
        .error {
            color: red;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Automation</h1>
        <form action="/" method="POST" enctype="multipart/form-data">
            <label for="username">Instagram Username:</label>
            <input type="text" id="username" name="username" placeholder="Enter your username" required>

            <label for="password">Instagram Password:</label>
            <input type="password" id="password" name="password" placeholder="Enter your password" required>

            <label for="choice">Send To:</label>
            <select id="choice" name="choice" required>
                <option value="inbox">Inbox</option>
                <option value="group">Group</option>
            </select>

            <label for="target_username">Target Username (for Inbox):</label>
            <input type="text" id="target_username" name="target_username" placeholder="Enter target username">

            <label for="thread_id">Thread ID (for Group):</label>
            <input type="text" id="thread_id" name="thread_id" placeholder="Enter group thread ID">

            <label for="message_file">Message File (.txt):</label>
            <input type="file" id="message_file" name="message_file" required>
            <p class="info">Upload a file containing messages, one per line.</p>

            <label for="delay">Delay (seconds):</label>
            <input type="number" id="delay" name="delay" placeholder="Enter delay in seconds" required>

            <button type="submit">Send Messages</button>
        </form>
    </div>
</body>
</html>
'''

# Login to Instagram
def login_instagram(username, password):
    try:
        api = Client(username, password)
        return api
    except ClientError as e:
        return f"[ERROR] Login failed: {e.msg}"

# Send messages
def send_messages(api, choice, target_username, thread_id, messages, delay):
    try:
        for message in messages:
            if choice == "inbox" and target_username:
                api.direct_v2_message(message, recipients=[{"users": [target_username]}])
                print(f"[INFO] Message sent to inbox: {target_username} - {message}")
            elif choice == "group" and thread_id:
                api.direct_v2_message(message, thread_ids=[thread_id])
                print(f"[INFO] Message sent to group thread {thread_id}: {message}")
            else:
                return "[ERROR] Invalid choice or missing target!"
            time.sleep(delay)
        return "[SUCCESS] All messages sent successfully!"
    except Exception as e:
        return f"[ERROR] Failed to send messages: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def automate_instagram():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        choice = request.form["choice"]
        target_username = request.form.get("target_username")
        thread_id = request.form.get("thread_id")
        delay = int(request.form["delay"])
        message_file = request.files["message_file"]

        # Read messages from uploaded file
        try:
            messages = message_file.read().decode("utf-8").splitlines()
            if not messages:
                flash("The message file is empty.", "error")
                return redirect(url_for("automate_instagram"))
        except Exception as e:
            flash(f"Error reading file: {e}", "error")
            return redirect(url_for("automate_instagram"))

        # Login to Instagram
        api = login_instagram(username, password)
        if isinstance(api, str):  # Error during login
            flash(api, "error")
            return redirect(url_for("automate_instagram"))

        # Send messages
        result = send_messages(api, choice, target_username, thread_id, messages, delay)
        flash(result, "success" if "SUCCESS" in result else "error")
        return redirect(url_for("automate_instagram"))

    # Render HTML form
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True)
            
