"""
Run with python -m tests.build_system_prompt (from root) to see the output for first lesson to check formatting and length 
"""

from pathlib import Path
from app.services.lessons.load_lessons import load_all_lessons
from app.services.lessons.load_general import load_general_instructions
from app.services.lessons.build_system_prompt import build_system_prompt

if __name__ == "__main__":
    path = Path(__file__).resolve()
    roleplay_dir = path.parents[1] / "app" / "data" / "lessons" / "roleplay"
    vocabulary_game_dir = (
        path.parents[1] / "app" / "data" / "lessons" / "vocabulary_game"
    )

    lessons = load_all_lessons(roleplay_dir, vocabulary_game_dir)
    general_instructions_path = path.parents[1] / "app" / "data" / "general_instructions_placeholder.toml"
    load_general_instructions(general_instructions_path)

    # take first lesson
    first_lesson = next(iter(lessons.values()))
    system_prompt = build_system_prompt(first_lesson, general_instructions=load_general_instructions(general_instructions_path))
    
    print(system_prompt)
    print(f"Length of system prompt: {len(system_prompt)}")