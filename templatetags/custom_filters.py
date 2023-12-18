from django import template

register = template.Library()

@register.filter(name='range_around_current')
def range_around_current(page_range, current, offset=2):
    total = page_range[-1]
    start = max(1, current - offset)
    end = min(total, current + offset)
    return range(start, end + 1)


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()