from flask import Flask, render_template, request, url_for, flash, redirect, escape
from sqlalchemy import text, select
from sqlalchemy.orm import Session
import base64
from src.db_func import insert_into_tables, print_all_table, build_select_statement
from src.gmail_func import gmail_authenticate, search_messages, generate_data_from_msgs, data_extract_keyword
from database import db_session, init_db, engine

app = Flask(__name__)
data = []


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/')
def home():
    # conn = get_db_connection()
    # posts = conn.execute('SELECT * FROM posts').fetchall()
    # conn.close()
    return render_template('home.html')


@app.route('/greet')
def greet():  # http://127.0.0.1:8000/greet?name=aa
    name = request.args['name']
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title></title>
    </head>
    <body>
        <h1>Hi {}</h1>
    </body>
    </html>'''.format(escape(name))


@app.route('/load_mails', methods=('GET', 'POST'))
def load_mails():
    global data
    if request.method == 'POST':
        if 'get-emails' in request.form:
            keyword = request.form['keyword']
            date_after = request.form['date_after']
            date_before = request.form['date_before']
            email_from = request.form['email_from']
            email_to = request.form['email_to']

            query = ""
            if keyword:
                query += f"{keyword} "
            if date_after:
                query += f"after:{date_after} "
            if date_before:
                query += f"before:{date_before} "
            if email_from:
                query += f"from:{email_from} "
            if email_to:
                query += f"to:{email_to} "

            results = search_messages(service, query)
            print(f"Found {len(results)} results.")
            data = []
            data = generate_data_from_msgs(service, results)
            print(data)
            data_extract_keyword(data)
            flash(f'Found {len(results)} matching mails!')
            return render_template('raw_mail_list.html', emails=data)
        elif 'confirm-emails' in request.form:
            # for each email matched, read it (output plain/text to console & save HTML and attachments)
            inserted_data = []
            for name in list(request.form.keys()):
                if name.startswith('mail'):
                    num = int(name[4:])
                    row = data[num]
                    row.pop('id')
                    inserted_data.append(row)
            data = []
            with Session(engine) as session:
                num_succeed = insert_into_tables(session, inserted_data)
                flash(f"You've successfully added {num_succeed} new mails!")  # info, error, warning
                # print_all_table(session)
                return redirect(url_for('load_mails'))

    return render_template('load_mails.html')


@app.route('/search_mails')
def search_mails():
    # return redirect(url_for('mail_list', encoded_sql='None'))
    return redirect(url_for('mail_list'))


def mail_search_text(sql_request):
    with Session(engine) as session:
        mails = session.execute(text(sql_request)).fetchall()
    return mails


def mail_search_statement(query):
    with Session(engine) as session:
        mails = session.execute(query).fetchall()
    return mails


@app.route('/mail_list_text', defaults={'encoded_sql': None}, methods=['GET', 'POST'])
@app.route('/mail_list_text/<encoded_sql>/', methods=('GET', 'POST'))
def mail_list_text(encoded_sql):
    if request.method == 'POST':
        sql_request = request.form['sql_request']
        # encoded_sql = base64.b64encode(bytes(sql_request, 'utf-8'))
        encoded_sql = sql_request.replace(' ', '1')
        return redirect(url_for('mail_list', encoded_sql=encoded_sql))
    # sql_request = encoded_sql.decode('utf-8')
    if encoded_sql is None:
        mails = []
    else:
        sql_request = encoded_sql.replace('1', ' ')
        mails = mail_search_text(sql_request)
    return render_template('mail_list_text.html', emails=mails)


@app.route('/mail_list/', methods=('GET', 'POST'))
def mail_list():
    if request.method == 'POST':
        keyword = request.form['keyword']
        date_after = request.form['date_after']
        date_before = request.form['date_before']
        email_from = request.form['email_from']
        email_to = request.form['email_to']
        query = "?"
        if email_from:
            query += f"fr={email_from}&"
        if email_to:
            query += f"to={email_to}&"
        if date_before:
            query += f"be={date_before}&"
        if date_after:
            query += f"af={date_after}&"
        if keyword:
            query += f"ke={keyword}&"
        query = query[:-1]
        return redirect(f'/mail_list/{query}')
    filters = request.args.to_dict()
    query = build_select_statement(filters)
    mails = mail_search_statement(query)
    return render_template('mail_list.html', emails=mails)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    init_db()
    service = gmail_authenticate()
    app.run(host='0.0.0.0', port='8000', debug=True)