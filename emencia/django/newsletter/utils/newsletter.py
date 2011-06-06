"""Utils for newsletter"""
from BeautifulSoup import BeautifulSoup
from django.core.urlresolvers import reverse

from emencia.django.newsletter.models import Link


def body_insertion(content, insertion, end=False, insertion_id=None):
    """Insert an HTML content into the body HTML node"""
    if not content.startswith('<body'):
        content = '<body>%s</body>' % content
    soup = BeautifulSoup(content)

    inserted = False

    if insertion_id:
        element = soup.find('', attrs={'id':insertion_id})
        if element:
            element.contents = []
            element.append(insertion)
            inserted = True

    if not inserted:
        if end:
            soup.body.append(insertion)
        else:
            soup.body.insert(0, insertion)
    return soup.prettify()


def track_links(content, context):
    """Convert all links in the template for the user
    to track his navigation"""
    if not context.get('uidb36'):
        return content

    soup = BeautifulSoup(content)
    for link_markup in soup('a'):
        if link_markup.get('href') and \
               'no-track' not in link_markup.get('rel', ''):
            link_href = link_markup['href']
            link_title = link_markup.get('title', link_href)
            link, created = Link.objects.get_or_create(url=link_href,
                                                       defaults={'title': link_title})
            link_markup['href'] = 'http://%s%s' % (context['domain'], reverse('newsletter_newsletter_tracking_link',
                                                                              args=[context['newsletter'].slug,
                                                                                    context['uidb36'], context['token'],
                                                                                    link.pk]))
    return soup.prettify()
