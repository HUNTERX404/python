from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from PIL import Image
import os

TOKEN = "7874621200:AAEPohhlCDvqfCINFM2cB0CwYjODRc9OAvo"

# Temporary storage for images
user_images = {}

# Command handler function for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Create PDF", callback_data="start_pdf_process")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Use the button below to start creating a PDF.", reply_markup=reply_markup)

# Callback for button clicks
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_pdf_process":
        # Initialize user's image storage
        user_images[query.from_user.id] = []
        await query.edit_message_text("Send your images. When done, click 'Create Now'.")
        # Add a button to trigger PDF creation
        keyboard = [[InlineKeyboardButton("Create Now", callback_data="create_pdf")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Waiting for your images...", reply_markup=reply_markup)

    elif query.data == "create_pdf":
        images = user_images.get(query.from_user.id, [])
        if not images:
            await query.message.reply_text("No images received! Please send images first.")
            return

        # Create a PDF from the collected images
        pdf_path = f"{query.from_user.id}_output.pdf"
        image_objects = [Image.open(image).convert("RGB") for image in images]
        image_objects[0].save(pdf_path, save_all=True, append_images=image_objects[1:])
        
        # Send the PDF back to the user
        await query.message.reply_document(document=open(pdf_path, "rb"), filename="YourPDF.pdf")
        
        # Clean up files
        for image in images:
            os.remove(image)
        os.remove(pdf_path)

        # Reset user's image list
        user_images[query.from_user.id] = []

# Function to handle received images
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Ensure the user has started the PDF process
    if user_id not in user_images:
        await update.message.reply_text("Please start the PDF creation process first by clicking 'Create PDF'.")
        return

    # Save the image
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_path = f"{photo.file_id}.jpg"
    await file.download_to_drive(file_path)

    # Add the image to the user's list
    user_images[user_id].append(file_path)
    await update.message.reply_text("Image received! You can send more images or click 'Create Now'.")

# Main function to set up the bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()
 
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))  # Handle button clicks
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))  # Handle photos

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
