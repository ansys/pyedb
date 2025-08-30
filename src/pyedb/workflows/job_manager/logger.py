import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("solver_manager.log"), logging.StreamHandler()],
)
logger = logging.getLogger("SolverManager")
