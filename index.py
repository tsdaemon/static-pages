from flask import render_template

app_list = [
    {
        'name': 'Binary relation extractor',
        'description': 'BRE solved for Ukrainian for one type of relations - "parent of".',
        'href': '/bre'
    },
    {
        'name': 'Description to code translation',
        'description': 'Neural model for a code generation from a text description.',
        'href': '/codegen'
    }
]


def index_fn():
    return render_template('index.html', title='Application list', apps=app_list)
