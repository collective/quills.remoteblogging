from zope.interface import Interface


class IReadableMetaWeblogAPI(Interface):
    """
    """

    def getPost(postid, username, password):
        """Return a post as struct.
        """

    def getCategories(blogid, username, password):
        """Returns a struct containing description, htmlUrl and rssUrl.
        """

    def getRecentPosts(blogid, username, password, num):
        """Return 'num' recent posts to specified blog,

        returns a struct: The three basic elements are title, link and
        description. For blogging tools that don't support titles and links,
        the description element holds what the Blogger API refers to as
        'content'.
        """

    def getUsersBlogs(appkey, username, password):
        """TODO: getUsersBlogs.
        """
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

    def getUserInfo(appkey, username, password):
        """Returns returns a struct containing userinfo

        userid, firstname, lastname, nickname, email, and url.
        """

    #def entryStruct(obj):
    #    """Returns the entry as a struct. Called by getRecentPosts and getPost.
    #    """


class IAddableMetaWeblogAPI(Interface):
    """
    """
    
    def newPost(blogid, username, password, struct, publish):
        """Create a new entry - either in draft folder or directly in archive.
        """


class IEditableMetaWeblogAPI(Interface):
    """
    """

    def editPost(postid, username, password, struct, publish):
        """Implement MetaWeblog editPost.
        """

    def deletePost(postid, username, password, publish):
        """Returns true on success, fault on failure.
        """


class IMetaWeblogAPI(IReadableMetaWeblogAPI,
                     IAddableMetaWeblogAPI,
                     IEditableMetaWeblogAPI):
    """
    """

    #def extractDescriptionFromBody(body):
    #    """If the body contains a leading <h2> element, this is extraced as its
    #    description. The body without that element is then returned as new body.
    #    """


