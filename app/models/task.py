from app import db
# import json

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    # confirm null is default if task has not been completed
    completed_at = db.Column(db.DateTime, nullable=True)
    # is_complete = db.Column(db.Boolean) # check if needed
    goal_id = db.Column(db.Integer, db.ForeignKey("goal.id"),nullable=True)
    goal = db.relationship("Goal", back_populates="tasks")
    

    def to_dict(self):
        task_dict = {}
        task_dict["id"] = self.id
        task_dict["title"] = self.title
        task_dict["description"] = self.description
        # task_dict["is_complete"] = False
        if self.completed_at == None:
            task_dict["is_complete"] = False
        else:
            task_dict["is_complete"] = True
        if self.goal_id:
            task_dict["goal_id"]= self.goal_id
        return task_dict
