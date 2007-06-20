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
        """XXX
        """

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


class IUserManager(Interface):

    def getWeblogsForUser(user_id):
        """Return a sequence of dictionaries for each of the weblogs that
        `user_id' has access to.
            [
                {'url': parent_blog.absolute_url(),
                 'blogid' : parent_blog.UID(),
                 'blogName' : parent_blog.title_or_id(),
                },
            ]
        """

    def getUserInfo(user_id):
        """Return a dictionary of details for `user_id'.
            info = {'name'      : 'no name',
                    'email'     : 'no email',
                    'userid'    : 'no user id',
                    'firstname' : 'no first name',
                    'lastname'  : 'no last name',
                    'url'       : 'no url',}
        """


class IUIDManager(Interface):
    """
    """

    def getByUID(uid):
        """
        """

    def getUIDFor(obj):
        """
        """

    def getUID():
        """
        """
