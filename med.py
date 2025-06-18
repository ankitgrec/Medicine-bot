import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from difflib import get_close_matches

# Setup logging
logging.basicConfig(level=logging.INFO)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("medicine-use-419570d06c83.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1EMSLkqU_osdX4SptmtYwxoCee3qwbj-S1KnMdOxr-x8").worksheet("MedicineData")

# Search function
def find_medicine_use(user_input):
    user_input = user_input.strip().lower()
    records = sheet.get_all_records()

    # Step 1: Exact match (any field)
    for row in records:
        fields = [row['Medicine Name'], row['Composition'], row['Brand']]
        if any(user_input in str(field).strip().lower() for field in fields):
            return f"✅ {row['Medicine Name']}:\n{row['Uses']}"

    # Step 2: Fuzzy match (for spelling mistakes)
    all_terms = []
    for row in records:
        all_terms.extend([row['Medicine Name'], row['Composition'], row['Brand']])

    match = get_close_matches(user_input, all_terms, n=1, cutoff=0.6)
    if match:
        return find_medicine_use(match[0])  # recursive search with corrected match

    return "❌ Medicine not found. Please check the spelling."


# Bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Send me any medicine name to know its uses.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    response = find_medicine_use(query)
    await update.message.reply_text(response)

# Main function
def main():
    app = ApplicationBuilder().token("7850112989:AAG1vybskh4GRGgbrv-t2-eCx9wdSTgJokc").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()



