# timebutler2workedhours
A program that takes CSV exports from the software timebutler and calculates hours worked based on those

# Installation

Clone the repository `git clone https://github.com/CoolHandLuki/timebutler2workedhours.git`

Change into the directory `cd timebutler2workedhours`

The dependencies inside the requirements.txt need to be installed. It is best practice to do so inside a virtual environment. 

Ensure that pip is installed. On Debian/Ubuntu do `sudo apt-get update && sudo apt-get install python3-pip`

Ensure that venv is installed `pip install venv`. 

Create a virtual environment `python3 -m venv tb2wh-env`

Activate the virtual environment `source tb2wh-env/bin/activate`

Install the dependencies `pip install -r requirements.txt`

# Prepare the Inputs
Download the CSV exports for sick and vacation days from timebutler, place them inside the /inputs directory

# Adjust the code
Open 'calculate_hours_and_break.py' and adjust the last line to fit your circumstances:
`calculate_work_hours('2022-10-01', '2022-12-31', 'inputs/2022_sick_days.csv', 'inputs/2022_vacation_days.csv', 'BW')`

The first argument is the first day (including) from which to calculate hours worked.
The second argument is the last day (including) up to which to calculate hours worked.
The third argument is the relative filepath to the CSV file containing the sick days.
The fourth argument is the relative filepath to the CSV file containing the vacation days.
The fifth argument is the country code for the German state you're in used to calculate public holidays.

# Run the code
`python calculate_hours_and_break.py`

The result should be inside the /outputs directory.
