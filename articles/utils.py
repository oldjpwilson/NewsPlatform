import random
import string
import urllib.parse
from django.utils.text import slugify


def unique_string_generator(size=5, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def create_slug(instance, new_slug=None):
    if not new_slug:
        slug = slugify(instance.title)
    else:
        slug = new_slug
    Klass = instance.__class__
    qs = Klass.objects.filter(slug=slug).order_by('-id')
    if qs.exists():
        string_unique = unique_string_generator()
        newly_created_slug = slug + f"-{string_unique}"
        return create_slug(instance, new_slug=newly_created_slug)
    return slug


def generate_twitter_share_link(request, article):
    query = f"{article.title} by {article.channel.name} {request.build_absolute_uri()}"
    encode_query = urllib.parse.quote(query)
    twitter_url = f"https://twitter.com/intent/tweet?text={encode_query}"
    return twitter_url


def generate_facebook_share_link(request, article):
    app_id = '542599432471018'
    query = f'{request.build_absolute_uri()}'
    redirect_uri = 'https%3A%2F%2Fmedium.com%2Fm%2Ffacebook%2Fclose'
    encode_query = urllib.parse.quote(query)
    encoded_redirect = urllib.parse.quote(redirect_uri)
    facebook_url = f'https://www.facebook.com/v2.9/dialog/share?app_id={app_id}&href={encode_query}&display=page&redirect_uri={encoded_redirect}'
    return facebook_url


def generate_whatsapp_share_link(request, article):
    url_encoded_message = urllib.parse.quote(
        f"{article.title} by {article.channel.name} {request.build_absolute_uri()}")
    whatsapp_url = f'https://wa.me/?text={url_encoded_message}'
    return whatsapp_url


def generate_share_links(request, article):
    links = [
        {
            'icon_class': 'fab fa-twitter',
            'link': generate_twitter_share_link(request, article)
        },
        # {
        #     'icon_class': 'fab fa-facebook-f',
        #     'link': generate_facebook_share_link(request, article)
        # },
        # {
        #     'icon_class': 'fab fa-whatsapp',
        #     'link': generate_whatsapp_share_link(request, article)
        # }
    ]
    return links
