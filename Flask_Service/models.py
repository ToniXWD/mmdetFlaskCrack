from exts import db
from datetime import datetime

class EmailCaptureModel(db.Model):
    __tablename__="email_capture"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    email = db.Column(db.String(100),nullable=False,unique=True)
    capture = db.Column(db.String(10),nullable=False)
    create_time = db.Column(db.DateTime,default=datetime.now)