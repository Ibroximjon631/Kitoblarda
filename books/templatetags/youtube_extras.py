from django import template
import re

register = template.Library()

def extract_youtube_id(url):
    # Standart, youtu.be, shorts va boshqa formatlar uchun universal regex
    patterns = [
        r'(?:v=|be/|embed/|shorts/)([\w-]{11})',  # asosiy formatlar
        r'youtube\.com/shorts/([\w-]{11})',       # shorts uchun
        r'youtube\.com/watch\?.*v=([\w-]{11})',  # watch?v= uchun
        r'youtu\.be/([\w-]{11})',                 # youtu.be uchun
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ''

@register.filter
def youtube_id(url):
    return extract_youtube_id(url) 