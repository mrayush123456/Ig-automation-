from flask import Flask, request, render_template_string, redirect, url_for, flash
from instagram_private_api import Client, ClientError
import time

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with your secret key

# HTML Template for the Web Page
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Group Messenger</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            max-width: 500px;
            width: 100%;
        }
        h1 {
            text-align: center;
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: bold;
            margin: 10px 0 5px;
        }
        input, button {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            background-color: #007BFF;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .info {
            font-size: 12px;
            color: #777;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Group Messenger</h1>
        <form action="/" method="POST" enctype="multipart/form-data">
            <label for="username">Instagram Username:</label>
            <input type="text" id="username" name="username" placeholder="Enter your username" required>

            <label for="password">Instagram Password:</label>
            <input type="password" id="password" name="password" placeholder="Enter your password" required>

            <label for="thread_id">Group Thread ID:</label>
            <input type="text" id="thread_id" name="thread_id" placeholder="Enter group thread ID" required>

            <label for="message_file">Message File:</label>
            <input type="file" id="message_file" name="message_file" required>
            <p class="info">Upload a file containing messages, one per line.</p>

            <label for="delay">Delay Between Messages (seconds):</label>
            <input type="number" id="delay" name="delay" placeholder="Enter delay in seconds" required>

            <button type="submit">Send Messages</button>
        </form>
    </div>
</body>
</html>
'''

# Flask Route for Login and Messaging
@app.route("/", methods=["GET", "POST"])
def instagram_messenger():
    if request.method == "POST":
        # Extract form data
        username = request.form["username"]
        password = request.form["password"]
        thread_id = request.form["thread_id"]
        delay = int(request.form["delay"])
        message_file = request.files["message_file"]

        # Read messages from the uploaded file
        try:
            messages = message_file.read().decode("utf-8").splitlines()
        except Exception as e:
            flash(f"Error reading message file: {e}", "error")
            return redirect(url_for("instagram_messenger"))

        # Login to Instagram
        try:
            api = Client(username, password)
            flash("Logged into Instagram successfully!", "success")
        except ClientError as e:
            flash(f"Instagram Login Failed: {e.msg}", "error")
            return redirect(url_for("instagram_messenger"))

        # Send messages to the group thread
        for message in messages:
            try:
                api.direct_v2_message(
                    text=message,
                    thread_ids=[thread_id]
                )
                flash(f"Message sent: {message}", "success")
                time.sleep(delay)  # Delay between messages
            except Exception as e:
                flash(f"Failed to send message: {e}", "error")
                return redirect(url_for("instagram_messenger"))

        flash("All messages sent successfully!", "success")
        return redirect(url_for("instagram_messenger"))

    # Render the form
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

