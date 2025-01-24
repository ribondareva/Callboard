from django import template
import re

register = template.Library()


@register.filter
def extract_video_id(value):
    # Для YouTube
    if "youtube.com" in value:
        match = re.search(r"v=([a-zA-Z0-9_-]+)", value)
        if match:
            return match.group(1)
    # Для Vimeo
    elif "vimeo.com" in value:
        match = re.search(r"vimeo.com/(\d+)", value)
        if match:
            return match.group(1)
    return value


@register.filter(name='regex_replace')
def regex_replace(value, arg):
    pattern, replacement = arg.split(',')
    return re.sub(pattern, replacement, value, count=1)