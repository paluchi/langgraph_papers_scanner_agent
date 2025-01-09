from dotenv import load_dotenv

load_dotenv(override=True)

import os
import subprocess

# HERE LIES A SCRIPT THAT STARTS THE PAPER SCANNER STREAMLIT APP (prev bigquery setup is neeeded)


def main():
    """
    Runs the Streamlit app located at apps/paper_scanner_app/app.py.
    """
    app_path = "apps/paper_scanner_app/app.py"

    # Check if the app exists
    if not os.path.exists(app_path):
        raise FileNotFoundError(f"Streamlit app not found at {app_path}")

    # Run the Streamlit app with suppressed output
    try:
        print("Starting Streamlit app...")
        subprocess.run(
            [
                "streamlit",
                "run",
                app_path,
                "--server.headless",
                "true",
                "--logger.level",
                "error",
                "--server.address",
                "localhost",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to run Streamlit app: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
