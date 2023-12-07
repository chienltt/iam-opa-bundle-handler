from flask import request

from src import init_app

app = init_app()


@app.route('/status', methods=['POST'])
def status():
    print("okok status", request.headers)

    return {}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
