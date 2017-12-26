from log import init_log
init_log()

from flask import Flask, send_from_directory
from index import index_fn
# from apps.bre import static_bre_fn, api_bre_fn
from apps.codegen import static_codegen_fn, api_codegen_fn

app = Flask(__name__, static_url_path='', )


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('img', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/')
def index():
    return index_fn()


# @app.route('/bre')
# def bre():
#     return static_bre_fn()
#
#
# @app.route('/bre/api', methods=['POST'])
# def bre_api():
#     return api_bre_fn()

@app.route('/apps/codegen')
def condegen():
    return static_codegen_fn()


@app.route('/apps/codegen/api', methods=['POST'])
def codegen_api():
    return api_codegen_fn()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)