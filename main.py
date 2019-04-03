#!/usr/bin/env python
# -*- coding: utf-8 -*-
import jwt
import logging
from functools import wraps
from flask import Flask, request, jsonify
from models.user import User
from models.board import Board
from models.task import Task
from secrets import SECRET

app = Flask(__name__)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if auth:
            try:
                payload = jwt.decode(auth.split()[-1], SECRET)
                logging.debug(payload)
                for key in payload:
                    logging.debug('{}: {}'.format(str(key), str(payload[key])))
                return f(*args, **kwargs)
            except Exception as e:
                logging.exception(e)
        return jsonify(code=401, message='Unauthorized'), 401
    return wrapper

@app.before_request
def before_req():
    try:
        body = request.get_json()
        if body:
            for key in body:
                if 'password' in key:
                    continue
                logging.debug('{}: {}'.format(str(key), str(body[key])))
    except Exception as e:
        logging.debug(e)

@app.route('/api/boards/<int:board_id>', methods=['GET', 'PUT'])
@app.route('/api/boards', methods=['GET', 'POST'])
@login_required
def boards(board_id=None):
    auth = request.headers.get('Authorization')
    user = jwt.decode(auth.split()[-1], SECRET)
    if request.method == 'POST':
        body = request.get_json()
        board = Board.save(name=body.get('name'), user_id=user['id'])
        return jsonify(board.to_dict())
    elif request.method == 'PUT':
        body = request.get_json()
        board = Board.save(id=board_id, name=body.get('name'))
        return jsonify(board.to_dict())
    if board_id:
        board = Board.get_by_id(board_id)
        return jsonify(board.to_dict())
    return jsonify(Board.get_user_boards(user['id']))

@app.route('/api/boards/<int:board_id>/users/<int:user_id>', methods=['PUT', 'DELETE'])
@login_required
def board_users(board_id, user_id):
    board = Board.get_by_id(board_id)
    if request.method == 'PUT':
        board = board.add_user(user_id)
    if request.method == 'DELETE':
        board = board.remove_user(user_id)
    return jsonify(board.to_dict())

@app.route('/api/boards/<int:board_id>/tasks/<int:task_id>', methods=['GET', 'PUT'])
@app.route('/api/boards/<int:board_id>/tasks', methods=['GET', 'POST'])
@login_required
def tasks(board_id, task_id=None):
    if request.method == 'POST':
        body = request.get_json()
        task = Task.save(
            title=body.get('title'),
            description=body.get('description'),
            status=body.get('status'),
            board=board_id
        )
        return jsonify(task.to_dict())
    elif request.method == 'PUT':
        body = request.get_json()
        task = Task.save(
            id=task_id,
            title=body.get('title'),
            description=body.get('description'),
            status=body.get('status')
        )
        return jsonify(task.to_dict())
    if task_id:
        task = Task.get_by_id(task_id)
        return jsonify(task.to_dict())
    tasks = Board.get_tasks(board_id)
    return jsonify(tasks)

@app.route('/api/register', methods=['POST'])
def register():
    body = request.get_json()
    user = User.save(
        name=body.get('name'),
        email=body.get('email'),
        password=body.get('password')
    )
    return jsonify(user.to_dict())

@app.route('/api/login', methods=['POST'])
def login():
    body = request.get_json()
    user = User.login(
        email=body.get('email'),
        password=body.get('password')
    )
    return jsonify(user)

@app.errorhandler(500)
def application_error(e):
    logging.exception(e)
    return jsonify(message='An error occured'), 500

@app.errorhandler(405)
def method_not_allowed(e):
    logging.exception(e)
    return jsonify(message='Method not allowed'), 405

@app.errorhandler(404)
def not_found(e):
    logging.exception(e)
    return jsonify(message='Resource not found'), 404
