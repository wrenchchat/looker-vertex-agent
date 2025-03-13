#!/usr/bin/env python3
"""
Check how many questions remain to be tested.
"""

import pickle
import re

def extract_all_questions(file_path):
    """
    Extract all questions from the markdown file.
    Returns a list of tuples: (question, category, difficulty)
    """
    questions = []
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find categories and difficulties
    sections = re.split(r'\*\*([^*]+)\*\*\s*\n\s*\*\*([^*]+)\*\*', content)
    
    # Extract all questions
    for i in range(1, len(sections), 3):
        if i+2 <= len(sections):
            category = sections[i].strip()
            difficulty = sections[i+1].strip()
            section_content = sections[i+2]
            
            # Extract numbered questions
            numbered_questions = re.findall(r'\d+\.\s+(.*?)\n', section_content)
            
            for question in numbered_questions:
                questions.append((question.strip(), category, difficulty))
    
    return questions

# Load tested indices from pickle file
with open('tested_indices.pkl', 'rb') as f:
    tested_indices = pickle.load(f)

# Get total number of questions
questions_file = "/Users/dionedge/dev/looker-vertex-agent/agent-api/tests/test_questions.md"
all_questions = extract_all_questions(questions_file)
total_questions = len(all_questions)

# Calculate statistics
questions_tested = len(tested_indices)
questions_remaining = total_questions - questions_tested

print(f"Total questions in test set: {total_questions}")
print(f"Questions tested so far: {questions_tested}")
print(f"Questions remaining to test: {questions_remaining}")

# Show statistics by category
questions_by_category = {}
for idx, (question, category, difficulty) in enumerate(all_questions):
    if category not in questions_by_category:
        questions_by_category[category] = {'total': 0, 'tested': 0}
    
    questions_by_category[category]['total'] += 1
    if idx in tested_indices:
        questions_by_category[category]['tested'] += 1

print("\nTest progress by category:")
for category, stats in questions_by_category.items():
    percent = (stats['tested'] / stats['total']) * 100 if stats['total'] > 0 else 0
    print(f"  {category}: {stats['tested']}/{stats['total']} tested ({percent:.1f}%)")

# Show statistics by difficulty
questions_by_difficulty = {}
for idx, (question, category, difficulty) in enumerate(all_questions):
    if difficulty not in questions_by_difficulty:
        questions_by_difficulty[difficulty] = {'total': 0, 'tested': 0}
    
    questions_by_difficulty[difficulty]['total'] += 1
    if idx in tested_indices:
        questions_by_difficulty[difficulty]['tested'] += 1

print("\nTest progress by difficulty:")
for difficulty in ['Easy', 'Medium', 'Difficult', 'Extremely Difficult']:
    if difficulty in questions_by_difficulty:
        stats = questions_by_difficulty[difficulty]
        percent = (stats['tested'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"  {difficulty}: {stats['tested']}/{stats['total']} tested ({percent:.1f}%)")