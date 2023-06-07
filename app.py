from flask import Flask, render_template, request, jsonify
from flask import request
import os
import sqlite3 as sql
from dotenv import load_dotenv
# app - The flask application where all the magical things are configured.
app = Flask(__name__)
load_dotenv()

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/poster')
def poster():
  return render_template('poster.html')

@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------

@app.route('/random')
def random_buggy():
        import random
        power_type_options = ['bio', 'electric', 'fusion', 'hamster', 'none', 'petrol', 'rocket', 'solar', 'steam', 'thermo', 'wind']
        tyres_options = ['knobbly', 'maglev', 'reactive', 'slick']
        armour_options = ['aluminium', 'thicksteel', 'thinsteel', 'titanium', 'wood']
        attack_options = ['biohazard', 'charge', 'flame', 'spike']
        algo_options = ['buggy','defensive','offensive','random','steady','titfortat']
        flag_color_options = ['white', 'black', 'grey', 'red', 'orange', 'yellow', 'green', 'blue', 'purple']
        flag_pattern_options = ['plain', 'spots', 'stripes']
        special_options = ['antibiotic','banging','fireproof','hamster_boosted','insulated']

        qty_wheels = [2, 4, 6, 8, 10]
        qty_wheels_choice = random.choice(qty_wheels)
        power_type = random.choice(power_type_options)
        tyres = random.choice(tyres_options)
        qty_tyres = random.randint(qty_wheels_choice, qty_wheels_choice + 10)
        armour = random.choice(armour_options)
        attack = random.choice(attack_options)
        algo = random.choice(algo_options)
        flag_color = random.choice(flag_color_options)
        flag_color_sec = random.choice(flag_color_options)
        flag_pattern = random.choice(flag_pattern_options)
        special = random.choice(special_options)

        buggy_data = {
            'qty_wheels': qty_wheels_choice,
            'power_type': power_type,
            'tyres': tyres,
            'qty_tyres': qty_tyres,
            'armour': armour,
            'attack': attack,
            'algo': algo,
            'flag_color': flag_color,
            'flag_color_sec': flag_color_sec,
            'flag_pattern': flag_pattern,
            'special': special
        }

        return buggy_data

