from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

#WTFORM to add to list STOCKS
class AddForm(FlaskForm):
    stock = StringField(label='name', validators=[DataRequired()])
    submit = SubmitField(label='Submit')
