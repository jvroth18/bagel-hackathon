import os
import bagel
from getpass import getpass

# Copy & Paste the API Key from https://bakery.bagel.net/api-key
DEMO_KEY_IN_USE = getpass("Enter your API key: ")

client = bagel.Client()

# Set environment variable
api_key = os.environ['BAGEL_API_KEY'] = DEMO_KEY_IN_USE

payload = {
    "dataset_type": "RAW",
    "title": "insert title",
    "category": "insert categoty",
    "details": "provide details", #e.g "testing"
    "tags": ["insert tags"], # e.g ["AI", "DEMO", "TEST"] 
    "user_id": "insert the UID" # UID is assigned during avvount generation
}

# Calling the create asset method
asset_id = client.create_asset(payload, api_key)
file_path = "data/sample.csv" # e.g "product_catalog.csv" or "path/dir/file.csv"
# Calling the file upload method
response = client.file_upload(file_path, 
                              asset_id, # id from the step above
                              api_key)
print(response)

# Purchase the asset fom the Bakey
model_id = "insert model id"
user_id = "insert user id"
base_model = client.buy_asset(model_id, user_id, api_key)

# Initalize the finetuning process
file_name = "input file path" # base name of file in raw asset 
title = "create a title for the finetuned model"  # choose a title 
finetuned_model = client.fine_tune(title=title,
                            user_id=user_id,
                            asset_id=asset_id,
                            file_name=file_name,
                            base_model=base_model,
                            epochs=3,
                            learning_rate=0.01
                            )

# Download the model to perform inference
client.download_model(finetuned_model, api_key)

