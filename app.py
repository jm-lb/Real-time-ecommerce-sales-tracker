import gradio as gr
import pandas as pd
import time
import random

# temp memory storage until i can connect to external database
if 'data_history' not in globals():
    data_history = pd.DataFrame({
        'Order ID': [],
        'Product Name': [],
        'Category': [],
        'Price': [],
        'Quantity': [],
        'Customer Location': [],
        'Timestamp': []
    })

#generate a random order id
def generate_random_order_id():
    return f"ORD-{random.randint(1000, 9999)}-{int(time.time()) % 1000}"

#Adds the new data to the history DataFrame and returns the updated DataFrame.
def add_data(order_id, product_name, category, price, quantity, location, history_df):
   
    global data_history

    # validation of input
    if not all([order_id, product_name, category, price, quantity, location]):
        raise gr.Error("All fields are required. Please fill them out before submitting.")
    if price <= 0:
        raise gr.Error("Price must be a positive number.")
    if quantity <= 0:
        raise gr.Error("Quantity must be a positive integer.")
  

    # Creating new datafram for new entry
    new_entry = pd.DataFrame({
        'Order ID': [order_id],
        'Product Name': [product_name],
        'Category': [category],
        'Price': [f"${price:,.2f}"], # Format price for display
        'Quantity': [int(quantity)],
        'Customer Location': [location],
        'Timestamp': [pd.to_datetime(time.time(), unit='s').strftime('%Y-%m-%d %H:%M:%S')]
    })
# Append the new entry to the global history
    data_history = pd.concat([data_history, new_entry], ignore_index=True)

    # Return the updated history to be displayed
    return data_history

def clear_history():
    """Clears the in-memory data history."""
    global data_history
    data_history = data_history.iloc[0:0] # Clear DataFrame but keep columns
    return data_history, "" # Also clear the error message box

# --- Gradio Interface Definition ---
with gr.Blocks(theme=gr.themes.Soft(), css=".gradio-container {max-width: 960px !important; margin: auto;}") as demo:
    # State to hold the DataFrame across interactions
    history_state = gr.State(data_history)

    gr.Markdown(
        """
        # 📈 Data Source Simulator
        Enter the details for a new order. The submitted data will be collected and displayed in the table below.
        This simulates a real-time data entry point for a data pipeline or database.
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### Order Details")
            order_id_input = gr.Textbox(label="Order ID", value=generate_random_order_id)
            product_name_input = gr.Textbox(label="Product Name", placeholder="e.g., Wireless Mouse")
            category_input = gr.Dropdown(
                label="Category",
                choices=["Electronics", "Books", "Home & Kitchen", "Clothing", "Toys & Games", "Health & Beauty"]
            )
        with gr.Column(scale=2):
            gr.Markdown("### Purchase Information")
            price_input = gr.Number(label="Price (USD)", minimum=0.01, precision=2)
            quantity_input = gr.Number(label="Quantity", minimum=1, precision=0)
            location_input = gr.Textbox(label="Customer Location", placeholder="e.g., New York, USA")


    with gr.Row():
        submit_button = gr.Button("Submit Data", variant="primary")

    gr.Markdown("---")
    gr.Markdown("### Collected Data Log")
    output_dataframe = gr.DataFrame(
        value=data_history,
        headers=['Order ID', 'Product Name', 'Category', 'Price', 'Quantity', 'Customer Location', 'Timestamp'],
        interactive=False
    )

    # --- Event Handlers ---
    submit_button.click(
        fn=add_data,
        inputs=[
            order_id_input,
            product_name_input,
            category_input,
            price_input,
            quantity_input,
            location_input,
            history_state
        ],
        outputs=[output_dataframe]
    )


if __name__ == "__main__":
    demo.launch()