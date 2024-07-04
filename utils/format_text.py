import json


def init_prompt():
    global question_template, answer_template
    with open("prompt/template/question.txt") as f:
        question_template = f.read()
    with open("prompt/template/answer.txt") as f:
        answer_template = f.read()


init_prompt()


def get_history_text(history, is_dump=False, with_table_diff=True):
    if is_dump:
        history = convert_history_to_dumped_text(history, with_table_diff=with_table_diff)
    else:
        history = convert_history_to_text(history, with_table_diff=with_table_diff)
    return history


def format_information(information, with_table_diff=True):
    result = ""
    for index, item in enumerate(information["sheet_state"]):
        result += item
        if with_table_diff and "table_diff" in information and index < len(information["table_diff"]):
            result += "\n"
            result += information["table_diff"][index]
    result += "\n"
    result += information["user_prompt"]
    result += "\n"
    return result


def convert_history_to_text(history, with_table_diff=True):
    start_index = 0

    prompt = format_information(history["information"], with_table_diff)

    question_index = 1
    for pair in history["question_answer_pairs"]:
        question = pair["question"]
        choices = pair["choices"]

        choices_text = ""
        for i, choice in enumerate(choices, start=1):
            choices_text += f"{i}. {choice}\n"

        prompt += "\n"

        question_answer_pair = (
            question_template.replace("{INDEX}", str(question_index))
            .replace("{QUESTION}", question)
            .replace("{CHOICES}", choices_text)
        )
        if "answer" in pair:
            answer = pair["answer"]
            question_answer_pair += answer_template.replace(
                "{INDEX}", str(question_index)
            ).replace("{ANSWER}", answer)

        question_index += 1
        prompt += question_answer_pair
    return prompt


def convert_history_to_dumped_text(history, with_table_diff=True):
    start_index = 0

    prompt = format_information(history["information"], with_table_diff)
    prompt += "Question & Answering History:\n"

    for pair in history["question_answer_pairs"]:
        question = pair["question"]
        choices = pair["choices"]
        summary = pair["summary"]

        question_answer_pair = "ASSISTANT:\n"
        question_answer_pair += json.dumps(
            {
                "type": "question",
                "summary": summary,
                "question": question,
                "choices": choices,
            },
            indent=4,
        )

        answer = pair["answer"]
        question_answer_pair += "\n\nUSER:\n"
        question_answer_pair += json.dumps({"choice": answer}, indent=4)

        prompt += question_answer_pair
    return prompt
