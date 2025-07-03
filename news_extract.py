# Import required module
import newspaper

# Assign url
url = 'https://techcrunch.com/tag/ai/feed/'

# Extract web data
url_i = newspaper.Article(url="%s" % (url), language='en')
url_i.download()
url_i.parse()

# Display scrapped data
print(url_i.text)