# Importing the necessary modules
from transformers import AutoTokenizer, AutoModelWithLMHead

# Defining the summarize_text function
def summarize_text(text):
    # Initializing tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained('t5-base')
    model = AutoModelWithLMHead.from_pretrained('t5-base', return_dict=True)

    # Tokenizing the text
    inputs = tokenizer.encode("summarize: " + text, return_tensors='pt', max_length=512, truncation=True)

    # Generating the summary
    outputs = model.generate(inputs, max_length=300, min_length=100, num_beams=4, early_stopping=True)

    # Decoding and cleaning the output
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return summary

# Test function
def test_summarize_text():
    text = """Hello, everybody. Now I am gonna tell you how the app works. So, basically, user creates a meeting, or connects to the existing one. In the process of meeting user starts recording of the meeting. After meeting is finished, or if the user stops the recording, audiofile of the meeting lands in the user's documents folder. 

    After completing the previous step, user can proceed to the app, see the meetings in his calendar, and press the update button to get the summaries of the available meetings records.
    The backend call starts the process where our app search for the audiofiles in the user's records folder. Also, before adding the audio to the queue, the app also checks if the records are related to the meetings in the user's calendar. If audio is present and it is related to the meeting in user's calendar, this meetings is added to the related db table, and also shows on the front end.

    Next step is to choose one of the available meetings, and get the summary of it. To do it, user presses on the pen icon near the name of the meeting, and make a backend call, passing the meeting id.

    Backend gets it, and using the info from db, gets the audiofile, and go through the chain of transformations:
    formatting, speech to text, autocorrect, punctuation check, sentimental analysis and summarization. After the process is completed, user can get all the info on the front end."""

    summary = summarize_text(text)
    print("Original Text:")
    print(text)
    print("\nGenerated Summary:")
    print(summary)

# Running the test function
if __name__ == "__main__":
    test_summarize_text()
