from transformers import pipeline

summariser = pipeline("summarization", model="t5-small", tokenizer="t5-small")

def summarise_headlines(headlines):
    combined = ". ".join(headlines)
    input_text = "summarize: " + combined
    summary = summariser(input_text, max_length=60, min_length=20, do_sample=False)
    return summary[0]['summary_text'].strip().split(". ")
