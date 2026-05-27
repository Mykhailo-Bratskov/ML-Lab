# Prompt Extraction
from pathlib import Path

def ask_for_zip_folder(zip_folder: str): 
    zip = True
    while True:
        if zip:
            zip_path = input("\nEnter zip folder's name with data:\n> ")
            zip_path = Path(zip_folder)
            # Check if file exists
            if not zip_path.exists():
                raise FileNotFoundError(f"Zip file not found: {zip_path}")
        else:
            query_text = input("\nAny addittional zip folders? Type 'quit' to exit:\n> ")

        if query_text.lower().strip() == 'quit': 
            break
    # getting input from the user 
    zip_path = Path(zip_folder)
    
    # Check if file exists
    if not zip_path.exists():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")



def ask_for_contest_rules(file: str = None, url_link: str = None):
    """
    Get contest rules from either a file or URL link.
    Validates the file exists if provided, or validates the URL format.
    """
    rules_source = None
    
    while True:
        choice = input("\nHow would you like to provide contest rules?\n1. From a file\n2. From a URL\n3. Skip\nEnter choice (1/2/3):\n> ").strip()
        
        if choice == '1':
            if file:
                file_path = Path(file)
            else:
                file = input("\nEnter contest rules file path:\n> ").strip()
                file_path = Path(file)
            
            # Check if file exists
            if not file_path.exists():
                print(f"Error: File not found: {file_path}")
                retry = input("Try again? (yes/no):\n> ").strip().lower()
                if retry != 'yes':
                    break
                continue
            
            rules_source = {'type': 'file', 'path': file_path}
            print(f"✓ Contest rules loaded from: {file_path}")
            break
        
        elif choice == '2':
            if url_link:
                url = url_link
            else:
                url = input("\nEnter contest rules URL:\n> ").strip()
            
            # Basic URL validation
            if not url.startswith(('http://', 'https://')):
                print("Error: Invalid URL format. Must start with http:// or https://")
                retry = input("Try again? (yes/no):\n> ").strip().lower()
                if retry != 'yes':
                    break
                continue
            
            rules_source = {'type': 'url', 'url': url}
            print(f"✓ Contest rules URL set to: {url}")
            break
        
        elif choice == '3':
            print("Skipping contest rules...")
            break
        
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    return rules_source


def ask_for_prompt(string: str = None):
    """
    Get a prompt from user input.
    Allows user to input a prompt directly or load from string parameter.
    Validates that the prompt is not empty.
    """
    prompt = None
    
    while True:
        if string:
            prompt = string
            print(f"✓ Using provided prompt")
        else:
            prompt = input("\nEnter your prompt:\n> ").strip()
        
        # Validate prompt is not empty
        if not prompt:
            print("Error: Prompt cannot be empty.")
            retry = input("Try again? (yes/no):\n> ").strip().lower()
            if retry != 'yes':
                print("Skipping prompt input...")
                return None
            continue
        
        # Ask for confirmation
        print(f"\nPrompt: {prompt}")
        confirm = input("Is this correct? (yes/no):\n> ").strip().lower()
        
        if confirm == 'yes':
            print("✓ Prompt confirmed.")
            return prompt
        else:
            retry = input("Enter new prompt? (yes/no):\n> ").strip().lower()
            if retry != 'yes':
                print("Skipping prompt input...")
                return None
            string = None  # Reset to allow new input