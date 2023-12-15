import json
from typing import List, Optional
from difflib import get_close_matches

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: List[str]) -> Optional[str]:
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_mistake(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["ban"]:
        if q["ban"] == question:
            return q["bAnswer"]

def get_answer_for_question(question: str, knowledge_base: dict) -> str|None:
    for q in knowledge_base:
        if q["question"] == question:
            return q["answer"]