@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
    import random

    def validate_random_buggy(buggy_data):
        count = 0
        error_messages = []

        qty_wheels = buggy_data['qty_wheels']
        power_type = buggy_data['power_type']
        tyres = buggy_data['tyres']
        qty_tyres = buggy_data['qty_tyres']
        armour = buggy_data['armour']
        attack = buggy_data['attack']
        algo = buggy_data['algo']
        flag_color = buggy_data['flag_color']
        flag_color_sec = buggy_data['flag_color_sec']
        flag_pattern = buggy_data['flag_pattern']
        special = buggy_data['special']

         # Check for if qty_wheels and qty_tyres have values
        if not qty_wheels:
            error_messages.append("Quantity of wheels is required.")
        if not qty_tyres:
            error_messages.append("Quantity of tyres is required.")

        # Check for if qty_wheels is even and an integer
        if qty_wheels and not qty_wheels.isdigit():
            error_messages.append("Quantity of wheels must be an integer.")
        elif qty_wheels and int(qty_wheels) % 2 != 0:
            error_messages.append("Quantity entered for wheels must be an even value.")

        # Check for if qty_tyres is an integer
        if qty_tyres and not qty_tyres.isdigit():
            error_messages.append("Quantity of tyres must be an integer.")

        # Check for if power_type is selected
        if power_type == 'none':
            error_messages.append("You must choose a Power Type. 'none' is not allowed.")

        # Check for if flag_color and flag_color_sec are different
        if flag_color == flag_color_sec:
            error_messages.append("Colors selected must be different from each other.")

        # Check for 'plain' flag_pattern selected
        if flag_pattern == 'plain':
            flag_color_sec = 'none'

        # Check for if either attack or defensive selected or not
        if attack == 'none':
            algo = 'defensive' if algo == 'defensive' else 'steady'
            

        if not error_messages:
            count = 7  # All checks passed

        return count, error_messages, qty_wheels, power_type, tyres, qty_tyres, armour, attack, algo, flag_color, flag_color_sec, flag_pattern, special

    
    def rules(qty_wheels, power_type, qty_tyres, attack, algo, flag_color, flag_color_sec, flag_pattern):
        count = 0
        error_messages = []
     
        # Check for if qty_wheels and qty_tyres have values
        if not qty_wheels:
            error_messages.append("Quantity of wheels is required.")
        if not qty_tyres:
            error_messages.append("Quantity of tyres is required.")

        # Check for if qty_wheels is even and an integer
        if qty_wheels and not qty_wheels.isdigit():
            error_messages.append("Quantity of wheels must be an integer.")
        elif qty_wheels and int(qty_wheels) % 2 != 0:
            error_messages.append("Quantity entered for wheels must be an even value.")

        # Check for if qty_tyres is an integer
        if qty_tyres and not qty_tyres.isdigit():
            error_messages.append("Quantity of tyres must be an integer.")

        # Check for if power_type is selected
        if power_type == 'none':
            error_messages.append("You must choose a Power Type. 'none' is not allowed.")

        # Check for if flag_color and flag_color_sec are different
        if flag_color == flag_color_sec:
            error_messages.append("Colors selected must be different from each other.")

        # Check for 'plain' flag_pattern selected
        if flag_pattern == 'plain':
            flag_color_sec = 'none'

        # Check for if either attack or defensive selected or not
        if attack == 'none':
            algo = 'defensive' if algo == 'defensive' else 'steady'
            

        if not error_messages:
            count = 7  # All checks passed

        return count, error_messages, qty_wheels, power_type, qty_tyres, attack, algo, flag_color, flag_color_sec, flag_pattern


    def calculate(qty_wheels, power_type, tyres, armour, attack, algo, special, costs):       
        # The total cost of the buggy based on choices selected
    
        total_cost = costs.get(power_type, 0)
        total_cost += costs.get(tyres, 0)
        total_cost += costs.get(attack, 0)
        total_cost += costs.get(algo, 0)
        total_cost += costs.get(special, 0)
        # Multiply the total cost by choices where an integer is involved
        total_cost *= int(qty_wheels)
        # Wheel and Armour cost Percentage equations 
        if int(qty_wheels) > 4:
            wheel_cost_percent = (int(qty_wheels) - 4) * 10
            armour_cost = costs.get(armour, 0)
            wheel_armour_cost = armour_cost * (wheel_cost_percent / 100)
            total_cost += wheel_armour_cost
        elif int(qty_wheels) == 4:
            armour_cost = costs.get(armour, 0)
            total_cost += armour_cost

        return total_cost

    if request.method == 'GET':
        return render_template("buggy-form.html")
    elif request.method == 'POST':
        msg = ""
        action = request.form.get('action')
        
    if action == 'Generate Random Buggy':
        buggy_data = random_buggy()
        count, error_messages, qty_wheels, power_type, tyres, qty_tyres, armour, attack, algo, flag_color, flag_color_sec, flag_pattern, special = validate_random_buggy(buggy_data) 
        total_cost = calculate(buggy_data)

        if count == 7:  # All checks passed
            # Update the database with the random buggy data
            try:
                with sql.connect(DATABASE_FILE) as con:
                    cur = con.cursor()
                    cur.execute(
                        "UPDATE buggies SET qty_wheels=?, power_type=?, tyres=?, qty_tyres=?, armour=?, attack=?, algo=?, flag_color=?, flag_color_sec=?, flag_pattern=?, special=?, valid_check=?, total_cost=? WHERE id=?",
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
                            True,  # Set valid_check to True
                            total_cost,
                            DEFAULT_BUGGY_ID
                        )
                    )
                    con.commit()
                    msg = "Random buggy successfully updated in the database"
            except Exception as e:
                con.rollback()
                msg = "Error in update operation: " + str(e)
            finally:
                con.close()

                return render_template("updated.html", msg=msg)
        else:
            random_buggy_validation_msg = "Random buggy failed validation and therefore was not saved"

        return msg
    

    
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
    row = cursor.fetchone()
    boolean_check = row[0] if row is not None else False
    count, error_messages, qty_wheels, power_type, qty_tyres, attack, algo, flag_color, flag_color_sec, flag_pattern = rules(qty_wheels, power_type, qty_tyres, attack, algo, flag_color, flag_color_sec, flag_pattern)

    valid_check = bool(boolean_check or count == 7)

    if error_messages:
        msg = " ".join(error_messages)
        return render_template("buggy-form.html", error_messages=error_messages, msg=msg)

    total_cost = calculate(qty_wheels, power_type, tyres, armour, attack, algo, special, costs)

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

    return "Invalid request method"



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
