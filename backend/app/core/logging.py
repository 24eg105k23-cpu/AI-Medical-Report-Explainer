import logging
import sys

# Configure standard logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("medi_explainer")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"medi_explainer.{name}")
