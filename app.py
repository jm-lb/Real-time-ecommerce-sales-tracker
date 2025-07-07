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
