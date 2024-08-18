import flask
import models
import forms
from datetime import datetime
app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://coe:CoEpasswd@localhost:5432/coedb"

models.init_app(app)

@app.route("/")
def index():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.title)
    ).scalars()
    return flask.render_template(
        "index.html",
        notes=notes,
    )
@app.route("/notes/create", methods=["GET", "POST"])
def notes_create():
    form = forms.NoteForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "notes-create.html",
            form=form,
        )

    db = models.db

    # สร้างออบเจ็กต์ Note โดยกำหนดวันที่ปัจจุบันให้กับ created_date และ updated_date
    note = models.Note(
        title=form.title.data,
        description=form.description.data,
        created_date=datetime.now(),  # ใช้วันที่ปัจจุบัน
        updated_date=datetime.now()   # ใช้วันที่ปัจจุบัน
    )

    # จัดการฟิลด์ tags แยกออกมา
    for tag_name in form.tags.data:
        print(f"Processing tag: {tag_name}")  # ตรวจสอบว่า tag_name คืออะไร
        tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
            .scalars()
            .first()
        )

        if not tag:
            tag = models.Tag(name=tag_name)
            db.session.add(tag)

        note.tags.append(tag)

    db.session.add(note)
    db.session.commit()

    return flask.redirect(flask.url_for("index"))
@app.route("/notes/edit/<int:note_id>", methods=["GET", "POST"])
def notes_edit(note_id):
    db = models.db
    note = db.session.execute(db.select(models.Note).where(models.Note.id == note_id)).scalars().first()

    if not note:
        return flask.redirect(flask.url_for("index"))

    form = forms.NoteForm(obj=note)
    if form.validate_on_submit():
        note.title = form.title.data
        note.description = form.description.data
        note.updated_date = datetime.now()

        # จัดการฟิลด์ tags
        note.tags = []
        for tag_name in form.tags.data:
            tag = db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name)).scalars().first()
            if not tag:
                tag = models.Tag(name=tag_name)
                db.session.add(tag)
            note.tags.append(tag)

        db.session.commit()
        return flask.redirect(flask.url_for("index"))

    return flask.render_template("notes-edit.html", form=form, note=note)

@app.route("/tags/edit/<int:tag_id>", methods=["GET", "POST"])
def tags_edit(tag_id):
    db = models.db
    tag = db.session.execute(db.select(models.Tag).where(models.Tag.id == tag_id)).scalars().first()

    if not tag:
        return flask.redirect(flask.url_for("index"))

    form = forms.TagForm(obj=tag)
    if form.validate_on_submit():
        tag.name = form.name.data
        db.session.commit()
        return flask.redirect(flask.url_for("index"))

    return flask.render_template("tags-edit.html", form=form, tag=tag)

@app.route("/notes/delete/<int:note_id>", methods=["POST"])
def notes_delete(note_id):
    db = models.db
    note = db.session.execute(db.select(models.Note).where(models.Note.id == note_id)).scalars().first()

    if note:
        db.session.delete(note)
        db.session.commit()

    return flask.redirect(flask.url_for("index"))

@app.route("/tags/delete/<int:tag_id>", methods=["POST"])
def tags_delete(tag_id):
    db = models.db
    tag = db.session.execute(db.select(models.Tag).where(models.Tag.id == tag_id)).scalars().first()

    if tag:
        db.session.delete(tag)
        db.session.commit()

    return flask.redirect(flask.url_for("index"))


@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
        .scalars()
        .first()
    )
    if not tag:
        return flask.redirect(flask.url_for("index"))

    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars()

    return flask.render_template(
        "tags-view.html",
        tag_name=tag_name,
        notes=notes,
        tag=tag  # ส่งตัวแปร `tag` ไปยังเทมเพลต
    )


if __name__ == "__main__":
    app.run(debug=True, port=1234)
