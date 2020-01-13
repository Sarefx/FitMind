from flask import (Flask, render_template, redirect, url_for, 
    request, make_response, g, flash, session, abort)
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required
import forms
import db
import datetime
import fitmind

app = Flask(__name__)
app.secret_key = "fmasdmvs,mv.q;)(*&^%$wpoeuxmcmvruei8eoksmdm1245tw1%!@#$*%vsmxcv"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return db.User.get(db.User.id == userid)
    except db.DoesNotExist:
        return None

@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = db.DATABASE
    g.db.connect(reuse_if_open=True)

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response

# ***************************HOME***************************

@app.route('/', methods=('GET', 'POST'))
def home():
    form = forms.GenerateGoals2()
    
    if form.validate_on_submit():
        weight = form.weight.data
        weight_measurement_preference = form.weight_measurement_preference.data

        if weight_measurement_preference == "lbs":
            weight = weight / 2.20462
        height = form.height.data
        height_measurement_preference = form.height_measurement_preference.data

        if height_measurement_preference == "inches":
            height = height / 0.393701
        age = form.age.data
        gender = form.gender.data
        bw_goal = form.bw_goal.data
        bw_goal_measurement_preference = form.bw_goal_measurement_preference.data

        if bw_goal_measurement_preference == "lbs":
            bw_goal = bw_goal / 2.20462
        results = fitmind.generate_goals2(weight,height,age,gender,bw_goal)
        return render_template('home.html', form=form, results=results)
    return render_template('home.html', form=form, results=None)

# ***************************LOGIN***************************

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()

    if form.validate_on_submit():
        try:
            user = db.User.get(db.User.email==form.email.data)
        except db.DoesNotExist:
            flash("Your email or password doesnt match!", "error")
        else:            
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Your email or password doesnt match!", "error")
    return render_template('login.html', form=form)

# ***************************Dashboard***************************

@app.route('/dashboard', methods=('GET', 'POST'))
@login_required
def dashboard():
    user = db.User.get(db.User.id == session["user_id"])

    # print("Today date is ",today_date)
    
    calorie_deficit_last_7_days = 0
    calorie_deficit_previous_7_days = 0
    calorie_deficit_last_30_days = 0
    calorie_deficit_previous_30_days = 0
    calorie_balance_last_7_days = 0
    calorie_balance_previous_7_days = 0
    calorie_balance_last_30_days = 0
    calorie_balance_previous_30_days = 0
    average_bodyweight_last_7_days = 0
    average_bodyweight_previous_7_days = 0
    average_bodyweight_last_30_days = 0
    average_bodyweight_previous_30_days = 0

    #sup_def_balance_last_7_days = 0
    #sup_def_balance_previous_7_days = 0
    #sup_def_balance_last_30_days = 0
    #sup_def_balance_previous_30_days = 0

    today_date = datetime.datetime.now()

    for x in range(60):
        current_date = today_date - datetime.timedelta(days=1+x)
        #print("X is ",x," and current date is ",current_date)

        try:
            day_data = db.DayData.get(db.DayData.user == user and db.DayData.date == current_date)
            deficit = day_data.calorie_plus - day_data.calorie_minus
            calorie_balance = (day_data.calorie_minus - user.calorie_minus_goal) + (user.calorie_plus_goal - day_data.calorie_plus)
            bodyweight = day_data.dayweight

            if x < 7:
                calorie_deficit_last_7_days = calorie_deficit_last_7_days + deficit
                calorie_balance_last_7_days = calorie_balance_last_7_days + calorie_balance
                average_bodyweight_last_7_days = average_bodyweight_last_7_days + bodyweight
            elif x < 14:
                calorie_deficit_previous_7_days = calorie_deficit_previous_7_days + deficit
                calorie_balance_previous_7_days = calorie_balance_previous_7_days + calorie_balance
                average_bodyweight_previous_7_days = average_bodyweight_previous_7_days + bodyweight
            
            if x < 30:
                calorie_deficit_last_30_days = calorie_deficit_last_30_days + deficit
                calorie_balance_last_30_days = calorie_balance_last_30_days + calorie_balance
                average_bodyweight_last_30_days = average_bodyweight_last_30_days + bodyweight
            elif x < 60:
                calorie_deficit_previous_30_days = calorie_deficit_previous_30_days + deficit
                calorie_balance_previous_30_days = calorie_balance_previous_30_days + calorie_balance
                average_bodyweight_previous_30_days = average_bodyweight_previous_30_days + bodyweight
        except db.DoesNotExist:
            flash("Not enough data for the full analysis", "error")
            break

    average_bodyweight_last_7_days = float("{0:.1f}".format(average_bodyweight_last_7_days / 7))
    average_bodyweight_previous_7_days = float("{0:.1f}".format(average_bodyweight_previous_7_days / 7))
    average_bodyweight_last_30_days = float("{0:.1f}".format(average_bodyweight_last_30_days / 30))
    average_bodyweight_previous_30_days = float("{0:.1f}".format(average_bodyweight_previous_30_days / 30))

    statistics_data = {'c_d_7': calorie_deficit_last_7_days, 'c_b_7': calorie_balance_last_7_days, 'a_b_7': average_bodyweight_last_7_days,
        'c_d_14': calorie_deficit_previous_7_days, 'c_b_14': calorie_balance_previous_7_days, 'a_b_14': average_bodyweight_previous_7_days,
        'c_d_30': calorie_deficit_last_30_days, 'c_b_30': calorie_balance_last_30_days, 'a_b_30': average_bodyweight_last_30_days,
        'c_d_60': calorie_deficit_previous_30_days, 'c_b_60': calorie_balance_previous_30_days, 'a_b_60': average_bodyweight_previous_30_days,}

    return render_template('dashboard.html', statistics_data=statistics_data)

