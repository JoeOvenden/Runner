from django import template

register = template.Library()

@register.filter(name='range_around_current')
def range_around_current(page_range, current, offset=2):
    total = page_range[-1]
    start = max(1, current - offset)
    end = min(total, current + offset)
    return range(start, end + 1)
