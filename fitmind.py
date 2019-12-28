import datetime
import db

fitbit_error = 1.0123145423513231



# gives us an average value
def avg(array):
    return sum(array) / len(array)  


# find variables for the equastion
# works to variables for a week goal
def findEquationAvg(input_cal_burnt, input_cal_consumed, output_bw_change):
    # output = inputA * variableA - inputB - variableB
    
    # Assumption for starting values
    var_A = 1
    var_B = 0
    
    input_train_cal_burnt = avg(input_cal_burnt)
    input_train_cal_consumed = avg(input_cal_consumed)
    output_train_bw_change = output_bw_change

    output_train_bw_change += .00000001

    print("The train data: cal burn ",input_train_cal_burnt," cal consumed ",input_train_cal_consumed," bw change ",output_train_bw_change)
    
    goal_accuracy = 1

    # First test
    trial_accuracy = 0
    trial = 1
    
    # 7700 calories is needed to lose 1 kg of bodyfat
    output_trial_bw_change = (input_train_cal_consumed - input_train_cal_burnt * var_A + var_B)/7700
    
    trial_accuracy = abs(output_trial_bw_change / output_train_bw_change)
    print("Trial # ",trial," and output trial: ", output_trial_bw_change, " but output train: ", output_train_bw_change," so trial accuracy: ", trial_accuracy," and goal accuracy is ",goal_accuracy)
    
    if (trial_accuracy < goal_accuracy):
        while trial_accuracy < goal_accuracy:
        
            var_A += .01
            var_B += 5
            
            # 7700 calories is needed to lose 1 kg of bodyfat
            output_trial_bw_change = (input_train_cal_consumed - input_train_cal_burnt * var_A + var_B)/7700
            trial_accuracy = abs(output_trial_bw_change / output_train_bw_change)
            print("The - trial# ",trial," and output trial: ", output_trial_bw_change, " but output train: ", output_train_bw_change," so trial accuracy: ", trial_accuracy," and goal accuracy is ",goal_accuracy)
            
            trial += 1
            # break in case something breaks
            if trial > 100:
                break
    elif (trial_accuracy > goal_accuracy):       
         while trial_accuracy > goal_accuracy:
        
            var_A -= .01
            var_B -= 5
            
            # 7700 calories is needed to lose 1 kg of bodyfat
            output_trial_bw_change = (input_train_cal_consumed - input_train_cal_burnt * var_A + var_B)/7700
            trial_accuracy = abs(output_trial_bw_change / output_train_bw_change)
            print("The + trial# ",trial," and output trial: ", output_trial_bw_change, " but output train: ", output_train_bw_change," so trial accuracy: ", trial_accuracy," and goal accuracy is ",goal_accuracy)
            
            trial += 1
            # break in case something breaks
            if trial > 100:
                break
    return var_A, var_B

def testEquationAvg(var_A, var_B, cal_minus, cal_plus):
    bw_change = 0
    bw_change = (cal_plus - cal_minus * var_A + var_B) / 7700
    return bw_change

def get_base_general_goals(bw):
    # its gonna really hard to pick the right numbers here, still a lot needs to be changed. I think if the subject is male, start with base metabolic rate bw * 10 calories
    # average weight for men is 75 kg, assuming a person wants to lose weight is around 110 kg, that accumulates a caloric need of 110 * 22 = 2420 plus 300 to spare = 2720 is a bench mark
    # average calories to burn will be around 3500 to lose weight

    # I will use an average between average of all numbers user provided and use my benchmark

    average_human_height = 175.4
    median_human_age_usa = 38

    caloriesConsumeBenchmark_new_formula = (88.362 + (4.799 * average_human_height) + (13.397 * bw) - (5.677 * median_human_age_usa)) * 1.3 
    #print(caloriesConsumeBenchmark_new_formula)

    calories_consume_benchmark = bw * 23.5
    calories_burn_benchmark = bw * 27.5

    #print("Starting calorie goals are ",calories_consume_benchmark," and ",calories_burn_benchmark)
    
    return calories_consume_benchmark, calories_burn_benchmark

