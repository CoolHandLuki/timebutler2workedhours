import pandas as pd
import holidays
from datetime import datetime, timedelta
import random

def read_csv_with_dates(csv_file):
    df = pd.read_csv(csv_file, sep=';', usecols=['From', 'To', 'Half a day', 'Type'], encoding='ISO-8859-1')
    df['From'] = pd.to_datetime(df['From'], dayfirst=True)
    df['To'] = pd.to_datetime(df['To'], dayfirst=True)
    return df

def date_range_includes(df, date, type_check):
    for _, row in df.iterrows():
        if row['From'] <= date <= row['To'] and row['Type'] == type_check:
            return row['Half a day']
    return None

def generate_weights(length):
    midpoint = length / 2
    weights = [(x - midpoint)**2 for x in range(length)]
    max_weight = max(weights)
    # Invert weights since we want a bell curve (lower quadratic values for the center)
    weights = [max_weight - weight for weight in weights]
    # Normalize weights to make them more manageable
    total_weight = sum(weights)
    weights = [weight / total_weight for weight in weights]
    return weights

def calculate_work_hours(firstdate, lastdate, days_csv, state_code):
    days_df = read_csv_with_dates(days_csv)
    
    start_date = datetime.strptime(firstdate, '%Y-%m-%d')
    end_date = datetime.strptime(lastdate, '%Y-%m-%d')
    
    de_holidays = holidays.Germany(prov=state_code)
    
    output = pd.DataFrame(columns=['date', 'weekday', 'hours worked', 'hours break', 'work_start', 'work_end', 'break_start', 'break_end', 'comment'])

    # Generate all possible start times and break durations
    start_times = [datetime(start_date.year, start_date.month, start_date.day, hour, minute)
                   for hour in range(7, 10) for minute in (0, 15, 30, 45)]
    break_durations = [0.5, 0.75, 1.0]

    # Generate the weights for start_times to have a more natural distribution
    weights_start_times = generate_weights(len(start_times))
    # Manually assign weights for break durations
    weights_break_durations = [0.7, 0.2, 0.1]
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        weekday = current_date.strftime('%A')
        hours_worked = 8
        hours_break = random.choices(break_durations, weights_break_durations, k=1)[0]  # Randomly choose the break duration based on assigned weights
        work_start = None
        work_end = None
        break_start = None
        break_end = None
        comment = 'regular work day'
        
        # Adjust the comments and hours for weekends, public holidays, sick leaves, and vacations
        if current_date.weekday() >= 5:
            comment = 'weekend'
            hours_worked = 0
            hours_break = 0
        elif date_str in de_holidays:
            comment = 'public holiday'
            hours_worked = 0
            hours_break = 0
        else:
            # Check and adjust for sick leave or vacation days
            sick_day_type = date_range_includes(days_df, current_date, 'Illness') or date_range_includes(days_df, current_date, 'Child ill')
            vacation_day_type = date_range_includes(days_df, current_date, 'Vacation') or date_range_includes(days_df, current_date, 'Company Holidays') or date_range_includes(days_df, current_date, 'Further training')

            if sick_day_type is not None or vacation_day_type is not None:
                hours_break = 0
                if sick_day_type is not None:
                    comment = 'sick leave'
                elif vacation_day_type is not None:
                    comment = 'vacation'
                if sick_day_type == 'yes' or vacation_day_type == 'yes':
                    hours_worked = 4
                    comment += '(half day)'
                else:
                    hours_worked = 0

        if current_date.weekday() < 5 and date_str not in de_holidays:
            # Randomly choose the work start time based on assigned weights for weekdays that are not public holidays
            
            if hours_worked > 0:
                work_start = random.choices(start_times, weights_start_times, k=1)[0]
                work_start = work_start.replace(year=current_date.year, month=current_date.month, day=current_date.day)
                work_end = work_start + timedelta(hours=hours_worked + hours_break)
            
            if hours_worked > 4:
                break_start = work_start + timedelta(hours=4)  # Assuming break starts after 4 hours of work
                break_end = break_start + timedelta(hours=hours_break)
        
        new_row = pd.DataFrame([{
            'date': date_str, 
            'weekday': weekday, 
            'hours worked': hours_worked, 
            'hours break': hours_break, 
            'work_start': work_start.time() if work_start else None, 
            'work_end': work_end.time() if work_end else None, 
            'break_start': break_start.time() if break_start else None, 
            'break_end': break_end.time() if break_end else None, 
            'comment': comment
        }])
        
        output = pd.concat([output, new_row], ignore_index=True)
        
        current_date += timedelta(days=1)
    
    output.to_csv('outputs/work_hours_report.csv', index=False)

# Example usage
calculate_work_hours('2024-01-01', '2024-02-29', 'inputs/2024_sick_and_vacation_days.csv', 'BW')