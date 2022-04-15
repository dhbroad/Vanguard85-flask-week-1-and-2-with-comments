from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired

class CreateProductForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    img_url = StringField('Image URL', validators=[DataRequired()])
    description = StringField('Caption', validators=[DataRequired()])
    price = FloatField('Caption', validators=[DataRequired()])
    submit = SubmitField()
