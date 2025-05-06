import random
import openai
from openai import OpenAI
import tkinter as tk
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Store history to avoid duplicates and rotate styles
question_history = []
question_types_used = set()
score = {'correct': 0, 'wrong': 0}

# Initialize OpenAI client with API key from .env
client = OpenAI(api_key="sk-" + os.getenv("APP_K") + "A")

current_answers = []
current_correct_index = -1
option_labels = ["A", "B", "C", "D"]
question_styles = [
    "Conceptual understanding",
    "Scenario-based",
    "Process ordering",
    "Error diagnosis",
    "Matching",
    "NOT/EXCEPT logic",
    "Code or YAML snippet evaluation"
]

# GUI Setup must come before tkinter variables
root = tk.Tk()
root.title("DevOps Exam App")
root.config(bg="#185488")
root.geometry("800x600")
root.resizable(False, False)

selected_option = tk.IntVar()
selected_option.set(-1)

def get_next_question_style():
    remaining_styles = list(set(question_styles) - question_types_used)
    if not remaining_styles:
        question_types_used.clear()
        remaining_styles = question_styles.copy()
    selected = random.choice(remaining_styles)
    question_types_used.add(selected)
    return selected

def generate_question():
    style = get_next_question_style()

    prompt = f"""
    You are a DevOps exam question generator. Generate ONE multiple-choice question in the style of: **{style}**.
    Choose a topic such as SDLC, Agile, DevOps, CI/CD, data ethics, Jira, Kanban, Scrum, or general software development.

    DO NOT reuse or paraphrase any previous question in this list:
    {question_history}

    Return your answer in this format:
    Question: <question here>
    Answers:
    - true: <correct answer>
    - false: <wrong answer 1>
    - false: <wrong answer 2>
    - false: <wrong answer 3>

    Add a line: #Type: {style} at the end.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes exam questions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=600
    )

    text = response.choices[0].message.content.strip()
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#Type:")]

    if not lines or not lines[0].startswith("Question:"):
        raise ValueError("Malformed response: Missing 'Question:' line.")

    question_text = lines[0].replace("Question: ", "").strip()
    answers_raw = [line for line in lines[1:] if line.startswith("- true:") or line.startswith("- false:") or line.startswith("true:") or line.startswith("false:")]

    answers = []
    correct_answer = None
    for item in answers_raw:
        match = re.match(r"^(true|false):\s*(.+)$", item.replace("- ", ""))
        if match:
            is_correct, answer_text = match.groups()
            if is_correct == "true":
                correct_answer = answer_text.strip()
            answers.append(answer_text.strip())

    if correct_answer is None or correct_answer not in answers:
        raise ValueError("Malformed response: Correct answer not found or missing.\n Don't worry. Just continue with the test.")

    random.shuffle(answers)
    correct_index = answers.index(correct_answer)

    tagged_question = f"[{style}] {question_text}"
    question_history.append(tagged_question)

    return question_text, answers, correct_index

def display_question():
    global current_answers, current_correct_index
    question_text, current_answers, current_correct_index = generate_question()

    question_label.config(text=question_text)
    selected_option.set(-1)
    for i in range(4):
        answer_buttons[i].config(text=f"{option_labels[i]}. {current_answers[i]}", bg="#E3F2FD", fg="#000000")
    generate_btn.config(text="Next Question", state="disabled")
    submit_btn.config(state="normal")
    status_label.config(text="", fg="#333333")

def check_answer():
    idx = selected_option.get()

    if not current_answers or current_correct_index == -1:
        status_label.config(text="Please generate a question first.", fg="orange")
        return

    if idx not in range(len(current_answers)):
        status_label.config(text="Please select an answer before submitting.", fg="orange")
        return

    if idx == current_correct_index:
        status_label.config(text="Great job, you're correct!", fg="#13ff45")
        answer_buttons[idx].config(bg="#00C853", fg="white")
        score['correct'] += 1
    else:
        answer_buttons[idx].config(bg="#D32F2F", fg="white")
        answer_buttons[current_correct_index].config(bg="#00C853", fg="white")
        correct = f"{option_labels[current_correct_index]}. {current_answers[current_correct_index]}"
        status_label.config(text=f"The correct answer was: {correct}", fg="#fff832")
        score['wrong'] += 1

    update_score()
    submit_btn.config(state="disabled")
    generate_btn.config(state="normal")

def update_score():
    score_label.config(text=f"Score: ✅ {score['correct']} ❌ {score['wrong']}")

def update_wraplength(event=None):
    wrap = root.winfo_width() - 100
    for btn in answer_buttons:
        btn.config(wraplength=wrap)

question_label = tk.Label(
    root,
    text="Click 'Generate Question' to start",
    wraplength=760,
    justify="left",
    anchor="w",
    font=("Segoe UI", 14),
    bg="#185488",
    fg="white"
)
question_label.pack(pady=20, padx=20)

answer_frame = tk.Frame(root, bg="#185488")
answer_frame.pack()

answer_buttons = []
for i in range(4):
    radio = tk.Radiobutton(
        answer_frame,
        text="",
        variable=selected_option,
        value=i,
        anchor="w",
        font=("Segoe UI", 12),
        indicatoron=False,
        width=80,
        justify="left",
        padx=10,
        pady=10,
        bg="#E3F2FD",
        fg="#000000",
        activebackground="#BBDEFB",
        selectcolor="#BBDEFB",
        bd=2,
        relief="raised"
    )
    radio.grid(row=i, column=0, padx=10, pady=5, sticky="w")
    answer_buttons.append(radio)

button_frame = tk.Frame(root, bg="#185488")
button_frame.pack(pady=15)

submit_btn = tk.Button(button_frame, text="Submit Answer", command=check_answer, font=("Segoe UI", 12), bg="#F57C00", fg="white", padx=10, pady=5, state="disabled")
submit_btn.grid(row=0, column=0, padx=10)

generate_btn = tk.Button(button_frame, text="Generate Question", command=display_question, font=("Segoe UI", 12), bg="#43A047", fg="white", padx=10, pady=5)
generate_btn.grid(row=0, column=1, padx=10)

score_label = tk.Label(root, text="Score: ✅ 0 ❌ 0", font=("Segoe UI", 12), bg="#185488", fg="white")
score_label.pack(pady=10)

status_label = tk.Label(root, wraplength=750, text="", font=("Segoe UI", 12), bg="#185488")
status_label.pack(pady=5)

root.bind('<Configure>', update_wraplength)
root.mainloop()
