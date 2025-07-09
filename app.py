import gradio as gr
import pandas as pd
import time
import random
import json
from google.cloud import pubsub_v1

#GCP configuratoin. make sure env is authenticated
PROJECT_ID = "gcp-project-id"
TOPIC_ID = "pubsub-topic-name"

#initialize pubsub publisher client
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

#in-memory storage for display purposes only
data_history = pd.DataFrame({
    'Order ID': [], 'Product Name': [], 'Category': [], 'Price': [],
    'Quantity': [], 'Customer Location': [], 'Timestamp': []
})

def generate_random_order_id():
    """Generates a unique random order ID."""
    return f"ORD-{random.randint(1000, 9999)}-{int(time.time()) % 1000}"

def submit_to_pubsub_and_update_ui(order_id, product_name, category, price, quantity, location):
    """Sends data to GC pub/sub and updates the local UI display."""
    global data_history

    #input validation
    if not all([order_id, product_name, category, price, quantity, location]):
        raise gr.Error("All fields are required. Please fill them out before submitting.")
    if price <= 0:
        raise gr.Error("Price must be a positive number.")
    if quantity <= 0:
        raise gr.Error("Quantity must be a positive integer.")
    
    # prepare data payload as a dictionary
    timestamp = pd.to_datetime(time.time(), unit='s').isoformat()
    data_dict = {
        "order_id": order_id,
        "product_name": product_name,
        "category": category,
        "price": float(price),
        "quantity": int(quantity),
        "customer_location": location,
        "timestamp": timestamp
    }

    # publish to google cloud pub/sub
    try:
        data_payload = json.dumps(data_dict).encode("utf-8")
        future = publisher.publish(topic_path, data_payload)
        #block until the message is published
        print(f"published message to pubsub with ID: {future.result()}")
    except Exception as e:
        raise gr.Error(f"GCP Publishing Error: {e}")
    
    # update local data frame for UI display. for visual feedback in gradio app
    display_entry = pd.DataFrame({
        'Order ID': [order_id],
        'Product Name': [product_name],
        'Category': [category],
        'Price': [f"${price:,.2f}"], # Format for display only
        'Quantity': [int(quantity)],
        'Customer Location': [location],
        'Timestamp': [pd.to_datetime(timestamp).strftime('%Y-%m-%d %H:%M:%S')]
    })
    data_history = pd.concat([data_history, display_entry], ignore_index=True)

    # returnt he updated history to the gradio datafram component
    return data_history

#gradio interface
with gr.Blocks(theme=gr.themes.Soft(), css=".gradio-container {max-width: 960px !important; margin: auto;}") as demo:
    gr.Markdown("# 📈 Data Source Simulator (Connected to GCP)")
    with gr.Row():
        with gr.Column(scale=2):
            order_id_input = gr.Textbox(label="Order ID", value=generate_random_order_id)
            product_name_input = gr.Textbox(label="Product Name", placeholder="e.g., Wireless Mouse")
            category_input = gr.Dropdown(label="Category", choices=["Electronics", "Books", "Home & Kitchen", "Clothing", "Toys & Games", "Health & Beauty"])
        with gr.Column(scale=2):
            price_input = gr.Number(label="Price (USD)", minimum=0.01, precision=2)
            quantity_input = gr.Number(label="Quantity", minimum=1, precision=0)
            location_input = gr.Textbox(label="Customer Location", placeholder="e.g., New York, USA")

    submit_button = gr.Button("Submit Data to GCP", variant="primary")
    gr.Markdown("---")
    gr.Markdown("### Data Log (Local Display)")
    output_dataframe = gr.DataFrame(value=data_history, interactive=False)

    # --- Event Handler ---
    submit_button.click(
        fn=submit_to_pubsub_and_update_ui,
        inputs=[order_id_input, product_name_input, category_input, price_input, quantity_input, location_input],
        outputs=[output_dataframe]
    )

if __name__ == "__main__":
    demo.launch()