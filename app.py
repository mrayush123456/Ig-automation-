from flask import Flask, request, render_template_string, redirect, flash
import requests
import time

app = Flask(__name__)
app.secret_key = "your_secret_key"

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Message Sender</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        h1 {
            text-align: center;
            color: #333;
        }
        label {
            display: block;
            margin-top: 10px;
            font-weight: bold;
        }
        input, select, button {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            background-color: #007bff;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .info {
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Message Sender</h1>
        <form action="/" method="POST" enctype="multipart/form-data">
            <label for="access_token">Access Token:</label>
            <input type="text" id="access_token" name="access_token" placeholder="Enter your access token" required>

            <label for="thread_id">Group Thread ID:</label>
            <input type="text" id="thread_id" name="thread_id" placeholder="Enter group thread ID" required>

            <label for="message_file">Message File (.txt):</label>
            <input type="file" id="message_file" name="message_file" accept=".txt" required>
            <p class="info">Upload a .txt file containing messages, one per line.</p>

            <label for="delay">Delay (seconds):</label>
            <input type="number" id="delay" name="delay" placeholder="Enter delay between messages" required>

            <button type="submit">Send Messages</button>
        </form>
    </div>
</body>
</html>
'''

# Endpoint to render form and handle submission
@app.route("/", methods=["GET", "POST"])
def send_messages():
    if request.method == "POST":
        try:
            # Get form data
            access_token = request.form["access_token"]
            thread_id = request.form["thread_id"]
            delay = int(request.form["delay"])
            message_file = request.files["message_file"]

            # Validate and read message file
            messages = message_file.read().decode("utf-8").splitlines()
            if not messages:
                flash("Message file is empty!", "error")
                return redirect("/")

            # Send messages via Instagram Graph API
            for message in messages:
                api_url = f"https://graph.facebook.com/v16.0/{thread_id}/messages"
                data = {
                    "message": message,
                    "access_token": access_token,
                }
                response = requests.post(api_url, data=data)

                # Check API response
                if response.status_code == 200:
                    print(f"Message sent: {message}")
                else:
                    print(f"Failed to send message: {response.json()}")
                    flash(f"Error sending message: {response.json()}", "error")
                    break

                time.sleep(delay)

            flash("All messages sent successfully!", "success")
            return redirect("/")

        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return redirect("/")

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
