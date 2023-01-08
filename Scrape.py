from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException  
import time
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains

def scrape_classes():

    df = pd.DataFrame(columns=['Campus','Year','Season','Department','Course code','Name','Credits','Pre-reqs','Co-reqs','Restrictions','Pre-req string','Description','URL'])

    browser = webdriver.Chrome()
    browser.get("https://courses.students.ubc.ca/cs/courseschedule")
    browser.find_element(By.XPATH,"//button[contains(text(),'Campus')]").click()
    time.sleep(1)
    elem_campuses = browser.find_elements(By.XPATH,"//ul[@class='dropdown-menu']//descendant::a[contains(@title,'UBC')]")
    i = 0
    string_campuses = list()
    for elem_campus in elem_campuses:
        string_campuses.append(elem_campus.get_attribute("title"))

    for string_campus in string_campuses:      
        browser.find_element(By.XPATH,"//button[contains(text(),'Session')]").click()
        time.sleep(1)
        elem_sessions = browser.find_elements(By.XPATH,"//ul[@class='dropdown-menu']//descendant::a[contains(@title,'20')]")

        string_sessions = list()
        for elem_session in elem_sessions:
            string_sessions.append(elem_session.text)

        for string_session in string_sessions:
            season = string_session.split(" ")[1][0]
            year = string_session.split(" ")[0]
            browser.get("https://courses.students.ubc.ca/cs/courseschedule?tname=subj-all-departments&sessyr={}&sesscd={}&campuscd={}&pname=subjarea".format(year,season,string_campus))
            
            try:
                elem_depts = browser.find_elements(By.XPATH,"//tr[contains(@class,'section')]")        
            except NoSuchElementException:
                continue
            
            string_depts = list()
            for elem_dept in elem_depts:
                string_depts.append(elem_dept.text)

            for string_dept in string_depts:             
                if '*' in string_dept:
                    continue
                dept_code = string_dept.split(" ")[0]
                browser.get("https://courses.students.ubc.ca/cs/courseschedule?tname=subj-department&sessyr={}&sesscd={}&campuscd={}&dept={}&pname=subjarea".format(year,season,string_campus,dept_code))
                elem_courses = browser.find_elements(By.XPATH,"//tr[contains(@class,'section')]")

                string_courses = list()
                for elem_course in elem_courses:
                    string_courses.append(elem_course.text)


                for string_course in string_courses:
                    course_num = string_course.split(" ")[1]
                    url = "https://courses.students.ubc.ca/cs/courseschedule?sesscd={}&campuscd={}&pname=subjarea&tname=subj-course&course={}&sessyr={}&dept={}".format(season,string_campus,course_num,year,dept_code)
                    browser.get(url)

                   
                    pre_reqs = list()
                    pre_req_str = ""
                    try:
                        elem_pre_reqs = browser.find_elements(By.XPATH,"//p[contains(text(),'Pre-reqs:')]//descendant::a")
                        pre_req_str = browser.find_element(By.XPATH,"//p[contains(text(),'Pre-reqs:')]").text
                        for elem_pre_req in elem_pre_reqs:
                            pre_reqs.append(elem_pre_req.text)
                    except:
                       pass

                    co_reqs = list()
                    try:
                        elem_co_reqs = browser.find_elements(By.XPATH,"//p[contains(text(),'Co-reqs:')]//descendant::a")
                        for elem_co_req in elem_co_reqs:
                            co_reqs.append(elem_co_req.text)
                    except:
                       pass
                    
                    name = browser.find_element(By.XPATH,"//h4").text
                    desc = browser.find_element(By.XPATH,"//div[@role = 'main']/descendant::p[1]").text
                    credits = browser.find_element(By.XPATH,"//p[contains(text(),'Credits:')]").text.split(':')[1]

                    try:
                        restrictions = browser.find_element(By.XPATH,"//li[contains(text(),'restricted to students')]").text
                    except:
                       pass

                    str_co_reqs = ""

                    for co_req in co_reqs:
                        str_co_reqs = str_co_reqs + co_req + ","

                    
                    str_pre_reqs = ""

                    for pre_req in pre_reqs:
                        str_pre_reqs = str_pre_reqs + pre_req + ","

                    df.loc[len(df.index)]=[string_campus,year,season,dept_code,course_num,name,credits,str_pre_reqs[:-1],str_co_reqs[:-1],restrictions,pre_req_str,desc,url]
                    print(str(round((i/9657)*100,2)) + "%")
                    i +=1
                    
    df.to_csv("courses.csv")

scrape_classes()

