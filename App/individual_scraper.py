from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
import glob
import csv

from BaiduApp.scroll import auto_scroll

# Get all of the mentioned education details
def get_education(item):
  try:
    institute = item.find("h3", class_ = 'pv-entity__school-name t-16 t-black t-bold').text

    try:
      degree = item.find("p", class_ = 'pv-entity__secondary-title pv-entity__degree-name t-14 t-black t-normal').find_all("span")[1].text
    except:
      degree = ''
  
    data = []
    data.append(institute)
    data.append(degree)

  except:
    data = []

  return data

# Gets detail of an experience
def get_detail(value):
  try:
    interval = value.find("h4", class_ = 'pv-entity__date-range t-14 t-black--light t-normal').find_all("span")[1].text
    duration = value.find("h4", class_ = 't-14 t-black--light t-normal').find_all("span")[1].text
    data = []
    try:
      location = value.find("h4", class_ = 'pv-entity__location t-14 t-black--light t-normal block').find_all("span")[1].text
    except:
      location = "Location Not Mentioned"
    
    data.append(interval)
    data.append(duration)
    data.append( location )
  except:
    data = []
  return data

# If there is a single position/role in a particular company
def single_role(experience):
  try:
    title   = experience.find("h3", class_ = 't-16 t-black t-bold').text
    company = experience.find("p", class_ = 'pv-entity__secondary-title t-14 t-black t-normal').text.strip()
    detail  = get_detail(experience)
    company = company.splitlines()
    data = []
    data.append(company[0])
    data.append(title)
    data.append(detail[:2])
    data.append(detail[2])
  except:
    data = []
  return data

# If there is more than one job position in the same company
def multi_role(experience):
  try:  
    all_roles = []
    data = []
    company = experience.find("h3", class_ = 't-16 t-black t-bold').find_all("span")[1].text
    multi_roles = experience.find_all("li", class_ = 'pv-entity__position-group-role-item')

    for role in multi_roles:
      role_title = role.find("h3", class_ = 't-14 t-black t-bold').find_all("span")[1].text 
      detail = get_detail(role)
      all_roles.append(role_title)
      all_roles.append(detail[:1])
      all_roles.append(detail[2])

    company = company.splitlines()

    data.append(company[0])
    data.append(all_roles)
  except:
    data = []

  return data


def Location(driver):
    content = driver.find_element_by_tag_name('main')
    result = content.get_attribute('innerHTML')
    soup = BeautifulSoup(result, 'html.parser')

    auto_scroll(driver)

    try:
      location = soup.find("li", class_ = 't-16 t-black t-normal inline-block').text.strip()
    except:
      location = 'Not Found'
    
    try:
        driver.find_element_by_class_name('pv-profile-section__card-action-bar').click()
    except:
        try:
            driver.find_element_by_xpath('/html/body/div[8]/div[3]/div/div/div/div/div[2]/main/div[2]/div[6]/div/section/div[2]/button').click()
        except:
            try:
                driver.find_element_by_css_selector('button.pv-profile-section__card-action-bar')
            except:
                pass

    time.sleep(3)
    
    # To click all the show more records button in the page
    try:
        see_more_list = driver.find_elements_by_class_name('pv-profile-section__see-more-inline')
        for more in see_more_list:
            more.click()
            time.sleep(3)
    except:
        pass

    return location


def Experience(driver):
    try:
      experiences = []
      # Extracting experiences 
      experience_section = driver.find_element_by_class_name('experience-section')
      experience_section = BeautifulSoup(experience_section.get_attribute('innerHTML'), 'html.parser')
      experience_list    = experience_section.find_all("li", class_ = 'pv-entity__position-group-pager pv-profile-section__list-item ember-view')
      for experience in experience_list:
          try:
              data = single_role(experience)
              experiences.append(data)
          except:
              data = multi_role(experience)
              experiences.append(data)
    except:
        experiences = []

    return experiences 
      
def Education(driver):

    try:
        # Extracting education
        education = []
        education_section = driver.find_element_by_class_name('education-section')
        education_section = BeautifulSoup(education_section.get_attribute('innerHTML'), 'html.parser')
        education_list    = education_section.find_all("li", class_ = 'pv-profile-section__list-item pv-education-entity pv-profile-section__card-item ember-view')
        for item in education_list:
            data = get_education(item)
            education.append(data)
    except:
        education = []

    return education 
      

def Skill(driver):    
      
    time.sleep(10)
        
    try:
        content = driver.find_element_by_tag_name('body')
        result = content.get_attribute('innerHTML')
        soup = BeautifulSoup(result, 'html.parser')
        skills_list = soup.find_all("span", class_ = 'pv-skill-category-entity__name-text')
        skill_list = []
        print(skills_list)
        for skill in skills_list:
            skill_list.append(skill.text)
    except:
        try:
            skills_list = driver.find_elements_by_css_selector('#ember1129 > span')
            skill_list = []
            for skill in skills_list:
                skill_list.append(str(skill.text).strip('\n').strip())
        except:
            skill_list = []


    return skill_list  
      



              
        

