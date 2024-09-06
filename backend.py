import json
import sqlite3
from flask_wtf import FlaskForm, CSRFProtect
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired


class Bank:
    def __init__(self):
        self.conn = sqlite3.connect('bank.db')

    def execute(self, command):
        cursor = self.conn.cursor()
        cursor.execute(command)
        result = cursor.fetchall()
        self.conn.commit()
        cursor.close()
        return result

    def make_bank(self):
        self.execute("CREATE TABLE IF NOT EXISTS bank("
                     "    id INTEGER PRIMARY KEY,"
                     "    name LINESTRING, "
                     "    balance FLOAT)")

    def create_account(self, name, balance=0.0):
        self.execute(f"INSERT INTO bank "
                     f" (name, balance) VALUES ('{name}', {balance})")

    def get_account(self, name):
        return self.execute(f"SELECT * FROM bank WHERE name = '{name}'")

    def get_account_by_id(self, id):
        return self.execute(f"SELECT * FROM bank WHERE id = {id}")

    def get_json(self, name):
        account = self.get_account(name)[0]
        return {f'{account[1]}': account[2]}

    def get_all_bank(self):
        return self.execute('SELECT * FROM bank')

    def jsonify_bank(self):
        data = self.get_all_bank()
        output = {}
        for account in data:
            output[account[1]] = f'{account[2]}'
        return json.dumps(output)

    def generate_table(self):
        bank = self.get_all_bank()
        output = ("<table> <tr>"
                  " <th>Naam</th>"
                  " <th>Balans</th>")
        for account in bank:
            name = account[1]
            balance = account[2]
            output += (f'<tr>'
                       f'<td>{name}</td> '
                       f'<td>{balance}</td>'
                       f'</tr>')
        output += '</table>'
        return output

    def modify_money(self, name, money):
        account = self.get_account(name)
        if account is not []:
            account = account[0]
            balance = account[2] + float(money)
            self.execute(f'UPDATE bank SET balance = {balance} WHERE name = '
                         f'"{name}"')
        else:
            return False

    def set_money(self, name, money):
        account = self.get_account(name)
        if account is not []:
            account = account[0]
            print(account)
            balance = float(money)
            self.execute(f'UPDATE bank SET balance = {balance} WHERE name = '
                         f'"{name}"')
        else:
            return False
    def total(self):
        return self.execute(f"SELECT SUM(balance) FROM bank")[0][0]

    def getNames(self):
        hits = self.execute("SELECT name FROM bank")
        names = []
        for hit in hits:
            names.append((hit[0], hit[0]))
        return names

class AdminForm(FlaskForm):
    bank = Bank()
    name = SelectField("Username", choices=bank.getNames())
    modifier = StringField('How much money to add:')
    submit = SubmitField('Submit')

class CreateForm(FlaskForm):
    name = StringField('Name of account:')
    balance = StringField('How much money to start them with:')
    submit = SubmitField('Submit')

class UpdateForm(FlaskForm):
    amount = StringField('How much?')
    choice = SelectField("Choose an option", choices=[('modify', 'Modify'),
                                                      ('set', 'Set')])
    submit = SubmitField('Submit')