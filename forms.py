from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField
from wtforms.validators import DataRequired

class DateForm(FlaskForm):
    start_date = DateField("시작일을 입력하세요 (예: 2023-07-10):", validators=[DataRequired()])
    end_date = DateField("종료일을 입력하세요 (예: 2023-07-16):", validators=[DataRequired()])
    submit = SubmitField("검색")