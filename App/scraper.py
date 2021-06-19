# import web driver
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import urllib.request
import csv
import pandas as pd
import math
import random
from App.app import db
from App.models import Founders, Rejected
import datetime
import unicodedata
import os

from App.individual_scraper import Location,Skill,Experience,Education
from App.scroll import auto_scroll

def getbasicinfo(driver, currentuser):
    links = ['https://www.linkedin.com/search/results/people/?facetGeoUrn=%5B%22103644278%22%5D&facetIndustry=%5B%2212%22%5D&origin=FACETED_SEARCH&title=Founder','https://www.linkedin.com/search/results/people/?facetCurrentCompany=%5B%221109086%22%2C%221131902%22%2C%2218225241%22%2C%2218454116%22%2C%222120790%22%2C%2224732%22%2C%22883230%22%2C%22963818%22%5D&facetIndustry=%5B%2212%22%2C%2214%22%2C%22124%22%2C%22139%22%5D&origin=FACETED_SEARCH&title=founder','https://www.linkedin.com/search/results/people/?company=startup&facetGeoUrn=%5B%22103644278%22%5D&facetIndustry=%5B%22124%22%2C%2212%22%5D&origin=FACETED_SEARCH&title=founder','https://www.linkedin.com/search/results/people/?company=startup&facetGeoUrn=%5B%22103644278%22%5D&facetIndustry=%5B%2212%22%5D&origin=FACETED_SEARCH&title=Founder','https://www.linkedin.com/search/results/people/?facetGeoUrn=%5B%22103644278%22%5D&facetIndustry=%5B%2212%22%5D&origin=FACETED_SEARCH&title=Founder','https://www.linkedin.com/search/results/people/?facetCurrentCompany=%5B%221109086%22%2C%221131902%22%2C%2218225241%22%2C%2218454116%22%2C%222120790%22%2C%2224732%22%2C%22883230%22%2C%22963818%22%5D&facetIndustry=%5B%2212%22%2C%2214%22%2C%22124%22%2C%22139%22%5D&origin=FACETED_SEARCH&title=founder']
    screening_title = ["Biotechnology", "Structural Biology", "Bioinformatics"]
    screening_past_role = ["machine learning", "professor", "researcher", "senior scientist", "artificial intelligence",  "research scientists", "applied research scientists", "visiting faculty researcher"]
    screening_past_company = ["Google Brain", "Google Health", "Verily", "Deepmind", "Flatiron Health", "Zymergen", "Babylon Health UK", "IBM Watson Health", "Oncora Medical", "CloudMedX Health", "Corti", "Butterfly Network", "Deep Genomics"]
    screening_schools = ["Stanford", "UC Berkeley", "MIT", "Harvard", "UPenn", "Cornell", "Columbia", "USC", "UMich", "Tel Aviv", "Indian Institute of Technology"] 
    screening_degree = ["Structural Biology","Biology","Computer Science","Artificial Intelligence","Bioinformatics"]
    screening_skills = ["Structural biology", "sequencing", "omics", "RNA", "DNA", "Protein", "genomics", "bioinformatics"]
    msg = []
    for url in links:
        driver.get(url)
        page_scrape = 0
        page = 1
        time.sleep(10)
        while True:
            try_to_find_page = 0
            while True:
                try_to_find_page = try_to_find_page + 1
                # Finding Page Number
                if page == 1:
                    try:
                        number_str = driver.find_element_by_xpath('/html/body/div[8]/div[3]/div/div[2]/div/div/div/div/div[1]').text
                        number = math.ceil(int(''.join(list(filter(str.isdigit, number_str))))/10)
                        break
                    except:
                        try:
                            number_str = driver.find_element_by_xpath('/html/body/div[8]/div[3]/div/div[2]/div/div[2]/div/div/div/div/h3').text
                            number = math.ceil(int(''.join(list(filter(str.isdigit, number_str))))/10)
                            break
                        except:
                            try:
                                number_str = soup.find("h3",{"class":"search-results__total t-14 t-black--light t-normal pl5 clear-both pt4 pb0"}).text
                                number = math.ceil(int(''.join(list(filter(str.isdigit, number_str))))/10)
                                break
                            except:
                                if try_to_find_page == 10:
                                    number = 1
                                    break
                                else:
                                    pass
                else:
                    number = 1
                    break
            # To avoid finding the total page number in each iteration
            page = page + 1
            time.sleep(15)
            # Searching only one page per link
            if page_scrape == 1:
                break
            # Since linkedin only shows 1000 result there is only 100 pages
            if number > 100:
                number = 100
            page_number = random.randint(1,number)
            # Creating Search URL
            search_url = url + '&page=' + str(page_number)
            driver.get(search_url) 
            # Scrolling the page
            auto_scroll(driver)                  
            main_page = driver.find_element_by_xpath('/html/body')
            # Creating soup for hadling some errors
            soup = BeautifulSoup(main_page.get_attribute("innerHTML"), 'html.parser')
            profile_details = soup.findAll("div", {"class": "search-result__info pt3 pb4 ph0"})
            if len(profile_details) < 1:
                profile_details = soup.findAll("div", {"class" : "entity-result__item"})
                
            # Finding Basic Details of the potential founder
            for profile_detail in profile_details:
                try:
                    name = profile_detail.find("span",{"class":"name actor-name"}).text
                except:
                    try:
                        name = profile_detail.find("span",{"class": "entity-result__title-text"}).text
                    except:
                        name = "Not found"
                        print('name')
                        continue
                try:
                    link = "https://www.linkedin.com"+str(profile_detail.find("a",{"class":"search-result__result-link ember-view"}, href = True)['href'])
                except:
                    try: 
                        link = str(profile_detail.find("a",{"class":"app-aware-link"}, href = True)['href'])
                    except:
                        link = "Not found"
                        print("link link")
                        continue

                #Checking for duplicates
                exists = db.session.query(Founders.link).filter_by(link=link).scalar() is not None
                if exists == True:
                    print("Passed")
                    continue
                else:
                    
                    pass

                exists = db.session.query(Rejected.link).filter_by(link=link).scalar() is not None
                if exists == True:
                    print("Passed")
                    continue
                else:
                    pass

                # Finding the title
                try:
                    title = profile_detail.find("p",{"class":"subline-level-1 t-14 t-black t-normal search-result__truncate"}).text
                except:
                    title = "Not found"

                driver.get(link)

                # Getting basic informations
                email = "Not Found"
                location = Location(driver)                
                educations = Education(driver)
                experience = Experience(driver)
                
                # Adding screening on basis of when they started the company
                try:
                    validation_yr = experience[0][2]
                except:
                    continue
                if "yr" in str(validation_yr).lower():
                    rejected = Rejected(str(link))
                    db.session.add(rejected)
                    db.session.commit() 
                    continue
                else:
                    pass

                # Adding first screening for past role
                flag = 0
                for i in screening_past_role:
                    if i.lower() in str(experience).lower():
                        flag = 1

                # Scraping skills
                skill_list = Skill(driver)                
                
                # Creating a list of their past company
                past_company = []
                company_count = 0
                for all in experience:
                    company_count += 1
                    if company_count == 1:
                        try:
                            current_company = all[0] + "-" + all[1]
                        except:
                            try: 
                               current_company = all[0] + "-" + str(all[1]) 
                            except:
                                try:
                                    current_company = all[0]
                                except: 
                                    current_company= "Not Found"
                    else:
                        try:
                            past_company.append(all[0] + "-" + all[1])
                        except:
                            try: 
                               past_company.append(all[0] + "-" + str(all[1])) 
                            except:
                                try:
                                    past_company.append(all[0])
                                except:
                                    pass
                
                # Creating a list of their past schools
                education = []
                for all in educations:
                    try:
                        education.append(all[0])
                    except:
                        pass

                added_by = currentuser

                if flag == 0:
                    # Screening based on title
                    for i in screening_title:
                        if i.lower() in str(title).lower():
                            flag = 1 

                #screening based on past company
                if flag == 0:
                    for i in screening_past_company:
                        if i.lower() in str(experience).lower():
                            flag = 1 
                
                # screening based on schools
                if flag == 0:
                    for i in screening_schools:
                        if i.lower() in str(education).lower():
                            flag = 1 

                # Screening based on degrees
                if flag == 0:
                    for i in screening_degree:
                        if i.lower() in str(education).lower():
                            flag = 1 

                # Screening based on skills
                if flag == 0:
                    for i in screening_skills:
                        if i.lower() in str(skill_list).lower():
                            flag = 1 
                # Adding the data if the screening passes
                if flag == 1:
                    founder = Founders(datetime.datetime.today().strftime('%Y-%m-%d'),str(name), str(title), str(location),  str(link), str(email),str(education), str(current_company), str(past_company),str(skill_list),str(added_by), True)
                    db.session.add(founder)
                    db.session.commit() 
                    message = name + ": <a href=" + link + ">Click Here to Visit Profile</a>"
                    msg.append(message)   
                else:
                    rejected = Rejected(str(link))
                    db.session.add(rejected)
                    db.session.commit() 
            page_scrape = page_scrape + 1
    return msg
               

