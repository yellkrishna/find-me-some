import logging
import os
# Configure the logging
logging.basicConfig(
    filename='app.log',  # Set the log file name
    level=logging.INFO,  # Set the log level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Example log statements
logging.info("This is an info message")
logging.warning(OPENAI_API_KEY)
logging.error("This is an error message")