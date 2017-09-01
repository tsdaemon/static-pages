from flask import render_template

app_list = [
    {
        'name': 'Binary relation extractor',
        'description': 'BRE solved for Ukrainian for one type of relations - "parent of".',
        'href': '/bre'
    }
]


def index_fn():
    return render_template('index.html', title='Application list', apps=app_list)
