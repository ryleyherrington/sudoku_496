from google.appengine.ext import db

class Puzzle(db.Model):
    unsolved = db.StringProperty("Unsolved Puzzle")
    solved = db.UserProperty("Solved Puzzle")
    post_time = db.DateTimeProperty("Post time", auto_now_add=True)

