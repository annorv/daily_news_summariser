from summariser import summarise_headlines

test_headlines = [
    "OpenAI launches new feature for ChatGPT agents",
    "UK invests £100 million into AI education programmes",
    "Researchers create ultra-fast AI image recognition model",
    "NVIDIA reveals next-generation AI GPUs",
    "Google announces new open-source AI safety toolkit"
]

summary = summarise_headlines(test_headlines)

print("🔍 Summary:")
for line in summary:
    print("•", line.strip())