# ***************************LOGOUT***************************

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out!", "success")
    return redirect(url_for('home'))

# ***************************REGISTER***************************

@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegistrationForm()

    if form.validate_on_submit():
        flash("Yay, you registered!", "success")
        db.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('login'))  
    return render_template('register.html', form=form)

# ***************************MY GOALS***************************

@app.route('/mygoals', methods=('GET', 'POST'))
@login_required
def mygoals():
    form1 = forms.SetGoals()
    form2 = forms.GenerateGoals()
    form3 = forms.SetLastCountedDate()
    user = db.User.get(db.User.id == session["user_id"])

    if form1.validate_on_submit():
        if form1.calorie_minus_goal.data is not None:
            user.calorie_minus_goal = form1.calorie_minus_goal.data
        if form1.calorie_plus_goal.data is not None:
            user.calorie_plus_goal = form1.calorie_plus_goal.data
        if form1.calorie_balance.data is not None:
            user.calorie_balance = form1.calorie_balance.data

    if form2.validate_on_submit():
        #print("The data in the field is ",form2.bw_goal.data)
        if form2.bw_goal.data is not None:
            bw_goal = form2.bw_goal.data
            results = fitmind.generate_goals(bw_goal, session["user_id"])
            user.calorie_minus_goal = results.get('cal_minus_goal')
            user.calorie_plus_goal = results.get('cal_plus_goal')
            #print("Goals are ",results.get('cal_minus_goal')," and ",results.get('cal_plus_goal'))
        user.save()
        flash("Your data was set!", "success")
        return redirect(url_for('mygoals'))

    if form3.validate_on_submit():
        user = db.User.get(db.User.id == session["user_id"])
        user.last_time_counted = form3.last_counted_date.data
        user.save()
        flash("The last counted date was set!", "success")
        return redirect(url_for('mygoals'))
    return render_template('mygoals.html', form1=form1, form2=form2, form3=form3)

@app.route('/count_yesterday', methods=('GET', 'POST'))
@login_required
def count_yesterday():
    user = db.User.get(db.User.id == session["user_id"])
    date_today = datetime.datetime.now()
    date_yesterday = date_today - datetime.timedelta(days=1)
    
    try:
        while user.last_time_counted.strftime("%Y-%m-%d") <= date_yesterday.strftime("%Y-%m-%d"):
            
            #print("Trying to count date ",date_yesterday.strftime("%Y-%m-%d")," and the last day counted is ",user.last_time_counted.strftime("%Y-%m-%d"))
            try:
                day_log = db.DayData.get(db.DayData.user == user and db.DayData.date == user.last_time_counted)

                balance =  (day_log.calorie_minus - user.calorie_minus_goal) + (user.calorie_plus_goal - day_log.calorie_plus)
                #print("Trying to calorie minus ",day_log.calorie_minus," minus calorie minus goal ",user.calorie_minus_goal," plus calories plus goal ",user.calorie_plus_goal," minus calorie plus ",day_log.calorie_plus)
                user.calorie_balance =  user.calorie_balance + balance
                user.last_time_counted = user.last_time_counted + datetime.timedelta(days=1)
                #print("Calorie balance is ",user.calorie_balance," and last counted day is ",user.last_time_counted)
                user.save() 
            except db.DoesNotExist:
                flash("There was a problem with a date", "error")
                return redirect(url_for('dashboard'))
        flash("You've updated your balance", "success")
        return redirect(url_for('dashboard'))
    except db.DoesNotExist:
        flash("There is no log from yesterday", "error")
        return redirect(url_for('dashboard'))

# ***************************MY LOGS***************************

