import datetime
from flask_login import UserMixin
from peewee import *
from flask_bcrypt import generate_password_hash, check_password_hash
from playhouse.migrate import *

DATABASE = SqliteDatabase('../users.db')

class User(UserMixin, Model):
    username = CharField(max_length=255, unique=True)
    email = CharField(max_length=255, unique=True)
    password = CharField(max_length=1000)
    weight = FloatField(default=0)  # in kgs
    height = FloatField(default=0)  # in cm
    gender = CharField(default='N/A', max_length=10)  # male, female, other

    birth_date = DateField(default=datetime.date.today)

    weight_measurement_preference =  CharField(default='kg', max_length=10)  # other choice is lbs
    height_measurement_preference =  CharField(default='cm', max_length=10)  # other choice is in
    
    calorie_plus_goal = IntegerField(default=0)
    calorie_minus_goal = IntegerField(default=0)
    calorie_balance = IntegerField(default=0)
    protein_balance = IntegerField(default=0)

    last_time_counted = DateTimeField(default=datetime.datetime.now)
    is_calorie_tracking_system_active = BooleanField(default=False)

    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    def set_weight(self, weight):
        if self.weight_measurement_preference == "kg":
            weight = weight
        elif self.weight_measurement_preference == "lbs":
            weight = weight / 2.20462
        self.weight = weight

    def set_height(self, height):
        if self.height_measurement_preference == "cm":
            height = height
        elif self.height_measurement_preference == "in":
            height = height / 0.393701
        self.height = height
        
    def weight_calculated(self):
        if self.weight_measurement_preference == "kg":
            return str(int(self.weight)) + " kg"
        elif self.weight_measurement_preference == "lbs":
            weight_lbs = self.weight * 2.20462
            return  str(int(weight_lbs)) + " lbs"

    def height_calculated(self):
        if self.height_measurement_preference == "cm":
            return str(int(self.height)) + " cm"
        elif self.height_measurement_preference == "in":
            height_inches = int(self.height * 0.393701)
            height_feet = int(height_inches / 12)
            height_inches = int(height_inches % 12)
            height_feet_inches = str(height_feet) + "' " + str(height_inches) + '"'
            return  height_feet_inches

    def age_calculated(self):
        today = datetime.date.today()
        age = today - self.birth_date
        age = age.days / 365.25
        age = int(age)
        return age
    
    def count_logs(self):
        logs_quantity = DayData.select().where(DayData.user == self).count()
        return logs_quantity

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            return cls.create(username=username,
            email=email,
            password=generate_password_hash(password),
            is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")

    class Meta:
        database = DATABASE

class DayData(Model):
    calorie_plus = IntegerField(default=0)
    carbohydrate = IntegerField(default=0)
    protein = IntegerField(default=0)
    protein_goal = IntegerField(default=0)
    protein_balance = IntegerField(default=0)
    fat = IntegerField(default=0) 
    
    calorie_plus_goal = IntegerField(default=0)
    calorie_minus_goal = IntegerField(default=0)
    calorie_balance_total = IntegerField(default=0)
    calorie_balance = IntegerField(default=0)
    calorie_deficit = IntegerField(default=0)

    calorie_minus = IntegerField(default=0)

    deficit_analysis = IntegerField(default=0) # 0 within 50 calories, +-1 within 200, +-2 within 500, +-3 within 1000, +-4 over 1000

    dayweight = FloatField(default=0) # in kg
    date = DateField(unique=False)
    user = ForeignKeyField(User, backref='data')

    def deficit_analysis_method(self):
        # Gives a string of analysis
        deficit_analysis_string = ""
        balance = self.calorie_plus - self.calorie_minus

        if balance < -1000:
            deficit_analysis_string = "Excessive Deficit"
        elif balance < -500:
            deficit_analysis_string = "Extra Deficit"
        elif balance < -200:
            deficit_analysis_string = "Deficit"
        elif balance < -50:
            deficit_analysis_string = "Small Deficit"
        elif balance < 50:
            deficit_analysis_string = "Even"
        elif balance < 200:
            deficit_analysis_string = "Small Surplus"
        elif balance < 500:
            deficit_analysis_string = "Surplus"
        elif balance <= 1000:
            deficit_analysis_string = "Extra Surplus"
        elif balance > 1000:
            deficit_analysis_string = "Excessive Surplus"
        return deficit_analysis_string

    def dayweight_calculated(self):
        measurement = self.user.weight_measurement_preference

        if measurement == "kg":
            return str("%.1f" % self.dayweight) + " kg"
        elif measurement == "lbs":
            weight_lbs = self.dayweight * 2.20462
            return  str("%.1f" % weight_lbs) + " lbs"

    @classmethod
    def create_daydata(cls, user, calorie_plus, calorie_minus, dayweight, date):

        if user.weight_measurement_preference == "kg":
            dayweight = dayweight
        elif user.weight_measurement_preference == "lbs":
            dayweight = dayweight / 2.20462
        return cls.create(user=user,
            calorie_plus=calorie_plus,
            calorie_minus=calorie_minus,
            dayweight=dayweight,
            date=date)

    class Meta:
        database = DATABASE
        order_by = ('-date',)


class Blog(Model):
    title = CharField(max_length=50)
    date = DateField(default=datetime.date.now)
    text = CharField(max_length=10000)
    author = CharField(max_length=50)

    @classmethod
    def create_blog(cls, title, date, text, author):

        return cls.create(title=title,
            date=date,
            text=text,
            author=author)

    class Meta:
        database = DATABASE
        order_by = ('-date',)

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, DayData, Blog], safe=True)
    DATABASE.close()

