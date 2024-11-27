from transformers import pipeline

# Створюємо інструменти для виправлення граматики та стилю і для аналізу сентименту
corrector = pipeline("text2text-generation", model="t5-small")
sentiment_analyzer = pipeline("sentiment-analysis")


def auto_correct_text(input_text, chunk_size=512):
    """
    Використовує модель ШІ для автозаміни слів у вхідному тексті, щоб покращити його читабельність та стиль.

    Parameters:
    input_text (str): Текст для автозаміни.
    chunk_size (int): Максимальна кількість токенів для обробки (параметр для обмеження на кількість символів).

    Returns:
    str: Відкоригований текст.
    """
    # Розбиваємо вхідний текст на частини, кожна з яких містить не більше chunk_size токенів
    corrected_text = ""
    for i in range(0, len(input_text), chunk_size):
        chunk = input_text[i:i + chunk_size]
        # Генеруємо виправлений текст для кожної частини
        corrected_chunk = corrector(
            f"{chunk}",
            max_length=chunk_size,  # Максимальна довжина кожної частини
            min_length=100,  # Мінімальна довжина для кожної частини
            num_beams=5,  # Кількість проміжних варіантів для пошуку
            early_stopping=True
        )
        corrected_text += corrected_chunk[0]['generated_text'] + " "

    return corrected_text.strip()


def analyze_sentiment(input_text):
    """
    Використовує модель ШІ для аналізу сентименту тексту.

    Parameters:
    input_text (str): Текст для аналізу сентименту.

    Returns:
    dict: Результат аналізу сентименту.
    """
    sentiment = sentiment_analyzer(input_text)
    return sentiment


# Виконання основної програми
if __name__ == "__main__":
    print("=== Результат автокорекції ===")
    text = """I am absolutely thrilled with the results of the new app! It works flawlessly, and the interface is incredibly intuitive. I love how easy it is to schedule meetings and manage my calendar. The update feature is fantastic, and I can quickly get the summaries of all my meetings. This app has truly made my life easier, and I can't wait to use it even more. Highly recommend it to everyone!"""

    # Autocorrect the text
    corrected_text = auto_correct_text(text)
    print("Відкоригований текст:", corrected_text)

    # Analyze sentiment of the corrected text
    sentiment = analyze_sentiment(corrected_text)
    print("Аналіз сентименту:", sentiment)