def get_basal_metabolic_rate(weight, height, gender, age):
    # its gonna really hard to pick the right numbers here, still a lot needs to be changed. I think if the subject is male, start with base metabolic rate bw * 10 calories
    # average weight for men is 75 kg, assuming a person wants to lose weight is around 110 kg, that accumulates a caloric need of 110 * 22 = 2420 plus 300 to spare = 2720 is a bench mark
    # average calories to burn will be around 3500 to lose weight

    # The formula is from https://en.wikipedia.org/wiki/Harris–Benedict_equation

    #print("The gender is ",gender)
    if gender == "male":
        #print("If is 1")
        calories_consume_benchmark = 88.362 + (4.799 * height) + (13.397 * weight) - (5.677 * age)
    elif gender == "female":
        calories_consume_benchmark = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    elif gender == "other":
        one_benchmark = 88.362 + (4.799 * height) + (13.397 * weight) - (5.677 * age)
        two_benchmark = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        calories_consume_benchmark = (one_benchmark + two_benchmark) / 2

    #print("Basal metabolic rate is ",calories_consume_benchmark)
    return calories_consume_benchmark


def doFitMindMagic(cplus, cminus, bwchange, bw, week_goal):
    print("The data received is ",bw, cplus, cminus, bwchange, week_goal)

    week_goal = -week_goal

    var_A, var_B = findEquationAvg(cminus, cplus, bwchange)

    print("Variable A is ",var_A," and variable B is ",var_B)

    calories_consume_benchmark, calories_burn_benchmark = get_base_general_goals(bw)

    print("Starting calorie goals are ",calories_consume_benchmark," and ",calories_burn_benchmark)

    calorie_consume_lower_limit = calories_consume_benchmark * .8
    calorie_consume_upper_limit = calories_consume_benchmark * 2

    calorie_burn_lower_limit = calories_burn_benchmark * .9
    calorie_burn_upper_limit = calories_burn_benchmark * 3

    # to adapt calories to the behavior
    calories_consume = (avg(cplus) + calories_consume_benchmark * 3)  / 4
    calories_burn = (avg(cminus) +  calories_burn_benchmark * 3) / 4

    print("Adjusted calorie goals are ",calories_consume," and ",calories_burn)

    expected_bw_change = testEquationAvg(var_A, var_B, calories_burn, calories_consume)

    goalDay = week_goal / 7

    print("The goal per week is ",week_goal)

    iteration = 1

    print("This is iteration ",iteration," expected BW change is ",expected_bw_change," and the goal per day is ",goalDay)

    if expected_bw_change > goalDay:
        calorie_consume_minus = -2
        calorie_burn_plus = 4.5
    elif expected_bw_change < goalDay:
        calorie_consume_minus = 1
        calorie_burn_plus = -4

    while not ((goalDay - .01) < (expected_bw_change) < (goalDay +.01)):

        calories_consume += calorie_consume_minus
        calories_burn += calorie_burn_plus

        calories_consume = max(calorie_consume_lower_limit, calories_consume)
        calories_consume = min(calorie_consume_upper_limit, calories_consume)

        calories_burn = max(calorie_burn_lower_limit, calories_burn)
        calories_burn = min(calorie_burn_upper_limit, calories_burn)

        expected_bw_change = testEquationAvg(var_A, var_B, calories_burn, calories_consume)

        iteration += 1
        print("Iteration# ",iteration," expected BW change per day is ",expected_bw_change," with cal- ",calories_burn," cal+ ",calories_consume," the goal per day is ",goalDay)

        if iteration > 300:
                break

    calories_consume = int(calories_consume)
    calories_burn = int(calories_burn)

    results = {'cal_plus': calories_consume, 'cal_minus': calories_burn, 'var_A' : var_A, 'var_B' : var_B}
    return results