# make_changes function is to add or remove columns/tables
def make_changes():
    my_db = SqliteDatabase('users.db')
    migrator = SqliteMigrator(my_db)
    deficit_analysis_field = IntegerField(default=33)
    migrate(migrator.add_column('DayData', 'deficit_analysis', deficit_analysis_field),)  # this is old migration, need to change for the future

def populate_admin_data():
    # I commented out these 2 lines because it doesnt make sense why they are there
    #DATABASE.drop_tables([User, DayData])
    #DATABASE.create_tables([User, DayData], safe=True)
    data = (('admin', 'admin@test.com', 'password', 100, 175, 'male', 
        ((3000,3200, 105, "2019-03-01"),  (3100,3810, 104.8, "2019-03-03"), (2900,3150, 104.9, "2019-03-02"))
        ),)

    for username, email, password, weight, height, gender, days in data:
        user = User.create_user(username, email, password, True)
        user.weight = weight
        user.height = height
        user.gender = gender
        user.save()

        for dayP, dayM, dayweight, date in days:
            DayData.create(user=user, calorie_plus=dayP, calorie_minus=dayM, dayweight=dayweight, date=date)

def populate_test_data():
    data = (
        ('test1', 'test1@test.com', 'password', 100, 150, 'male', 
            ((3000,3500, 105, "2019-03-01"), (2900,3450, 104.9, "2019-03-02"), (3100,3810, 104.8, "2019-03-03"),
            (3050,3710, 104.8, "2019-03-04"), (2900,3550, 104.8, "2019-03-05"), (3000,3810, 104.7, "2019-03-06"),
            (3010,3730, 104.6, "2019-03-07"), (3200,3630, 104.6, "2019-03-08"), (3130,3820, 104.5, "2019-03-09"))),
        ('test2', 'test2@test.com', 'password', 100, 150, 'male',
            ((3000,3500, 105, "2019-03-01"), (2900,3450, 104.9, "2019-03-02"), (3100,3810, 104.8, "2019-03-03"),
            (3050,3710, 104.8, "2019-03-04"), (2900,3550, 104.8, "2019-03-05"), (3000,3810, 104.7, "2019-03-06"),
            (3010,3730, 104.6, "2019-03-07"), (3200,3630, 104.6, "2019-03-08"), (3130,3820, 104.5, "2019-03-09"))),
        ('test3', 'test3@test.com', 'password', 100, 150, 'male',
            ((3000,3500, 105, "2019-03-01"), (2900,3450, 104.9, "2019-03-02"), (3100,3810, 104.8, "2019-03-03"),
            (3050,3710, 104.8, "2019-03-04"), (2900,3550, 104.8, "2019-03-05"), (3000,3810, 104.7, "2019-03-06"),
            (3010,3730, 104.6, "2019-03-07"), (3200,3630, 104.6, "2019-03-08"), (3130,3820, 104.5, "2019-03-09"))),
        ('test4', 'test4@test.com', 'password', 100, 150, 'male',
            ((3000,3500, 105, "2019-03-01"), (2900,3450, 104.9, "2019-03-02"), (3100,3810, 104.8, "2019-03-03"),
            (3050,3710, 104.8, "2019-03-04"), (2900,3550, 104.8, "2019-03-05"), (3000,3810, 104.7, "2019-03-06"),
            (3010,3730, 104.6, "2019-03-07"), (3200,3630, 104.6, "2019-03-08"), (3130,3820, 104.5, "2019-03-09"))),
        ('test5', 'test5@test.com', 'password', 100, 150, 'male',
            ((3000,3500, 105, "2019-03-01"), (2900,3450, 104.9, "2019-03-02"), (3100,3810, 104.8, "2019-03-03"),
            (3050,3710, 104.8, "2019-03-04"), (2900,3550, 104.8, "2019-03-05"), (3000,3810, 104.7, "2019-03-06"),
            (3010,3730, 104.6, "2019-03-07"), (3200,3630, 104.6, "2019-03-08"), (3130,3820, 104.5, "2019-03-09")))
    )

    for username, email, password, weight, height, gender, days in data:
        user = User.create_user(username, email, password)
        user.weight = weight
        user.height = height
        user.gender = gender
        user.save()

        for dayP, dayM, dayweight, date in days:
            DayData.create(user=user, calorie_plus=dayP, calorie_minus=dayM, dayweight=dayweight, date=date)

def view_all_data():
    users = User.select()
    
    for user in users:
        print("Username: ",user.username," Email: ",user.email," Password: ",user.password," Weight: ",user.weight," Height: ",user.height)
        daydatas = DayData.select().where(DayData.user == user)
        for daydata in daydatas:
            print("Calories plus: ",daydata.calorie_plus," Calories minus: ",daydata.calorie_minus," Weight: ",daydata.dayweight ," Date: ",daydata.date)

if __name__ == '__main__':
    #initialize()
    #populate_admin_data()
    #populate_test_data()
    #make_changes()
    #view_all_data()
    pass
