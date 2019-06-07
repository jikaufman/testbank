import os
import sys
import requests
from lxml import html

if __name__ == "__main__":

    # login details, handled by bash script
    username = sys.argv[1]
    password = sys.argv[2]
    
    # necessary urls
    login_url = 'https://upe.seas.ucla.edu/auth/login'
    testbank_url = 'https://upe.seas.ucla.edu/testbank'

    # establish connection
    session = requests.session()

    # get xpath tree from login page
    page = session.get(login_url)
    tree = html.fromstring(page.content)

    # get CSRF Middleware token from login page, necessary to keep connection
    token = tree.xpath('//*[@id="login"]/form/fieldset/div[1]/input/@value')[0]
    
    # login details to POST
    payload = {
        'username' : username,
        'password' : password,
        'csrfmiddlewaretoken' : token,
        'Submit' : 'Login'
    }

    # get html tree from testbank website
    result = session.post(login_url, data = payload, headers = dict(referer=login_url))
    testbank_page = session.get(testbank_url, headers=dict(referer=testbank_url))
    tree = html.fromstring(testbank_page.content)

    # names of UCLA classes included in testbank, used for organizing files
    classes_path = '/html/body/div[2]/div/div/table/tbody/tr'
    classes_list = tree.xpath(classes_path + '/th/text()')

    # used to associate a course with its subsequent test
    # download files into the course_name directory until course_name is updated
    course_name = ''

    if not os.path.exists('testbank/'):
        os.mkdir('testbank/')
        print("Testbank directory 'testbank/' created")
    else:
        print("Testbank directory 'testbank/' already exits")

    for i in range(2025): # 2025 elements in page until the last test

    	# data for each test, as well as the link to the pdf download
        test_details_path = classes_path + '[' + str(i) + ']/td'
        test_details_list = tree.xpath(test_details_path + '/text()')
        pdf_link_path = test_details_path + '[5]'
        pdf_link_list = tree.xpath(pdf_link_path + '/a/@href')

        # details extracted from the data for each test. used for sorting and naming
        test_type = tree.xpath(test_details_path + '[1]/text()')
        test_num = tree.xpath(test_details_path + '[2]/text()')
        test_date = tree.xpath(test_details_path + '[3]/text()')
        test_prof = tree.xpath(test_details_path + '[4]/text()')
        class_name = tree.xpath(classes_path + '[' + str(i) + ']/th/text()')

        # edge cases. Professor name N/A corrupts filepath with ','
        # could make code more general to change all / to -. TODO...
        # works with specific set of data in June 2019
        if (test_prof == ['N/A']):
            test_prof[0] = "NA"
        if (test_prof == ['Jansma/Burns']):
            test_prof[0] = 'Jansma-Burns'

        # update class name and create directories with the class name in 
        # the current directory
        if (class_name):
            course_name = class_name
            course_path = 'testbank/' + str(course_name[0])
            if not os.path.exists(course_path):
                os.mkdir(course_path)
                print ("Directory " + course_path + " created")
            else:
                print("Directory " + course_path + " already exists")

        # if the pdf link exists, create the professor directory if necessary,
        # name the file, and download the file into the correct directory
        if (pdf_link_list):
            
            pdf_url = 'https://upe.seas.ucla.edu' + str(pdf_link_list[0])
        
        	# names must be in ascii. edge case with Flavien Leger contains 
        	# French accent aigu, hard-coded to change. Another fix to make.
            try:
                str(test_prof[0]).encode('ascii')
            except UnicodeEncodeError:
                test_prof[0] = ['Flavien Leger']

            # create professor directory if necessary
            prof_path = course_path + '/' + str(test_prof[0])
            if not os.path.exists(prof_path):
                try:
                    os.mkdir(prof_path)
                except UnicodeEncodeError:
                    os.mkdir(course_path + '/Flavien Leger')
                print ("Directory " + prof_path + " created")
            else:
                print ("Directory " + prof_path + " already exists")

            # final name of file
            filename = str(test_prof[0]) + '_' + test_type[0] + '_' + test_num[0] + '_' + test_date[0] + '.pdf'

            # final location of file to download
            final_path = prof_path + '/' + str(filename)

            # download file if one with the same name already exists. protects from 
            # duplicate files
            if not os.path.exists(final_path):
                r = session.get(pdf_url, headers=dict(referer=pdf_url))
                with open(final_path, 'wb') as f:
                    f.write(r.content)
                print("File with path " + final_path + " created")
            else:
                print("File with path " + final_path + " already exists")
