# -*- coding: utf-8 -*-
"""
@author: Ayon Ghosh
"""
# Importing the necessary Libraries
from flask_cors import CORS,cross_origin
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import requests
import os
import time
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')  # route for redirecting to the home page
@cross_origin()
def home():
    return render_template('index.html')

@app.route('/searchImages', methods=['GET','POST'])

def searchImages():
    if request.method == 'POST':
        print("entered post")
        search_criteria = request.form['keyword'].replace(' ','') # assigning the value of the input keyword to the variable keyword

    else:
        print("did not enter post")
    print('printing = ' + search_criteria)

    driver_path = './chromedriver'
    sleep_between_interactions = 0.5
    target_path = './target_image'
    #search_criteria = input("enter the search item: ").replace(' ', '')
    #print(search_criteria)

    class imageScrapperUtilities:
        def __init__(self, target_path):
            self.target_path = target_path

        def emptyTargetDir(self):
            list_of_jpg_files = []
            list_of_files = os.listdir(self.target_path)
            if len(list_of_files) > 0:
                for i in list_of_files:
                    if 'jpg' in i:
                       os.remove(f"./{self.target_path}/" + i)
                    else:
                        print('error in deleting')


    class fetchAndSaveImage:
        def __init__(self, sleep_between_interactions, target_path, search_criteria, driver_path):
            self.sleep_between_interactions = sleep_between_interactions
            self.driver_path = driver_path
            self.target_path = target_path
            self.search_criteria = search_criteria
            self.driver = webdriver.Chrome(executable_path=self.driver_path)
            self.search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img".format(
                q=search_criteria)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            print(self.search_url)

        def gatherImageSrc(self):
            self.driver.get(self.search_url)
            all_posts = self.driver.find_elements_by_class_name("Q4LuWd")
            print(len(all_posts))
            self.image_url_list = []
            for post in all_posts[0:20]:
                try:
                    post.click()
                    time.sleep(sleep_between_interactions)

                except Exception:
                    continue
                print('----------------')
                actual_images = self.driver.find_elements_by_class_name('n3VNCb')
                for actual_image in actual_images:
                    if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                        self.image_url_list.append(actual_image.get_attribute('src'))
            print(self.image_url_list)
            print('$$$$$$$$$$$')
            print(len(self.image_url_list))
            return self.image_url_list

        def saveImage(self):
            counter = 0
            for image in self.image_url_list:
                image_content = requests.get(image).content
                f = open(os.path.join(self.target_path, f"{self.search_criteria}" + "_" + str(counter) + ".jpg"), 'wb')
                f.write(image_content)
                f.close()
                counter = counter + 1




    def search_and_download(target_path, sleep_between_interactions, search_criteria, driver_path):
        # with webdriver.Chrome(executable_path=driver_path) as driver:
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        imageScrapperUtilitiesObject = imageScrapperUtilities(target_path)
        fetchAndSaveImageObject = fetchAndSaveImage(sleep_between_interactions, target_path, search_criteria, driver_path)
        imageScrapperUtilitiesObject.emptyTargetDir()
        fetchAndSaveImageObject.gatherImageSrc()
        fetchAndSaveImageObject.saveImage()


    driver_path = './chromedriver'
    sleep_between_interactions = 0.5
    target_path = './static'
    search_and_download(target_path,sleep_between_interactions,search_criteria,driver_path)

    list_of_files = os.listdir(target_path)
    print("We have downloaded ", len(list_of_files), "images of " + search_criteria + " for you")


    try:
        if (len(list_of_files) > 0):  # if there are images present, show them on a wen UI
            return render_template('showImage.html', user_images=list_of_files)
        else:
            return "Please try with a different string"  # show this error message if no images are present in the static folder
    except Exception as e:
        print('no Images found ', e)
        return "Please try with a different string"





if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8000) # port to run on local machine
    app.run(debug=True) # to run on cloud
