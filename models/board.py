from google.appengine.ext import ndb
from models.user import User
from models.task import Task

class Board(ndb.Model):
    name = ndb.StringProperty()
    users = ndb.KeyProperty(repeated=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        board = {}
        board['id'] = self.key.id()
        board['name'] = self.name
        board['users'] = []
        for user in self.users:
            board['users'].append(user.id())
        board['created'] = self.created.isoformat() + 'Z'
        board['updated'] = self.updated.isoformat() + 'Z'
        return board

    def add_user(self, user_id):
        user = ndb.Key(User, int(user_id))
        self.users.append(user)
        self.put()
        return self

    def remove_user(self, user_id):
        user = ndb.Key(User, int(user_id))
        self.users.remove(user)
        self.put()
        return self

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
        query = query.order(-cls.updated)
        boards = query.fetch()
        for board in boards:
            results.append(board.to_dict())
        return results

    @classmethod
    def get_tasks(cls, board_id):
        results = []
        board = ndb.Key(cls, int(board_id))
        query = Task.query(Task.board == board)
        query = query.order(-Task.updated)
        tasks = query.fetch()
        for task in tasks:
            results.append(task.to_dict())
        return results
