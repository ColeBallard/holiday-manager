from dataclasses import dataclass, field
import json
from datetime import datetime

from bs4 import BeautifulSoup
import requests

import data.config as config

@dataclass
class Holiday:
    name: str
    date: datetime      
    
    def getWeatherForecast(self, zip):
        response = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?zip={zip},us&appid={config.openWeatherKey}')

        for node in json.loads(response.text)['list']:
            if datetime.strptime(self.date, '%Y-%m-%d').date() == datetime.fromtimestamp(node['dt']).date():
                return node['weather'][0]['description']

        return 'No weather data.'
          
@dataclass           
class HolidayList:
    innerHolidays: list = field(default_factory = list)
   
    def addHoliday(self, holiday):
        self.innerHolidays.append(holiday)

    def findHoliday(self, name, year):
        if year != False:
            return any(holiday.name == name and str(datetime.strptime(holiday.date, '%Y-%m-%d').year) == year for holiday in self.innerHolidays)

        else:
            return any(holiday.name == name for holiday in self.innerHolidays)

    def removeHoliday(self, name, year):
        if year == 'ALL':
            self.innerHolidays = list(filter(lambda holiday: holiday.name != name, self.innerHolidays))

        else:
            self.innerHolidays = list(filter(lambda holiday: holiday.name != name or str(datetime.strptime(holiday.date, '%Y-%m-%d').year) != year, self.innerHolidays))

    def readJSON(self):
        file = open(config.locationJSON)

        for holiday in json.load(file)['holidays']:
            self.innerHolidays.append(Holiday(holiday['name'], holiday['date']))

        file.close()

    def saveToJSON(self):
        holidays = {'holidays':[]}

        for holiday in self.innerHolidays:
            holidays['holidays'].append({'name':holiday.name, 'date':holiday.date})

        file = open(config.locationJSON, 'w')

        json.dump(holidays, file)

        file.close()
    
    def filterHolidaysByWeek(self, year, week):
        if week == 'CURRENT':
            return list(filter(lambda holiday: str(datetime.strptime(holiday.date, '%Y-%m-%d').year) == year and str(datetime.strptime(holiday.date, '%Y-%m-%d').strftime('%V')) == datetime.now().strftime('%V'), self.innerHolidays))

        else:
            if len(week) == 1:
                week = f'0{week}'

            return list(filter(lambda holiday: str(datetime.strptime(holiday.date, '%Y-%m-%d').year) == year and str(datetime.strptime(holiday.date, '%Y-%m-%d').strftime('%V')) == week, self.innerHolidays))

def scrapeHolidays(holidayList):
    for year in range(config.currentYear - 2, config.currentYear + 3):
        response = requests.get(f'https://www.timeanddate.com/holidays/us/{year}')
        tbody = BeautifulSoup(response.text, 'html.parser').find('table', attrs = {'id':'holidays-table'}).find('tbody')

        for row in tbody.find_all('tr'):
            if len(row.find_all()) != 0:
                date = datetime.strftime(datetime.strptime(f'{row.th.string} {year}', '%b %d %Y'), '%Y-%m-%d')
                name = row.select_one('td > a').string

                holidayList.addHoliday(Holiday(name, date))

    print('Scraping successful.')
    print('')

def startupMessage(holidayCount):
    print('Holiday Manager')
    print('===============')
    print(f'There are {holidayCount} holidays stored in the system.')
    print('')

def printMenu():
    print('Menu')
    print('====')
    print('1. Add a Holiday')
    print('2. Remove a Holiday')
    print('3. Save Holiday List')
    print('4. View Holidays')
    print('5. Exit')

