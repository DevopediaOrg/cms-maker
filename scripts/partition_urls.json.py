import json


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


urls = []
with open("../urls.json", "r") as fp:
    urls = json.load(fp)

for index, chunk in enumerate(list(chunks(urls, 20))):
    with open("../resources/urls-" + str(index) + ".json", "w") as fp:
        json.dump(chunk, fp)