def login(driver,username_gui,password_gui,currentuser):
    url = 'https://www.linkedin.com'
    driver.get(url)
    # Getting the username
    username = driver.find_element_by_xpath('//*[@id="session_key"]')
    username_input= username_gui
    username.send_keys(username_input)

    # Getting the password
    password = driver.find_element_by_xpath('//*[@id="session_password"]')
    password_input = password_gui
    password.send_keys(password_input)
    
    # logging_in
    log_in_button = driver.find_element_by_xpath('//*[@type="submit"]')
    log_in_button.click()  

    #Checking if the email is correct and password is longer than 6 character
    try:        
        password_character_error = driver.find_element_by_xpath('/html/body/main/section[1]/div[2]/form/div[1]/div/p').text
        if password_character_error == "Password must be 6 characters or more.":
            print("Error")
            return ["error"]
        else:
            print("Error")
            return ["error"]              
    except:          
        try:
            error_check = driver.find_element_by_xpath('//*[@id="error-for-password"]').text
            print("Error")
            return ["error"]        
        except:
            pass
    
    msg = getbasicinfo(driver, currentuser)

    return msg

def before_logging(user_name,password, currentuser):
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")  
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('--headless') 
    # driver = webdriver.Chrome(executable_path = os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    driver = webdriver.Firefox()
    msg = login(driver,user_name,password, currentuser)
    if msg == []:
        return "Not added"
    elif msg == ["error"]:
        return "Error"
    else:
        updtmsg = "Hello -<br>" + currentuser+ " scraped linkedin and new founders were found. <br> <ul>."
        for i in msg:
            updtmsg = updtmsg + "<li>"+ i + "</li>"
        updtmsg = updtmsg + "</ul><br>Best, <br>Baidu Team" 
        return updtmsg