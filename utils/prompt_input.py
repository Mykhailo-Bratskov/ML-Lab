# Prompt Extraction
from pathlib import Path

def ask_for_zip_folder(zip_folder: str = None) -> str:
    """
    Ask for a dataset ZIP path and return it as a string path.
    If `zip_folder` is provided, validate and return it directly.
    """
    while True:
        raw_path = zip_folder if zip_folder else input("\nEnter zip file path with data:\n> ").strip()
        zip_path = Path(raw_path).expanduser()

        if not zip_path.exists():
            print(f"Error: Zip file not found: {zip_path}")
        elif not zip_path.is_file():
            print(f"Error: Path is not a file: {zip_path}")
        elif zip_path.suffix.lower() != ".zip":
            print(f"Error: Expected a .zip file, got: {zip_path.suffix}")
        else:
            return str(zip_path)

        if zip_folder:
            raise FileNotFoundError(f"Invalid zip path provided: {zip_path}")

        retry = input("Try again? (yes/no):\n> ").strip().lower()
        if retry != "yes":
            raise FileNotFoundError("No valid zip file path was provided.")



def ask_for_contest_rules(file: str = None, url_link: str = None):
    """
    Get contest rules from a file (PDF or text), URL link, or skip.
    Validates the file exists and has correct extension if provided.
    """
    rules_source = None
    allowed_extensions = {'.pdf', '.txt', '.md', '.doc', '.docx'}
    
    while True:
        choice = input("\nHow would you like to provide contest rules?\n1. From a file (PDF/TXT/MD/DOC)\n2. From a URL\n3. Skip\nEnter choice (1/2/3):\n> ").strip()
        
        if choice == '1':
            if file:
                file_path = Path(file)
            else:
                file = input("\nEnter contest rules file path (PDF/TXT/MD/DOC):\n> ").strip()
                file_path = Path(file)
            
            # Check if file exists
            if not file_path.exists():
                print(f"Error: File not found: {file_path}")
                retry = input("Try again? (yes/no):\n> ").strip().lower()
                if retry != 'yes':
                    break
                continue
            
            # Validate file extension
            file_extension = file_path.suffix.lower()
            if file_extension not in allowed_extensions:
                print(f"Error: Invalid file type '{file_extension}'. Allowed types: {', '.join(allowed_extensions)}")
                retry = input("Try again? (yes/no):\n> ").strip().lower()
                if retry != 'yes':
                    break
                continue
            
            rules_source = {'type': 'file', 'path': file_path, 'file_type': file_extension}
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