@app.route('/mylogs', methods=('GET', 'POST'))
@login_required
def mylogs():
    form = forms.AddLog()
    user = db.User.get(db.User.id == session["user_id"])
    day_datas = db.DayData.select().where(db.DayData.user == user).order_by(db.DayData.date.desc())

    if form.validate_on_submit():
        print("Adding log: date is",form.date.data,"user is",user.username)
        user_query = db.DayData.select().where(db.DayData.user == user)
        query =  user_query.select().where(db.DayData.date == form.date.data)
        if query.exists():
            flash("The date you selected already exists", "error")
        else:
            cal_plus = form.cal_plus.data
            cal_minus = form.cal_minus.data
            day_weight = form.day_weight.data
            date = form.date.data

            db.DayData.create_daydata(user=user, calorie_plus=cal_plus, calorie_minus=cal_minus, dayweight=day_weight, date=date)

            user.set_weight(day_weight)
            user.save()
            flash("Your new day log was added!", "success")
            return redirect(url_for('mylogs'))

    form.date.data = datetime.datetime.now() - datetime.timedelta(days=1)
    return render_template('mylogs.html', form=form, day_datas=day_datas)

@app.route('/remove_log/<day_date>', methods=('GET', 'POST'))
@login_required
def remove_log(day_date):
    user = db.User.get(db.User.id == session["user_id"])
    try:
        #print("Trying to delete date ",day_date," for user with id is ",session["user_id"])
        db.DayData.get(db.DayData.user == user and db.DayData.date == day_date).delete_instance()
        flash("You've removed a log!", "success")
        return redirect(url_for('mylogs'))
    except db.DoesNotExist:
        abort(404)

# ***************************ADMIN***************************

@app.route('/admin', methods=('GET', 'POST'))
@login_required
def admin():
    users = db.User.select().order_by(db.User.joined_at.desc())
    return render_template('admin.html', users=users)

@app.route('/remove_user/<user_email>', methods=('GET', 'POST'))
@login_required
def remove_user(user_email):
    try:
        db.User.get(db.User.email == user_email).delete_instance()
        flash("You've removed a user!", "success")
        return redirect(url_for('admin'))
    except db.DoesNotExist:
        abort(404)

@app.route('/add_blog', methods=('GET', 'POST'))
@login_required
def add_blog():
    form = forms.AddBlog()
    blogs = db.Blog.select()
    if form.validate_on_submit():
        title = form.title.data
        text = form.text.data
        author = form.author.data
        db.Blog.create_blog(title=title, text=text, author=author)

        flash("Blog was added!", "success")
        return redirect(url_for('add_blog'))
    return render_template('add_blog.html', form=form, blogs=blogs)

@app.route('/delete_blog/<blog_id>', methods=('GET', 'POST'))
@login_required
def delete_blog(blog_id):
    try:
        db.Blog.get(db.Blog.id == blog_id).delete_instance()
        flash("You've deleted a blog!", "success")
        return redirect(url_for('add_blog'))
    except db.DoesNotExist:
        abort(404)

# ***************************MY STATS***************************

@app.route('/mystats', methods=('GET', 'POST'))
@login_required
def mystats():
    form = forms.MyStats()
    user = db.User.get(db.User.id == session["user_id"])

    if form.validate_on_submit():

        if form.weight.data != None:
            user.set_weight(form.weight.data)
        
        if form.height.data != None:
            user.set_height(form.height.data)

        if form.birth_date.data != None:
            user.birth_date = form.birth_date.data

        if form.gender.data != "None":
            user.gender = form.gender.data

        if form.weight_measurement_preference.data != "None":
            user.weight_measurement_preference = form.weight_measurement_preference.data

        if form.height_measurement_preference.data != "None":
            user.height_measurement_preference = form.height_measurement_preference.data
        user.save()
        flash("Your data was updated!", "success")
        return redirect(url_for('mystats'))
    return render_template('mystats.html', form=form)

# ***************************BLOG***************************

@app.route('/blog', methods=('GET', 'POST'))
def blog():
    blogs = db.Blog.select().order_by(db.Blog.date.desc())
    return render_template('blog.html', blogs=blogs)

# ***************************CHANGE PASSWORD***************************

@app.route('/changepassword', methods=('GET', 'POST'))
@login_required
def changepassword():
    form = forms.ChangePasword()
    user = db.User.get(db.User.id == session["user_id"])

    if form.validate_on_submit():           
        if check_password_hash(user.password, form.old_password.data):
            new_password = form.password.data
            user.password = generate_password_hash(new_password)
            user.save()
            flash("Password was changed!", "success")
            return redirect(url_for('mystats'))
        else:
            flash("Your password doesnt match!", "error")
    return render_template('changepassword.html', form=form)

# ***************************ERROR HANDLING***************************

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    #app.run(debug=True, port=8000, host='0.0.0.0')
    app.run()
