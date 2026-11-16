
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Phone Lookup</title>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, Helvetica, sans-serif;
    background: #f5f6f8;
    color: #202938;
    min-height: 100vh;
}

header {
    height: 65px;
    background: #ffffff;
    border-bottom: 1px solid #e8eaee;
    display: flex;
    align-items: center;
    padding: 0 7%;
}

.logo {
    font-size: 19px;
    font-weight: 700;
    color: #172b4d;
    letter-spacing: -0.5px;
}

main {
    max-width: 650px;
    margin: 85px auto;
    padding: 0 20px;
}

.heading {
    margin-bottom: 28px;
}

.heading h1 {
    font-size: 27px;
    font-weight: 700;
    letter-spacing: -0.8px;
    margin-bottom: 10px;
}

.heading p {
    font-size: 14px;
    color: #778196;
    line-height: 1.7;
}

.search-box {
    background: #fff;
    border: 1px solid #e5e8ed;
    padding: 25px;
    border-radius: 10px;
}

label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 10px;
}

.input-row {
    display: flex;
    gap: 10px;
}

input {
    flex: 1;
    min-width: 0;
    height: 45px;
    padding: 0 13px;
    border: 1px solid #dce1e8;
    border-radius: 6px;
    outline: none;
    font-size: 14px;
    color: #202938;
    transition: border-color .2s;
}

input:focus {
    border-color: #3976d3;
}

button {
    height: 45px;
    padding: 0 22px;
    border: none;
    border-radius: 6px;
    background: #245fba;
    color: white;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
}

button:hover {
    background: #194d9c;
}

button:disabled {
    opacity: .6;
    cursor: wait;
}

.hint {
    font-size: 12px;
    color: #929baa;
    margin-top: 11px;
}

.result {
    display: none;
    margin-top: 22px;
    background: #fff;
    border: 1px solid #e5e8ed;
    border-radius: 10px;
    overflow: hidden;
}

.result-header {
    padding: 18px 20px;
    border-bottom: 1px solid #edf0f3;
    font-size: 14px;
    font-weight: 700;
}

.result-body {
    padding: 5px 20px;
}

.result-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
    padding: 16px 0;
    border-bottom: 1px solid #edf0f3;
    font-size: 13px;
}

.result-row:last-child {
    border-bottom: none;
}

.result-row span:first-child {
    color: #778196;
}

.result-row span:last-child {
    font-weight: 600;
    text-align: right;
    overflow-wrap: anywhere;
}

.status {
    font-size: 13px;
    margin-top: 15px;
    color: #778196;
    display: none;
}

.error {
    color: #c03939;
}

footer {
    text-align: center;
    color: #a0a7b3;
    font-size: 12px;
    padding: 25px;
}

@media (max-width: 480px) {
    main {
        margin-top: 55px;
    }

    .heading h1 {
        font-size: 24px;
    }

    .search-box {
        padding: 18px;
    }

    .input-row {
        flex-direction: column;
    }

    button {
        width: 100%;
    }
}
</style>
</head>

<body>

<header>
    <div class="logo">Phone Lookup</div>
</header>

<main>

    <section class="heading">
        <h1>Phone Number Information</h1>
        <p>
            Enter a phone number with its country code
            to retrieve available numbering information.
        </p>
    </section>

    <section class="search-box">

        <label for="phone">Phone number</label>

        <div class="input-row">
            <input
                type="tel"
                id="phone"
                autocomplete="off"
            >

            <button id="searchBtn" onclick="searchPhone()">
                Search
            </button>
        </div>

        <div class="hint">
            Include the country code. Example: 20 for Egypt.
            The + sign is optional.
        </div>

        <div id="status" class="status"></div>

    </section>

    <section class="result" id="result">

        <div class="result-header">
            Search Results
        </div>

        <div class="result-body" id="resultBody"></div>

    </section>

</main>

<footer>
    Phone Lookup &copy; 2026
</footer>

<script>
const phoneInput = document.getElementById("phone");
const searchBtn = document.getElementById("searchBtn");
const statusBox = document.getElementById("status");
const result = document.getElementById("result");
const resultBody = document.getElementById("resultBody");

function showStatus(message, error = false) {
    statusBox.style.display = "block";
    statusBox.className = error ? "status error" : "status";
    statusBox.textContent = message;
}

function addRow(label, value) {
    const row = document.createElement("div");
    row.className = "result-row";

    const title = document.createElement("span");
    title.textContent = label;

    const content = document.createElement("span");
    content.textContent = value || "Not available";

    row.append(title, content);
    resultBody.appendChild(row);
}

async function searchPhone() {

    const phone = phoneInput.value.trim();

    if (!phone) {
        showStatus("Please enter a phone number.", true);
        return;
    }

    if (!/^\+?\d+$/.test(phone)) {
        showStatus("Please enter a valid phone number format.", true);
        return;
    }

    searchBtn.disabled = true;
    searchBtn.textContent = "Searching...";
    result.style.display = "none";

    showStatus("Retrieving phone information...");

    try {

        const response = await fetch(
            "/lookup?num=" + encodeURIComponent(phone)
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Request failed.");
        }

        resultBody.innerHTML = "";

        addRow("Phone Number", data.number);
        addRow("Country / Region", data.location);
        addRow("Carrier", data.carrier);
        addRow("Time Zone", data.timezones.join(", "));

        result.style.display = "block";
        showStatus("Information retrieved successfully.");

    } catch (error) {
        showStatus(error.message, true);
    } finally {
        searchBtn.disabled = false;
        searchBtn.textContent = "Search";
    }
}

phoneInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        searchPhone();
    }
});
</script>

</body>
</html>
"""


@app.get("/lookup")
def lookup(num: str):

    try:
        phone_num = phonenumbers.parse(
            "+" + num.lstrip("+"), None
        )

        if not phonenumbers.is_valid_number(phone_num):
            raise HTTPException(400, "Invalid phone number")

        return {
            "number": phonenumbers.format_number(
                phone_num,
                phonenumbers.PhoneNumberFormat.E164
            ),
            "location": geocoder.description_for_number(
                phone_num, "en"
            ),
            "carrier": carrier.name_for_number(
                phone_num, "en"
            ),
            "timezones": list(
                timezone.time_zones_for_number(phone_num)
            )
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(400, "Invalid phone number format")
