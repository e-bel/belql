import logging

from flask import Flask, request, render_template, make_response
from werkzeug.middleware.proxy_fix import ProxyFix

from belql.utils import get_bel_edge_classes, get_bel_data, get_annotation_keys, get_annotation_values


app = Flask(__name__, static_url_path="", static_folder="static")
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

SECRET_KEY = 'a660ccbd5bf3d753cb50e20f707796995cb6e8e1372bdbdcddb3a29a9c9d2f6f'

logging.basicConfig(level=logging.DEBUG)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if "q_sub" in request.form:
            anno_key = request.form.get("q_anno_key")
            anno_val = request.form.get("q_anno_val")
            bel_query = f'{request.form.get("q_sub").strip()} {request.form.get("q_rel").strip()} {request.form.get("q_obj").strip()}'
            context = get_bel_data(bel_query, anno_key=anno_key, anno_val=anno_val)

            return make_response(context)

    return render_template(
        'index.html',
        additional_variables=get_bel_edge_classes(),
        anno_keys=get_annotation_keys(),
    )


@app.route("/anno", methods=["POST"])
def get_anno_vals():
    anno_key = request.form.get("anno_key")
    anno_vals = get_annotation_values(anno_key=anno_key)
    return anno_vals


if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")
