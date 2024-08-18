from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

note_tag_m2m = db.Table(
    "note_tag",
    sa.Column("note_id", sa.ForeignKey("notes.id"), primary_key=True),
    sa.Column("tag_id", sa.ForeignKey("tags.id"), primary_key=True),
)

class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), server_default=func.now())

class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    tags = db.relationship("Tag", secondary=note_tag_m2m, backref="notes")
    created_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
