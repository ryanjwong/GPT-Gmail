import json
import os
import tiktoken

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def append_json_to_file(data, file_path):
    """
    Append JSON data to a JSON file. If the file does not exist, create a new file.

    Parameters:
        data (dict): JSON data to append.
        file_path (str): The path to the JSON file.
    """
    # Check if the file exists
    if os.path.exists(file_path):
        # Read the existing data
        with open(file_path, 'r', encoding='utf-8') as file:
            # Load existing data into a dictionary
            file_data = json.load(file)
            # Append new data
            if isinstance(file_data, list):
                file_data.append(data)
            elif isinstance(file_data, dict):
                file_data.update(data)
    else:
        # Create a new list with the new data if file does not exist
        file_data = [data]

    # Write the updated data back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(file_data, file, indent=4)

def save_to_markdown(text_array, file_path):
    #Open the file in write mode
    with open(file_path, 'w', encoding='utf-8') as file:
        # Write each string in the array to the file on a new line
         for index, subject in enumerate(text_array, start=1):
            file.write(f"# {index}. {subject}:\n\n")
            for point, text in enumerate(text_array[subject], start=1):
                file.write(f"{point}. {text}\n\n")
    
def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def calculate_cost(total):
    return round(num_tokens_from_string(total, "gpt-3.5-turbo") / 1000000.00 * 0.5, 3)