from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
import os
from bs4 import BeautifulSoup
import urllib.request
import requests
import pandas as pd
import openpyxl
from forms import DateForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'

def get_netflix_data(start_date, end_date):
    # 기존 코드에 적용된 부분입니다.
    # 함수 내부에 넣어 원하는 결과를 얻을 수 있습니다.

@app.route('/', methods=['GET', 'POST'])
def index():
    form = DateForm()
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        result_df = get_netflix_data(start_date, end_date)
        excel_file = f"netflix_{start_date}_{end_date}.xlsx"
        result_df.to_excel(excel_file, index=False)
        return send_from_directory('.', excel_file, as_attachment=True)
    return render_template('index.html', form=form)

if __name__ == "__main__":
    app.run()