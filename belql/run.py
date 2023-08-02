import logging

from flask import Flask, request, render_template, make_response, jsonify

from belql.utils import get_bel_edge_classes, get_bel_data, get_annotation_keys, get_annotation_values


app = Flask(__name__)
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024
app.static_folder = "static"

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
        'template.html',
        additional_variables=get_bel_edge_classes(),
        anno_keys=get_annotation_keys(),
    )


@app.route("/anno", methods=["POST"])
def get_anno_vals():
    anno_key = request.form.get("anno_key")
    anno_vals = get_annotation_values(anno_key=anno_key)
    return anno_vals


if __name__ == '__main__':
    app.run(debug=True, port=5001, host="0.0.0.0")