def main():
    holidayList = HolidayList()

    holidayList.readJSON()

    if not config.scraped:
        scrapeHolidays(holidayList)

        holidayList.saveToJSON()

        file = open(config.locationConfig, 'r')
        file.seek(16)
        lines = file.readlines()
        lines.insert(0, 'scraped = True')

        file = open(config.locationConfig, 'w')
        file.write(''.join(lines))

    startupMessage(len(holidayList.innerHolidays))

    userExited = False

    while not userExited:
        printMenu()

        menuChoice = input('')

        if menuChoice == '1':
            print('')
            print('Add a Holiday')
            print('=============')

            validName = False
            while not validName:
                name = input('Holiday: ')

                if len(name) != 1:
                    validName = True

                else:
                    print('Holiday name too short.')
                    print('')

            validDate = False
            while not validDate:
                date = input('Date [YYYY-MM-DD]: ')

                try:
                    datetime.strptime(date, '%Y-%m-%d')

                    if int(date[0:4]) > 1500 and int(date[0:4]) < 2500:

                        holiday = Holiday(name, date)
                        
                        if holiday not in holidayList.innerHolidays:
                            holidayList.addHoliday(Holiday)

                            print('')
                            print(f'{name} ({date}) has been successfully added.')
                            print('')

                            validDate = True

                        else:
                            print('')
                            print('Holiday already exists.')
                            print('')
                            
                            validDate = True

                    else:
                        print('Year out of range.')
                        print('')

                except ValueError:
                    print('Incorrect date format.')
                    print('')

        elif menuChoice == '2':
            print('')
            print('Remove a Holiday')
            print('================')

            validYear = False
            while not validYear:
                year = input("Year (type 'all' to remove all instances): ")

                if year.upper() == 'ALL':
                    validYear = True

                elif year.isnumeric():
                    if int(year) > 1500 and int(year) < 2500:
                        validYear = True

                    else:
                        print('Year out of range.')

                else:
                    print('Invalid year.')

            validName = False
            while not validName:
                name = input('Holiday: ')

                if year.upper() == 'ALL':

                    if holidayList.findHoliday(name, False):
                        holidayList.removeHoliday(name, year.upper())
                        print('')
                        print(f'{name} has been successfully removed.')
                        print('')
                        validName = True

                    else:
                        print('Holiday could not be found.')

                else:

                    if holidayList.findHoliday(name, year):
                        holidayList.removeHoliday(name, year)
                        print('')
                        print(f'{name} has been successfully removed.')
                        print('')
                        validName = True

                    else:
                        print('Holiday could not be found.')

        elif menuChoice == '3':
            print('')
            print('Save Holiday List')
            print('=================')

            validChoice = False
            while not validChoice:
                choice = input('Are you sure you want to save your changes [y/n]?: ').lower()

                if choice == 'y':
                    holidayList.saveToJSON()
                    print('')
                    print('File successfully updated.')
                    print('')
                    validChoice = True

                elif choice =='n':
                    print('')
                    validChoice = True

                else:
                    print('Please enter a valid choice.')

        elif menuChoice == '4':
            print('')
            print('View Holidays')
            print('=============')

            validYear = False
            while not validYear:
                year = input("Year: ")

                if year.isnumeric():
                    if int(year) > 1500 and int(year) < 2500:
                        validYear = True

                    else:
                        print('Year out of range.')

                else:
                    print('Invalid year.')

            validWeek = False
            while not validWeek:
                if year == str(config.currentYear):
                    week = input("Week [1-52, type 'current' to view current week]: ")

                else:
                    week = input("Week [1-52]: ")
                
                if week.isnumeric():
                    if int(week) >= 1 and int(week) <= 52:
                        print('')
                        validWeek = True

                    else:
                        print('Week out of range.')

                elif week.upper() == 'CURRENT' and year == str(config.currentYear):
                    validChoice = False
                    while not validChoice:
                        weatherChoice = input('Display weather [y/n]?: ').lower()

                        if weatherChoice == 'y':
                            validZip = False
                            while not validZip:
                                zip = input('Zip code: ')

                                if zip.isnumeric() and len(zip) == 5:
                                    print('')
                                    validZip = True

                                else:
                                    print('Please enter a valid zip code.')

                            validChoice = True

                        elif weatherChoice =='n':
                            validChoice = True

                        else:
                            print('Please enter a valid choice.')

                    validWeek = True

                else:
                    print('Invalid week.')

            holidaysByWeek = holidayList.filterHolidaysByWeek(year, week.upper())

            if len(holidaysByWeek) == 0:
                print(f'Holidays for {year} Week {week}.')
                print('=========================')
                print('No holidays during this week.')
                print('')
            
            elif week.upper() == 'CURRENT' and weatherChoice == 'y':
                print('Holidays and Weather for the Current Week')
                print('=========================================')

                for holiday in holidaysByWeek:
                    print(f'{holiday.name} ({holiday.date}) - {holiday.getWeatherForecast(zip)}')

                print('')

            else:
                print(f'Holidays for {year} Week {week}.')
                print('=========================')

                for holiday in holidaysByWeek:
                    print(f'{holiday.name} ({holiday.date})')

                print('')

        elif menuChoice == '5':
            tempHolidayList = HolidayList()

            tempHolidayList.readJSON()

            if tempHolidayList.innerHolidays != holidayList.innerHolidays:
                changes = True

            else:
                changes = False

            validChoice = False
            while not validChoice:
                print('')
                
                if changes:
                    print('You have unsaved changes.')
                
                choice = input('Are you sure you want to exit [y/n]?: ').lower()

                if choice == 'y':
                    print('')
                    print('Goodbye.')
                    userExited = True
                    validChoice = True

                elif choice =='n':
                    print('')
                    validChoice = True

                else:
                    print('Please enter a valid choice.')

        else:
            print('Please enter a valid menu choice.')

if __name__ == '__main__':
    main()
