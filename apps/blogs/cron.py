import cronjobs
from django.conf import settings
from blogs.tasks import parse_feed
from blogs.models import BlogEntry
import commonware.log
import funfactory.log_settings  # Magic voodoo required to make logging work.

log = commonware.log.getLogger('ig.cron')


@cronjobs.register
def update_site_feeds():
    ids = []
    feeds = getattr(settings, 'SITE_FEED_URLS', None)
    for page, feed_url in feeds.iteritems():
        log.info('Importing articles for %s from %s' % (page, feed_url))
        parsed = parse_feed(feed_url, page)
        ids.extend(parsed)
    BlogEntry.objects.exclude(id__in=ids).delete()
