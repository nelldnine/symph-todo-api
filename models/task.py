from google.appengine.ext import ndb
from models.board import Board

class Task(ndb.Model):
    title = ndb.StringProperty()
    description = ndb.TextProperty()
    status = ndb.StringProperty()
    board = ndb.KeyProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        task = {}
        task['id'] = self.key.id()
        task['title'] = self.title
        task['description'] = self.description
        task['status'] = self.status
        task['created'] = self.created.isoformat() + 'Z'
        task['updated'] = self.updated.isoformat() + 'Z'
        return task

    @classmethod
    def save(cls, **kwargs):
        if kwargs.get('id'):
            task = cls.get_by_id(int(kwargs['id']))
        else:
            task = cls()
        if kwargs.get('title'):
            task.title = kwargs['title']
        if kwargs.get('description'):
            task.description = kwargs['description']
        if kwargs.get('status'):
            task.status = kwargs['status']
        if kwargs.get('board'):
            task.board = ndb.Key(Board, int(kwargs['board']))
        task.put()
        return task

    @classmethod
    def get_board_tasks(cls, board_id):
        results = []
        board = ndb.Key(Board, int(board_id))
        query = cls.query(cls.board == board)
        tasks = query.fetch()
        for task in tasks:
            results.append(task.to_dict())
        return results
