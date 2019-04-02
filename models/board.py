from google.appengine.ext import ndb

class Board(ndb.Model):
    name = ndb.StringProperty()
    users = ndb.KeyProperty(repeated=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        board = {}
        board['id'] = self.key.id()
        board['name'] = self.name
        board['created'] = self.created.isoformat() + 'Z'
        board['updated'] = self.updated.isoformat() + 'Z'
        return board

    @classmethod
    def save(cls, **kwargs):
        if kwargs.get('id'):
            board = cls.get_by_id(int(kwargs['id']))
        else:
            board = cls()
        if kwargs.get('name'):
            board.name = kwargs['name']
        if kwargs.get('user_id'):
            user = ndb.Key(cls, int(kwargs['user_id']))
            board.users = [user]
        board.put()
        return board

    @classmethod
    def get_user_boards(cls, user_id):
        results = []
        user = ndb.Key(cls, int(user_id))
        query = cls.query(cls.users == user)
        boards = query.fetch()
        for board in boards:
            results.append(board.to_dict())
        return results

    @classmethod
    def add_user(cls, board_id, user_id):
        board = cls.get_by_id(int(board_id))
        user = ndb.Key(cls, int(user_id))
        board.users.append(user)
        board.put()
        return board

    @classmethod
    def remove_user(cls, board_id, user_id):
        board = cls.get_by_id(int(board_id))
        user = ndb.Key(cls, int(user_id))
        board.users.remove(user)
        board.put()
        return board
