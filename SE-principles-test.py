import random
import openai
from openai import OpenAI
import tkinter as tk
from tkinter import messagebox
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Store history to avoid duplicates
question_history = []
score = {'correct': 0, 'wrong': 0}

# Initialize OpenAI client with API key from .env
client = OpenAI(api_key="sk-" + os.getenv("APP_K") + "A")

current_answers = []
current_correct_index = -1
option_labels = ["A", "B", "C", "D"]

# GUI Setup must come before tkinter variables
root = tk.Tk()
root.title("DevOps Exam App")
root.config(bg="#185488")
root.geometry("800x600")
root.resizable(False, False)

selected_option = tk.IntVar()
selected_option.set(-1)

def generate_question():
    prompt = f"""
    You are a DevOps exam question generator. You will generate ONE multiple choice question related to Software Development and Software Engineering topics such as SDLC, Agile, DevOps, CI/CD, data ethics, Jira, Kanban, Scrum. Do not repeat any of these questions:
    {question_history}

    Your response must be formatted like this:
    Question: <question here>
    Answers:
    - true: <correct answer>
    - false: <wrong answer 1>
    - false: <wrong answer 2>
    - false: <wrong answer 3>

    Make the question conceptually challenging, and do NOT make the correct answer obvious.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes exam questions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )

    text = response.choices[0].message.content.strip()
    #print("\n--- Raw OpenAI Response ---")
    #print(text)
    #print("--- End of Raw Response ---\n")

    lines = text.splitlines()
    question_text = lines[0].replace("Question: ", "")
    answers_raw = []
    for line in lines[2:]:
        line = line.strip().replace("- ", "")
        if line.startswith("true:") or line.startswith("false:"):
            answers_raw.append(line)

    #print("Parsed Question:", question_text)
    #print("Raw Answers:", answers_raw)

    answers = []
    correct_answer = None
    for item in answers_raw:
        if item.startswith("true:"):
            correct_answer = item.replace("true:", "").strip()
            answers.append(correct_answer)
        else:
            answers.append(item.replace("false:", "").strip())

    random.shuffle(answers)
    correct_index = answers.index(correct_answer)

    #print("Shuffled Answers:", answers)
    #print("Correct Index:", correct_index)
    #print("Correct Answer:", answers[correct_index])

    question_history.append(question_text)
    return question_text, answers, correct_index

def display_question():
    global current_answers, current_correct_index
    question_text, current_answers, current_correct_index = generate_question()

    #print("\n--- New Question Displayed ---")
    #print("Question:", question_text)
    #for i, ans in enumerate(current_answers):
        #print(f"{option_labels[i]}. {ans}")
    #print("Correct Answer:", current_answers[current_correct_index])
    #print("--- End of Question ---\n")

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

    #print(f"User selected option {option_labels[idx]}: {current_answers[idx]}")
    #print(f"Correct answer is {option_labels[current_correct_index]}: {current_answers[current_correct_index]}")

    if idx == current_correct_index:
        status_label.config(text="Great job, you're correct!", fg="#00C853")  # Green
        answer_buttons[idx].config(bg="#00C853", fg="white")
        score['correct'] += 1
    else:
        answer_buttons[idx].config(bg="#D32F2F", fg="white")  # Red
        answer_buttons[current_correct_index].config(bg="#00C853", fg="white")  # Green for correct
        correct = f"{option_labels[current_correct_index]}. {current_answers[current_correct_index]}"
        status_label.config(text=f"The correct answer was: {correct}", fg="#D32F2F")
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

status_label = tk.Label(root, text="", font=("Segoe UI", 12), bg="#185488")
status_label.pack(pady=5)

root.bind('<Configure>', update_wraplength)
root.mainloop()
