
import markdown


def mime_markdown(data):
    return markdown.markdown(data.decode("utf-8"))
