from flask import Flask, render_template, request, jsonify
import os
import sqlite3 as sql

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
    def rules(qty_wheels, power_type, qty_tyres, flag_color, flag_color_sec, flag_pattern):
        count = 0
        error_messages = []

            count += 1
        else:
            error_messages.append("Quantity entered for wheels must be an even value.")

        if power_type != 'none':
            count += 1
        else:
            error_messages.append("You must choose a Power Type. 'none' is not allowed.")
            return False, error_messages
    
        if int(qty_tyres) >= int(qty_wheels) and int(qty_tyres) % 2 == 0:
            count += 1
        else:
            error_messages.append("Quantity entered for tyres must be equal to or greater than the number of wheels, and it must be an even value.")

        if flag_color != flag_color_sec:
            count += 1
        else:
            error_messages.append("Colors selected must be different from each other.")

        if flag_pattern != 'plain':
            if flag_color != flag_color_sec:
                count += 1
            else:
                error_messages.append("Only the primary color is saved when 'plain' is selected for flag pattern.")

        return count == 5, error_messages


    def calculate(qty_wheels, power_type, tyres, qty_tyres, armour, attack, algo, special, costs):
    # Calculate the total cost of the buggy based on choices selected
        total_cost += costs.get(tyres, 0)  
        total_cost += costs.get(armour, 0)  
        total_cost += costs.get(attack, 0)  
        total_cost += costs.get(algo, 0)  
        total_cost += costs.get(special, 0)  
    # Multiply the total cost by choices where an integer is involved
        total_cost *= int(qty_wheels)
        total_cost *= int(qty_tyres)

        return total_cost
   

    if request.method == 'GET':
        return render_template("buggy-form.html")
    elif request.method == 'POST':
        msg = ""
        qty_wheels = request.form['qty_wheels']
        power_type = request.form['power_type']
        tyres = request.form['tyres']
        qty_tyres = request.form['qty_tyres']
        armour = request.form['armour']
        attack = request.form['attack']
        algo = request.form['algo']
        flag_color = request.form['flag_color']
        flag_color_sec = request.form['flag_color_sec']
        flag_pattern = request.form['flag_pattern']
        special = request.form['special']

        costs = {
            'bio': 5,
            'electric': 20,
            'fusion': 400,
            'hamster': 3,
            'none': 0,
            'petrol': 4,
            'rocket': 16,
            'solar': 40,
            'steam': 3,
            'thermo': 300,
            'wind': 20,
            'knobbly': 15,
            'maglev': 50,
            'reactive': 40,
            'slick': 10,
            'steelbend': 20,
            'aluminium': 200,
            'thicksteel': 200,
            'thinsteel': 100,
            'titanium': 290,
            'wood': 40,
            'biohazard': 30,
            'charge': 28,
            'flame': 20,
            'spike': 5,
            'antibiotic': 90,
            'banging': 42,
            'fireproof': 70,
            'hamster_booster': 5,
            'insulated': 100
        }
        
        connection = sql.connect(DATABASE_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT valid_check FROM buggies WHERE id = ?", (DEFAULT_BUGGY_ID,))
        boolean_check = cursor.fetchone()[0]

        check, error_messages = rules(qty_wheels, power_type, qty_tyres, flag_color, flag_color_sec, flag_pattern)
        valid_check = bool(boolean_check or check)

        if not check:
            msg = " ".join(error_messages)
            return render_template("buggy-form.html", error_messages=error_messages)

        total_cost = calculate(qty_wheels, power_type, tyres, qty_tyres, armour, attack, algo, special, costs)

        if not qty_wheels.isdigit():
            msg = "Quantity of wheels must be an integer"
            return render_template("buggy-form.html", msg=msg)
        if not qty_tyres.isdigit():
            msg = "Quantity of tyres must be an integer"
            return render_template("buggy-form.html", msg=msg)
        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE buggies SET qty_wheels=?, power_type=?, tyres=?, qty_tyres=?, armour=?, attack=?, algo=?, flag_color=?, flag_color_sec=?, flag_pattern=?, special=?, total_cost=?, valid_check=? WHERE id=?",
                    (
                        qty_wheels,
                        power_type,
                        tyres,
                        qty_tyres,
                        armour,
                        attack,
                        algo,
                        flag_color,
                        flag_color_sec,
                        flag_pattern,
                        special,
                        total_cost,
                        valid_check,
                        DEFAULT_BUGGY_ID
                    )
                )

                con.commit()
                msg = "Record successfully saved"
        except Exception as e:
            con.rollback()
            msg = "Error in update operation: " + str(e)
        finally:
            con.close()

        return render_template("updated.html", msg=msg)




#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone(); 
    return render_template("buggy.html", buggy = record)

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
@app.route('/edit')
def edit_buggy():
    return render_template("buggy-form.html")


@app.route('/specs')
def spec_buggy():
    return render_template("info.html")
#------------------------------------------------------------
# You probably don't need to edit this... unless you want to ;)
#
# get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------
@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))

    buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items() 
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })

# You shouldn't need to add anything below this!
if __name__ == '__main__':
    alloc_port = os.environ.get('CS1999_PORT') or 5000
    app.run(debug=True, host="0.0.0.0", port=alloc_port)
