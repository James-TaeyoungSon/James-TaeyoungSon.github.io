from flask import Flask, render_template, request, send_file, session
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import io

app = Flask(__name__)
app.secret_key = "supersecretkey"

chrome_driver_path = "/workspaces/James-TaeyoungSon.github.io/chromedriver"

def get_selenium_driver(driver_path):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(executable_path=driver_path, options=options)

def search_show_rankings(start_date, end_date):
    url = "https://flixpatrol.com/top10/streaming/world/history/"
    driver = get_selenium_driver(chrome_driver_path)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    neflix = soup.select("body > div > div > table > tbody > tr > td > div > a")

    # 결과를 저장할 빈 데이터프레임 생성
    result_df = pd.DataFrame(columns=['Date', 'Rank', 'Title', 'Score'])

    for link in neflix:
        url = link.get("href")
        date = url.split('/')[-2]

        if url and 'top10/netflix/world' in url and start_date <= date <= end_date:
            url = f'https://flixpatrol.com{url}'

            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            tv_show_section = soup.select_one("#netflix-2")
            tv_shows = tv_show_section.select("tbody > tr")

            ranks = [int(show.select_one("td.table-td.w-12.font-semibold.text-right.text-gray-500").text.strip().split('.')[0]) for show in tv_shows]
            titles = [show.select_one("td.table-td > a > div:nth-child(2)").text.strip() for show in tv_shows]
            scores = [int(show.select_one("td.table-td.w-12.text-right.text-gray-400.font-semibold").text.strip()) for show in tv_shows]

            temp_df = pd.DataFrame({'Date': [date] * len(ranks), 'Rank': ranks, 'Title': titles, 'Score': scores})
            result_df = result_df.append(temp_df, ignore_index=True)

    driver.quit()
    return result_df

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        result_df = search_show_rankings(start_date, end_date)
        session['result_df'] = result_df.to_json()

        return render_template('search_results.html', search_results=result_df.to_html(), processing=False)
    return render_template('index.html')

@app.route('/download', methods=['GET', 'POST'])
def download():
    result_df = pd.read_json(session.get('result_df'))

    excel_file = io.BytesIO()
    excel_writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    result_df.to_excel(excel_writer, sheet_name='sheet1')
    excel_writer.save()
    excel_file.seek(0)

    return send_file(excel_file, attachment_filename="flixpatrol_top10_tv_shows.xlsx", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
