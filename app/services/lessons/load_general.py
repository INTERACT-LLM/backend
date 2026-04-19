""" 
Placeholder for now; needs to be updated to somehow be populated with knowledge about user (given from the frontend)
"""
from pathlib import Path 
import tomllib
from app.models.instructions.general import ModelInstructionsGeneral

DEFAULT_GENERAL_INSTRUCTIONS_PATH = Path(__file__).parents[2] / "data" / "general_instructions_placeholder.toml"

def load_general_instructions(general_instructions_path: Path = DEFAULT_GENERAL_INSTRUCTIONS_PATH) -> ModelInstructionsGeneral:
    if not general_instructions_path.exists() or not general_instructions_path.is_file():
        raise ValueError(f"General instructions file {general_instructions_path} does not exist or is not a file.")

    with open(general_instructions_path, "rb") as f:
        data = tomllib.load(f)  
    
    general_instructions = ModelInstructionsGeneral.model_validate(data)
    
    return general_instructions