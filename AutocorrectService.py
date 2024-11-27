from transformers import pipeline

# Створюємо інструмент для виправлення граматики та стилю
corrector = pipeline("text2text-generation", model="t5-small")

def auto_correct_text(input_text):
    """
    Використовує модель ШІ для автозаміни слів у вхідному тексті, щоб покращити його читабельність та стиль.

    Parameters:
    input_text (str): Текст для автозаміни.

    Returns:
    str: Відкоригований текст.
    """
    # Генеруємо виправлений текст, передаючи інструкцію для корекції
    corrected_text = corrector(
        f"correct grammar: {input_text}",
        max_length=2000,  # Increase max_length for longer result
        min_length=100,   # Set a minimum length to avoid short outputs
        num_beams=5,      # Use beam search to improve coherence and length
        early_stopping=True
    )
    return corrected_text[0]['generated_text']


# Виконання основної програми
if __name__ == "__main__":
    print("=== Результат автокорекції ===")
    text = """Hello, everybody. Now I am gonna tell you how the app works. So, basically, user creates a meeting, or connects to the existing one. In the process of meeting user starts recording of the meeting. After meeting is finished, or if the user stops the recording, audiofile of the meeting lands in the user's documents folder. 

    After completing the previous step, user can proceed to the app, see the meetings in his calendar, and press the update button to get the summaries of the available meetings records.
    The backend call starts the process where our app search for the audiofiles in the user's records folder. Also, before adding the audio to the queue, the app also checks if the records are related to the meetings in the user's calendar. If audio is present and it is related to the meeting in user's calendar, this meetings is added to the related db table, and also shows on the front end.

    Next step is to choose one of the available meetings, and get the summary of it. To do it, user presses on the pen icon near the name of the meeting, and make a backend call, passing the meeting id.

    Backend gets it, and using the info from db, gets the audiofile, and go through the chain of transformations:
    formatting, speech to text, autocorrect, punctuation check, sentimental analysis and summarization. After the process is completed, user can get all the info on the front end."""

    corrected_text = auto_correct_text(text)
    print("Відкоригований текст:", corrected_text)
