from flask import Flask, Response, render_template, request, \
    make_response, redirect, abort
from flask_bootstrap import Bootstrap5

from backend import *

app = Flask(__name__)
app.secret_key = 'tO$&!|0wkamvVia0?n$NqIRVWOG'
bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)


@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


@app.route('/dashboard/overview')
def dashboard_overview():
    return render_template('bank.html')


@app.route('/dashboard/progress')
def dashboard_progress():
    bank = Bank()
    total = bank.total()
    required = 1000
    progressbar = round(total / required * 100)
    message = (f'Op dit moment hebben jullie {total} van de {required} '
               f'opgehaald!<br>Dat is {progressbar}%!<br>Ga zo door!')
    message = message.split('<br>')
    return render_template('progress.html', message=message,
                           progressbar=progressbar)


@app.route('/user/<identifier>', methods=["GET", "POST"])
def account(identifier):
    form = UpdateForm()
    bank = Bank()
    try:
        data = bank.get_account_by_id(identifier)[0]
        user = data[1]
        balance = data[2]
        if form.validate_on_submit():
            amount = form.amount.data
            admin_flag = request.cookies.get('admin')
            if admin_flag != '1':
                amount = -abs(int(amount))
            if form.choice.data == "modify":
                bank.modify_money(user, amount)
            else:
                bank.set_money(user, amount)
            return redirect(f'/user/{identifier}')
        return render_template('account.html',
                               user=user,
                               balance=balance,
                               form=form)
    except:
        abort(404, '/user/' + identifier)


@app.route('/api')
def api():
    bank = Bank()
    data = bank.jsonify_bank()
    return Response(data, mimetype='application/json')


@app.route('/progress')
def progress():
    bank = Bank()
    data = bank.total()
    expected = 1000
    result = str(round(data / expected))
    output = (f'<progress id="progress" max="100" value="'
              f'{result}">Progress Bar</progress>')
    return Response(output, mimetype='text/plain')


@app.route('/table')
def table():
    bank = Bank()
    data = bank.generate_table()
    return Response(data, mimetype='text')


@app.route('/admin_dash', methods=['GET', 'POST'])
def admi_dash():
    return render_template('admin.html')


@app.route('/admin')
def admin():
    resp = make_response(redirect('/admin_dash'))
    resp.set_cookie('admin', '1')
    return resp


@app.route('/deadmin')
def deadmin():
    resp = make_response(redirect('/'))
    resp.set_cookie('admin', '0')
    return resp


@app.route('/admin_dash/modify', methods=['GET', 'POST'])
def modify():
    form = AdminForm()
    message = ''
    if form.validate_on_submit():
        try:
            bank = Bank()
            if not bank.modify_money(form.name.data, form.modifier.data):
                message = f'Gave {form.name.data} ${form.modifier.data}'
            else:
                message = f'ERROR'
        except:
            abort(404, '/admin_dash/modify')
    return render_template('adminModify.html', form=form, message=message)


@app.route('/admin_dash/create', methods=['GET', 'POST'])
def create():
    form = CreateForm()
    message = ''
    if form.validate_on_submit():
        bank = Bank()
        try:
            starting_cash = float(form.balance.data)
            if not bank.create_account(form.name.data, ):
                message = f'Gave {form.name.data} ${starting_cash}'
            else:
                message = f'ERROR'
        except:
            message = f'Starting balance is not a valid number'
    return render_template('adminModify.html', form=form, message=message)


@app.errorhandler(404)
def page_not_found(a):
    return render_template("404.html", source=a
                           )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
