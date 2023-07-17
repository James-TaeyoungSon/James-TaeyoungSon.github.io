from bs4 import BeautifulSoup
import urllib.request
import requests
import pandas as pd
import openpyxl
from flask import Flask, request, send_file
from io import BytesIO

app = Flask(__name__)

@app.route("/netflix", methods=["POST"])
def netflix():
    url = "https://flixpatrol.com/top10/streaming/world/history/"
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    neflix = soup.select("body > div > div > table > tbody > tr > td > div > a")

    result_df = pd.DataFrame(columns=['Date', 'Rank', 'Title', 'Score'])

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'}

    for link in neflix:
        url = link.get("href")
        date = url.split('/')[-2]

        if url and 'top10/netflix/world' in url and start_date <= date <= end_date:
            url = f'https://flixpatrol.com{url}'

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            tv_show_section = soup.select_one("#netflix-2")
            tv_shows = tv_show_section.select("tbody > tr")

            ranks = [int(show.select_one("td.table-td.w-12.font-semibold.text-right.text-gray-500").text.strip().split('.')[0]) for show in tv_shows]
            titles = [show.select_one("td.table-td > a > div:nth-child(2)").text.strip() for show in tv_shows]
            scores = [int(show.select_one("td.table-td.w-12.text-right.text-gray-400.font-semibold").text.strip()) for show in tv_shows]

            temp_df = pd.DataFrame({'Date': [date] * len(ranks), 'Rank': ranks, 'Title': titles, 'Score': scores})
            result_df = result_df.append(temp_df, ignore_index=True)

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    result_df.to_excel(writer, index=False)
    writer.save()

    output.seek(0)
    return send_file(output, as_attachment=True, attachment_filename=f"netflix_{start_date}_{end_date}.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == "__main__":
    app.run(debug=True)