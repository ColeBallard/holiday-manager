# Holiday Manager

## **Description**

Python command line menu which automatically scrapes a list of holidays and their dates. User has the option to add and remove holidays, save the holiday list to a json file, and view holidays in a week-period with corresponding forecast if the user selects the current week.

Uses [timeanddate.com](https://www.timeanddate.com/holidays/us/) for holiday data and [OpenWeather API](https://openweathermap.org/api) for weather data.

## **Usage**

1. Clone the repository.

```shell
git clone https://github.com/ColeBallard/holiday-manager
```

2. Install the latest version of python. [Downloads.](https://www.python.org/downloads/)

3. Install dependencies.

```shell
pip install beautifulsoup4
pip install requests
```

4. [Create OpenWeather account.](https://home.openweathermap.org/users/sign_up)

5. Create config.py file.

```shell
touch data/config.py
```

6. Fill in config.py file with your own variable values.

```dosini
scraped = 
locationConfig = 
locationJSON = 
currentYear = 
openWeatherKey = 
```

7. Run the python file.

```shell
C:/Users/YourName/holiday-manager/main.py
```

## **Contribution**

If you have an idea or want to report a bug, please create an issue.

## **[Contact](https://coleb.io/contact)**