def process_data(weight_days, calorie_days, start_day, week_goal, user_id):
    print(start_day)
    start_day_polished = start_day
    weight_present_dates_start = start_day_polished

    weight_past_dates_start = start_day_polished - datetime.timedelta(days=calorie_days)

    print("Start day ",start_day_polished)

    user = db.User.get(db.User.id == user_id)

    # Not using this code because cant figure out how to select a prarticular row from a query

    #user_logs = db.DayData.select().where(db.DayData.user == user)
    #for log in user_logs:
        #print("The log dates selected are ",log.date)

    weight_present_logs = []
    weight_past_logs = []
    calorie_plus = []
    calorie_minus = []

    for x in range(weight_days):
        weight_present_date = weight_present_dates_start - datetime.timedelta(days=x)
        day_data = db.DayData.get(db.DayData.user == user and db.DayData.date == weight_present_date.strftime("%Y-%m-%d"))
        weight_present_logs.append(day_data.dayweight)
        print("On day ",weight_present_date.strftime("%Y-%m-%d")," the weight is ",day_data.dayweight," and x is ",x)

    print(weight_present_logs)

    for x in range(weight_days):
        weight_past_date = weight_past_dates_start - datetime.timedelta(days=x)
        day_data = db.DayData.get(db.DayData.user == user and db.DayData.date == weight_past_date.strftime("%Y-%m-%d"))
        weight_past_logs.append(day_data.dayweight)
        #print("On day ",weight_past_date.strftime("%Y-%m-%d")," the weight is ",day_data.dayweight," and x is ",x)

    print(weight_past_logs)

    for x in range(calorie_days):
        start_day = start_day_polished - datetime.timedelta(days=x)
        day_data = db.DayData.get(db.DayData.user == user and db.DayData.date == start_day.strftime("%Y-%m-%d"))
        calorie_plus.append(day_data.caloriesPlus)
        calorie_minus.append(day_data.caloriesMinus)
        #print("On day ",start_day.strftime("%Y-%m-%d")," calorie plus ",day_data.caloriesPlus," and calorie minus ",day_data.caloriesMinus," and x is ",x)
    
    #print(calorie_plus)
    #print(calorie_minus)

    bw_change = avg(weight_present_logs) - avg(weight_past_logs)
    bw_present = avg(weight_present_logs)

    calorie_plus_avg = avg(calorie_plus)
    calorie_minus_avg = avg(calorie_minus)

    #print("Bodyweight change is ",bw_change," and present bw is ",bw_present)

    bw_change_per_day = bw_change / calorie_days

    results = doFitMindMagic(calorie_plus, calorie_minus, bw_change_per_day, bw_present, week_goal)

    # Only leave 4 places after a dot
    bw_change = "{0:.3f}".format(bw_change)
    bw_change_per_day = "{0:.3f}".format(bw_change_per_day)

    calorie_plus_avg = int(calorie_plus_avg)
    calorie_minus_avg = int(calorie_minus_avg)

    results.update( {'week_goal' : week_goal, 'bw_change' : bw_change, 'bw_change_per_day' : bw_change_per_day, 'bw_present' : bw_present,
        'calorie_plus_avg' : calorie_plus_avg, 'calorie_minus_avg' : calorie_minus_avg}
        )

    print(results)
    return results




def generate_goals(bw_goal, user_id):

    user = db.User.get(db.User.id == user_id)
    user_weight = user.weight
    user_height = user.height
    user_gender = user.gender
    user_age = user.age_calculated()

    calories_consume_benchmark = get_basal_metabolic_rate(user_weight, user_height, user_gender, user_age)

    #print("BW goal is ", bw_goal)
    calories_burn_benchmark = calories_consume_benchmark + (7700 * bw_goal) / 7

    # Way to compensate for FitBit Error
    calories_burn_benchmark *= fitbit_error

    results = {'cal_plus_goal': calories_consume_benchmark, 'cal_minus_goal': calories_burn_benchmark, 'bw_present': user_weight}
    return results

def generate_goals2(user_weight, user_height, user_age, user_gender, bw_goal):

    calories_consume_benchmark = get_basal_metabolic_rate(user_weight, user_height, user_gender, user_age)

    #print("BW goal is ", bw_goal)

    calories_burn_benchmark = calories_consume_benchmark + (7700 * bw_goal) / 7

    # Way to compensate for FitBit Error
    calories_burn_benchmark *= fitbit_error

    calories_consume_benchmark = int(calories_consume_benchmark)
    calories_burn_benchmark = int(calories_burn_benchmark)

    results = {'cal_plus_goal': calories_consume_benchmark, 'cal_minus_goal': calories_burn_benchmark, 'bw_present': user_weight}
    return results