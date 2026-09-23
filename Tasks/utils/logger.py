import logging
import os

# Create logs folder
os.makedirs("logs", exist_ok=True)

# Log file path
log_file = os.path.join("logs", "automation.log")

# Configure logging
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)