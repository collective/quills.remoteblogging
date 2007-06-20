# Standard library imports
import re

# Zope imports
import DateTime
from Products.Five import BrowserView
from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

# CMF imports
from Products.CMFCore.utils import getToolByName

# Plone imports
from plone.i18n.normalizer.interfaces import IIDNormalizer

# Local imports
from quills.core.interfaces import IWeblog, IWeblogEntry, IWorkflowedWeblogEntry
from quills.remoteblogging.interfaces import IMetaWeblogAPI, IUserManager
from quills.remoteblogging.interfaces import IUIDManager
from quills.remoteblogging.utils import CaselessDict


class MetaWeblogAPI(BrowserView):
    """http://www.xmlrpc.com/metaWeblogApi
    """

    implements(IMetaWeblogAPI)

    def newPost(self, blogid, username, password, struct, publish):
        """See IMetaWeblogAPI.
        """
        struct = CaselessDict(struct)
        weblog = IUIDManager(self.context).getByUID(blogid)
        weblog = IWeblog(weblog)
        # preparing the ingredients:
        body  = struct.get('description')
        # if the body contains an excerpt, we extract it:
        excerpt, body = self.extractDescriptionFromBody(body)
        title = struct.get('title')
        topics = struct.get('categories')
        entry = weblog.addEntry(title=title,
                                excerpt=excerpt,
                                text=text,
                                topics=topics,)
        if publish:
            pubdate = getPublicationDate(struct)
            IWorkflowedWeblogEntry(entry).publish(pubdate)
        return self.getUIDFor(entry)

    def editPost(self, postid, username, password, struct, publish):
        """See IMetaWeblogAPI.
        """
        struct = CaselessDict(struct)
        entry = IUIDManager(self.context).getByUID(postid)
        entry = IWeblogEntry(entry)
        body  = struct.get('description')
        excerpt, body = self.extractDescriptionFromBody(body)
        title = struct.get('title')
        topics = struct.get('categories')
        entry.edit(title, excerpt, text, topics)
        if publish:
            pubdate = getPublicationDate(struct)
            IWorkflowedWeblogEntry(entry).publish(pubdate)
        return True

    def getPost(self, postid, username, password):
        """See IMetaWeblogAPI.
        """
        entry = IUIDManager(self.context).getByUID(postid)
        entry = IWeblogEntry(entry)
        return self.entryStruct(entry)

    def getCategories(self, blogid, username, password):
        """See IMetaWeblogAPI.
        """
        weblog = IUIDManager(self.context).getByUID(blogid)
        weblog = IWeblog(weblog)
        topics = weblog.getTopics()
        # 2005-12-13 tomster:
        # this is kind of ugly: according to the RFC we should return an array
        # of structs, but according to http://typo.leetsoft.com/trac/ticket/256
        # (at least) MarsEdit and ecto expect an array of strings containing the
        # category id.
        # Nigel: To accommodate ecto and other blogging clients we are going to
        # do this test to decide what format the topics should be returned in
        useragent = self.request['HTTP_USER_AGENT']
        if "ecto" in useragent or "Mars" in useragent:
            #self.plone_log("MetaWeblogAPI", "Using ecto/MarsEdit hack")
            categories = [topic.getId() for topic in topics]
        else:
            categories = []
            for topic in topics:
                 categories.append(
                     {'description' : topic.getId(),
                      'htmlUrl' : topic.absolute_url(),
                      'rssUrl' : '%s/rss.xml' % topic.absolute_url(),
                     })
        return categories

    def deletePost(self, postid, username, password, publish):
        """See IMetaWeblogAPI.
        """
        entry = IUIDManager(self.context).getByUID(postid)
        entry = IWeblogEntry(entry)
        weblog = entry.getParentWeblog()
        weblog.deleteEntry(entry.getId())
        return True

    def getRecentPosts(self, blogid, username, password, num):
        """See IMetaWeblogAPI.
        """
        weblog = IUIDManager(self.context).getByUID(blogid)
        weblog = IWeblog(weblog)
        entries = weblog.getEntries(max=20) # XXX 20 could be configurable.
        return [self.entryStruct(entry) for entry in entries]

    def getUsersBlogs(self, appkey, username, password):
        """See IMetaWeblogAPI.
        """
        app = IUIDManager(self.context).getByUID(appkey)
        return IUserManager(app).getWeblogsForUser(username)

    def getUserInfo(self, appkey, username, password):
        """See IMetaWeblogAPI.
        """
        app = IUIDManager(self.context).getByUID(appkey)
        return IUserManager(app).getUserInfo(username)

    def entryStruct(self, entry):
        """See IMetaWeblogAPI.
        """
        # description is used here as container for the full entry, including
        # the excerpt. the excerpt is inserted as <h2> element. The whole
        # description is wrapped in a <div> to ensure validity of the resulting
        # HTML and feeds.
        text = entry.getText()
        needToWrap = not text.startswith("<div>")
        if needToWrap:
            body = "<div>\n"
        else:
            body = ""
        excerpt = entry.getExcerpt()
        if excerpt is not None and excerpt != '':
            excerpt = '<h2 class="QuillsExcerpt">%s</h2>' % excerpt
            if needToWrap:
                body += excerpt + text
            else:
                # if there already exists a wrapping div, we need to inject
                # the excerpt inside of that, rather than just prepending it to
                # the body.
                body += '<div>%s%s</div>' % (excerpt, self.divExtractor.split(text)[1])
        else:
            body += text
        if needToWrap:
            body += "\n</div>"
        # Lookup a view for the entry so that we can figure out its archive URL.
        weview = getMultiAdapter((entry, self.request), u'weblogentry_view')
        struct = {
            'postid': IUIDManager(entry).getUID(),
            'dateCreated': entry.getPublicationDate(),
            'title': entry.Title(),
            'description' : body,
            'categories' : [topic.getId() for topic in entry.getTopics()],
            'link' : weview.getArchiveURLFor(entry)
        }
        return struct

    excerptExtractor = re.compile("<h2 class=[\"|']QuillsExcerpt[\"|']>(.*)</h2>")
    divExtractor = re.compile("<div>((.*\n)*.*)</div>")

    def extractDescriptionFromBody(self, body):
        """If the body contains a leading <h2> element, this is extraced as its
        description. The body without that element is then returned as new body.
        """
        excerpt = self.excerptExtractor.search(body)
        if excerpt == None:
            return "", body
        # Use the regex to get the h2-element string
        excerptString = excerpt.groups()[0]
        # Assuming, that there is only one excerpt element (which is why we're
        # using 'id' rather than 'class') we can now return the a leading,
        # opening <div> plus the second element of the split as body: re
        body_parts = self.excerptExtractor.split(body)
        strippedBody = body_parts[0] + body_parts[2]
        return excerptString, strippedBody


def getPublicationDate(struct):
    """Extract the effective date from the struct, or return a default
    value.
    """
    ed = struct.get('pubdate', struct.get('datecreated'))
    # Due to strange developments in Zope2.9 resp. xmlrpclib we need to parse
    # the XMLRPC-DateTime object's string representation and then construct a
    # 'proper' DateTime instance from a string assembled from those parsed bits.
    try:
        val = ed.value
        datetime_string = "%s-%s-%s%s" % (val[0:4], val[4:6], val[6:8], val[8:])
        return DateTime.DateTime(datetime_string)
    except AttributeError:
        # We obviously didn't receive a xmlrpclib DateTime instance, so we
        # can return the default unchanged (as it already is a Zope.DateTime
        # instance):
        return ed

