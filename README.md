# iracing_ai_helper

Project Plan:
All-in-1 Race manager + AI Season tracker for iRacing
- Season Tracker
    - Reads locally designated season and roster files
    - Uses driver, car, and season info stored in a database to allow for customization of AI skills on a race by race basis using defined parameters
    - View results on a single race basis
    - View point standings across the season
    - Handles playoff eligibility
- Race Manager
    - Randomly assess pre-race penalties, such as unapproved adjustments or failed inspection
        - Apply proper racetime penalty when applicable
    - Allow more cars to qualify than desired field size, eliminating the slowest
    - In-race randomization, tracking, and enforcement of pit-road/pit-stop penalties
    - In-race stage management
    - Extensive output of race result data, can be automatically fed into Season Tracker