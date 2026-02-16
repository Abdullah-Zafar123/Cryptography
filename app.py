from flask import Flask, render_template, request, redirect, flash, url_for
import os
import base64

app = Flask(__name__)
app.secret_key = "supersecretkey"

FILENAME = "encrypted_data.txt"

# --- Encryption / Decryption using Base64 ---
def encrypt_text(text, key):
    encrypted = ""
    for i, ch in enumerate(text):
        encrypted += chr((ord(ch) + ord(key[i % len(key)])) % 256)
    # Encode as Base64 to make it UTF-8 safe
    return base64.b64encode(encrypted.encode("latin1")).decode("utf-8")

def decrypt_text(text, key):
    # Decode from Base64 first
    encrypted = base64.b64decode(text.encode("utf-8")).decode("latin1")
    decrypted = ""
    for i, ch in enumerate(encrypted):
        decrypted += chr((ord(ch) - ord(key[i % len(key)])) % 256)
    return decrypted

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/encrypt", methods=["GET", "POST"])
def encrypt_page():
    if request.method == "POST":
        data = request.form.get("data", "").strip()
        key = request.form.get("key", "").strip()

        if not data or not key:
            flash("Please enter both text and key!", "error")
            return redirect(url_for("encrypt_page"))

        encrypted = encrypt_text(data, key)

        # Save to file
        line_num = 1
        if os.path.exists(FILENAME):
            with open(FILENAME, "r", encoding="utf-8") as f:
                line_num = sum(1 for _ in f) + 1

        with open(FILENAME, "a", encoding="utf-8") as f:
            f.write(f"{line_num}) {encrypted}\n")

        flash(f"Data encrypted! Saved as item #{line_num}", "success")
        return redirect(url_for("encrypt_page"))

    return render_template("encrypt.html")

@app.route("/decrypt", methods=["GET", "POST"])
def decrypt_page():
    lines = []
    if os.path.exists(FILENAME):
        with open(FILENAME, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

    if request.method == "POST":
        selected_index = int(request.form.get("item", -1))
        key = request.form.get("key", "").strip()

        if selected_index < 0 or selected_index >= len(lines):
            flash("Select a valid encrypted item!", "error")
            return redirect(url_for("decrypt_page"))

        if not key:
            flash("Please enter a key!", "error")
            return redirect(url_for("decrypt_page"))

        encrypted_text = lines[selected_index].split(") ", 1)[1]

        try:
            decrypted_text = decrypt_text(encrypted_text, key)
            flash(f"Decrypted text: {decrypted_text}", "success")
        except Exception:
            flash("Decryption failed! Wrong key?", "error")

        return redirect(url_for("decrypt_page"))

    return render_template("decrypt.html", lines=lines)

if __name__ == "__main__":
    app.run(debug=True)
