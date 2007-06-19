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
from quills.remoteblogging.interfaces import IMetaWeblogAPI
from quills.core.interfaces import IWeblog, IWeblogEntry


class MetaWeblogAPI(BrowserView):
    """http://www.xmlrpc.com/metaWeblogApi
    """

    implements(IMetaWeblogAPI)

    excerptExtractor = re.compile("<h2 class=[\"|']QuillsExcerpt[\"|']>(.*)</h2>")
    divExtractor = re.compile("<div>((.*\n)*.*)</div>")

    def newPost(self, blogid, username, password, struct, publish):
        """See IMetaWeblogAPI.
        """
        weblog = IWeblog(self._getByUID(blogid))
        # preparing the ingredients:
        body  = struct.get('description', struct.get('Description'))
        # if the body contains an excerpt, we extract it:
        excerpt, body = self.extractDescriptionFromBody(body)
        title = struct.get('title', struct.get('Title'))
        topics = struct.get('categories', struct.get('Categories'))
        effective_date = getEffectiveDate(struct)
        entry = weblog.addEntry(title=title,
                                excerpt=excerpt,
                                text=text,
                                topics=topics,)
        if publish:
            wf_tool = getToolByName(self.context, 'portal_workflow')
            entry.setEffectiveDate(effective_date)
            wf_tool.doActionFor(entry, 'publish')
        return self.getUIDFor(entry)

    def editPost(self, postid, username, password, struct, publish):
        """See IMetaWeblogAPI.
        """
        entry = IWeblogEntry(self._getByUID(postid))
        body  = struct.get('description', struct.get('Description'))
        excerpt, body = self.extractDescriptionFromBody(body)
        title = struct.get('title', struct.get('Title'))
        topics = struct.get('categories', struct.get('Categories'))
        entry.edit(title, excerpt, text, topics)
        if publish:
            #effective_date = getEffectiveDate(struct)
            #entry.setEffectiveDate(effective_date)
            wf_tool = getToolByName(self.context, 'portal_workflow')
            entry.setEffectiveDate(DateTime.DateTime())
            wf_tool.doActionFor(entry, 'publish')
        return True

    def getPost(self, postid, username, password):
        """See IMetaWeblogAPI.
        """
        entry = IWeblogEntry(self._getByUID(postid))
        return self.entryStruct(entry)

    def getCategories(self, blogid, username, password):
        """See IMetaWeblogAPI.
        """
        weblog = IWeblog(self._getByUID(blogid))
        topics = weblog.getTopics()
        # 2005-12-13 tomster:
        # this is kind of ugly: according to the RFC we should return an array
        # of structs, but according to http://typo.leetsoft.com/trac/ticket/256
        # (at least) MarsEdit and ecto expect an array of strings containing the
        # category id.
        # Nigel: To accomidate ecto and other blogging clients we are going to
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
        entry = IWeblogEntry(self._getByUID(postid))
        weblog = entry.getParentWeblog()
        weblog.deleteEntry(entry.getId())
        return True

    def getRecentPosts(self, blogid, username, password, num):
        """See IMetaWeblogAPI.
        """
        weblog = IWeblog(self._getByUID(blogid))
        entries = weblog.getEntries(max=20)
        return [self.entryStruct(entry) for entry in entries]

    def getUsersBlogs(self, appkey, username, password):
        """See IMetaWeblogAPI.
        """
        #catalog = getToolByName(self, 'portal_catalog')
        #results = catalog(meta_type='Weblog', Creator=username)
        #blogs = []
        #for item in results:
        #    o = item.getObject()
        #    blogs.append(
        #            {'url': o.absolute_url(),
        #             'blogid' : o.UID(),
        #             'blogName' : o.title_or_id()}
        #            )
        # This method returns a list with details for *only* the weblog
        # instance that it is being called through.  The previous
        # implementation (commented out above) searched for all weblogs
        # across the portal and returned them.  However, this causes
        # problems with multi-user blogs - there can only be one 'creator' -
        # and doesn't make a lot of sense, to my mind.  If/when we
        # componentise this code into a Five-ish view, it should be
        # possible to implement a getUsersBlogs for the portal root object
        # that *does* return all weblogs within the portal.  Until that day
        # users will simply need to know the URL of the weblogs that they
        # wish to work with and set their remote blogging client
        # appropriately.
        parent_blog = self.context
        blogs = []
        blogs.append(
            {'url': parent_blog.absolute_url(),
             'blogid' : parent_blog.UID(),
             'blogName' : parent_blog.title_or_id(),
            }
        )
        return blogs

    def getUserInfo(self, appkey, username, password):
        """See IMetaWeblogAPI.
        """
        membership = getToolByName(self.context, 'portal_membership')
        info = {'name'      : 'no name',
                'email'     : 'no email',
                'userid'    : 'no user id',
                'firstname' : 'no first name',
                'lastname'  : 'no last name',
                'url'       : 'no url',}
        member = membership.getAuthenticatedMember()
        if member:
            for key,value in info.items():
                info[key] = getattr(member, key, None) or value
        return info

    def entryStruct(self, obj):
        """See IMetaWeblogAPI.
        """
        # description is used here as container for the full entry, including
        # the excerpt. the excerpt is inserted as <h2> element. The whole
        # description is wrapped in a <div> to ensure validity of the resulting
        # HTML and feeds.
        text = obj.getText()
        needToWrap = not text.startswith("<div>")
        if needToWrap:
            body = "<div>\n"
        else:
            body = ""
        excerpt = obj.getExcerpt()
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
        struct = {
            'postid': self._getUIDFor(obj),
            'dateCreated': obj.effective(), # XXX This isn't in an interface!
            'title': obj.Title(),
            'description' : body,
            'categories' : [topic.getId() for topic in obj.getTopics()],
            'link' : self.getArchiveURLFor(obj)
        }
        return struct

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

    def _getByUID(self, uid):
        if uid=='0' or uid=='' or uid is None:
            return self.context
        uid_catalog = getToolByName(self.context, 'uid_catalog')
        lazy_cat = uid_catalog(UID=uid)
        obj = lazy_cat[0].getObject()
        return obj

    def _getUIDFor(self, obj):
        return obj.UID()


def getEffectiveDate(struct):
    """Extract the effective date from the struct, or return a default
    value.
    """
    ed = struct.get('pubDate',
        struct.get('pubdate',
            None)
    )
    if ed is None:
        ed = struct.get('datecreated',
            struct.get('dateCreated',
            DateTime.DateTime())
        )
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

