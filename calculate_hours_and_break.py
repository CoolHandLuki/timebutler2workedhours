import pandas as pd
import holidays
from datetime import datetime, timedelta

def read_csv_with_dates(csv_file):
    df = pd.read_csv(csv_file, sep=';', usecols=['Von', 'Bis', 'Halber Tag'], encoding='ISO-8859-1')
    df['Von'] = pd.to_datetime(df['Von'], dayfirst=True)
    df['Bis'] = pd.to_datetime(df['Bis'], dayfirst=True)
    return df

def date_range_includes(df, date):
    for _, row in df.iterrows():
        if row['Von'] <= date <= row['Bis']:
            return row['Halber Tag']
    return None

def calculate_work_hours(firstdate, lastdate, sick_days_csv, vacation_days_csv, state_code):
    sick_days = read_csv_with_dates(sick_days_csv)
    vacation_days = read_csv_with_dates(vacation_days_csv)
    
    start_date = datetime.strptime(firstdate, '%Y-%m-%d')
    end_date = datetime.strptime(lastdate, '%Y-%m-%d')
    
    de_holidays = holidays.Germany(prov=state_code)
    
    output = pd.DataFrame(columns=['date', 'weekday', 'hours worked', 'hours break', 'work_start', 'work_end', 'break_start', 'break_end', 'comment'])
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        weekday = current_date.strftime('%A')
        hours_worked = 8
        hours_break = 0.5
        work_start = None
        work_end = None
        break_start = None
        break_end = None
        comment = 'regular work day'
        
        if current_date.weekday() >= 5:
            comment = 'weekend'
            hours_worked = 0
            hours_break = 0
        elif date_str in de_holidays:
            comment = 'public holiday'
            hours_worked = 0
            hours_break = 0
        else:
            sick_day_type = date_range_includes(sick_days, current_date)
            vacation_day_type = date_range_includes(vacation_days, current_date)

            if sick_day_type is not None:
                comment = 'sick leave'
                if sick_day_type == 'ja':
                    comment += ' (half day)'
                    hours_break = 0
                    hours_worked = 4
                else:
                    hours_break = 0
                    hours_worked = 0
                    
            elif vacation_day_type is not None:
                comment = 'vacation'
                if vacation_day_type == 'ja':
                    comment += ' (half day)'
                    hours_break = 0
                    hours_worked = 4
                else:
                    hours_break = 0
                    hours_worked = 0

        # Calculate start and end times
        if hours_worked > 0:
            work_start = datetime(current_date.year, current_date.month, current_date.day, 8, 0)  # 8 AM CEST
            work_end = work_start + timedelta(hours=hours_worked + hours_break)
        
        if hours_worked > 4:
            break_start = work_start + timedelta(hours=4)
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
calculate_work_hours('2022-10-01', '2022-12-31', 'inputs/2022_sick_days.csv', 'inputs/2022_vacation_days.csv', 'BW')