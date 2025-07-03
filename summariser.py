from transformers import pipeline

# Load summarisation pipeline using T5-small (fast and free)
summariser = pipeline("summarization", model="t5-small", tokenizer="t5-small")

def summarise_headlines(headlines):
    combined = ". ".join(headlines)
    input_text = "summarize: " + combined
    summary = summariser(input_text, max_length=100, min_length=25, do_sample=False)
    return summary[0]['summary_text'].split(". ")
