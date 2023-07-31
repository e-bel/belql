import logging

from flask import Flask, request, render_template, make_response

from belql.utils import get_bel_edge_classes, get_bel_data


app = Flask(__name__)
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024
app.static_folder = "static"

logging.basicConfig(level=logging.DEBUG)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        bel_query = f'{request.form.get("q_sub").strip()} {request.form.get("q_rel").strip()} {request.form.get("q_obj").strip()}'
        context = get_bel_data(bel_query)

        return make_response(context)

    return render_template('template.html', additional_variables=get_bel_edge_classes())


if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
