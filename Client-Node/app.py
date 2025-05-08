from flask import Flask, render_template, request, redirect, url_for, session
from QueueUtils import send_task, receive_task
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'n' not in session:
        session['n'] = 1

    crawl_results = []  # List of full results, one per task

    if request.method == 'POST':
        if 'add' in request.form:
            session['n'] += 1
            return redirect(url_for('index'))

        elif 'submit' in request.form:
            urls = request.form.getlist('url')
            depths = request.form.getlist('depth')

            for url, depth in zip(urls, depths):
                task = {'seed_url': url, 'depth': int(depth)}
                print(task)
                send_task('client_task', task)

            # Receive individual results for each task
            for d in depths:
                result = receive_task('client_result', block=True, timeout=100 * int(d))
                if result:
                    crawl_results.append(result)
                else:
                    crawl_results.append({
                        "seed_url": "timeout",
                        "pages": []
                    })

            results_json = ""
            for r in crawl_results:
                results_json += json_to_collapsible_html(r) + "<br><br>"

            session['n'] = 1  # Reset inputs after submission
            return render_template('index.html', n=session['n'], crawl_summary=[], crawl_results=results_json)

    # Default GET
    return render_template('index.html', n=session['n'], crawl_summary=[], crawl_results="")

def json_to_collapsible_html(data):
    html = ""

    if isinstance(data, dict):
        html += "<details open><summary>{}</summary><ul>".format("Object")
        for key, value in data.items():
            html += f"<li class='{key}'><strong>{key}</strong>: "
            if key in ("url", "seed_url"):
                html += f"<a href='{value}' target='_blank'>{value}</a>"
            elif key == "raw_html":
                if value:
                    html += render_template('popup.html', content=value)
                else:
                    html += "<i>&lt;raw_html omitted&gt;</i>"
            else:
                html += json_to_collapsible_html(value)
            html += "</li>"
        html += "</ul></details>"

    elif isinstance(data, list):
        html += "<details><summary>List [{} items]</summary><ul>".format(len(data))
        for item in data:
            html += "<li>" + json_to_collapsible_html(item) + "</li>"
        html += "</ul></details>"

    else:
        html += str(data)

    return html


if __name__ == '__main__':
    app.run(debug=True)
