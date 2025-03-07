from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response, request, abort
from sqlalchemy import asc, desc
from datetime import date
import requests
import json
import os
from dotenv import load_dotenv
from .goal_routes import validate_model


slack_token = os.environ.get('SLACK_TOKEN')
headers = {'Authorization': slack_token}

def post_to_slack(text, blocks=None):
    slack_data ={'channel': '#slack-bot-test-channel', 'text':text}
    requests.post('https://slack.com/api/chat.postMessage', headers=headers,
                    data=slack_data)

tasks_bp = Blueprint('tasks_bp', __name__, url_prefix='/tasks')


#Get Tasks: Getting Saved Tasks
@tasks_bp.route("", methods=["GET"])
def get_all_task():
    get_sorted = request.args.get("sort")

    if get_sorted == 'desc':
        all_tasks =Task.query.order_by(Task.title.desc())
    elif get_sorted == 'asc':
        all_tasks =Task.query.order_by(Task.title.asc())
    else:
        all_tasks = Task.query.all()

    task_response = [task.to_dict() for task in all_tasks]

    return (jsonify(task_response))


@tasks_bp.route("/<task_id>", methods=["GET"])
def handle_task(task_id):
    task = validate_model(Task,task_id)

    return{"task":task.to_dict()} 


@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()

    # guard clause
    if "title" not in request_body or "description" not in request_body:
        return {"details": "Invalid data"}, 400
    new_task= Task(
        title=request_body['title'], 
        description=request_body['description']
        )
    
    db.session.add(new_task)
    db.session.commit()

    return make_response(jsonify({'task': new_task.to_dict()}), 201)


@tasks_bp.route("/<task_id>", methods=["PUT"])
def edit_task(task_id):
    
    task = validate_model(Task,task_id)
    request_body = request.get_json()

    task.title=request_body["title"]
    task.description=request_body["description"]

    db.session.commit()

    return make_response(jsonify({'task': task.to_dict()}), 200)


@tasks_bp.route('/<task_id>/<complete>', methods=['PATCH'])
def patch_task_complete(task_id,complete):
    task = validate_model(Task,task_id)

    if complete == "mark_complete":
        task.completed_at = date.today()
        text = f"Someone just completed the task {task.title}"
        post_to_slack(text)
        
    elif complete == "mark_incomplete":
        task.completed_at = None

    db.session.commit()

    return make_response({'task': task.to_dict()}, 200)


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = validate_model(Task,task_id)

    db.session.delete(task)
    db.session.commit()

    return {"details": f'Task {task.id} "{task.title}" successfully deleted'}, 200

