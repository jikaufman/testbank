import os
import requests
from lxml import html

if __name__ == "__main__":

    username = raw_input("Enter your username\n")
    password = raw_input("Enter your password\n")
    

    login_url = 'https://upe.seas.ucla.edu/auth/login'
    testbank_url = 'https://upe.seas.ucla.edu/testbank'

    session = requests.session()

    page = session.get(login_url)
    tree = html.fromstring(page.content)
    token = tree.xpath('//*[@id="login"]/form/fieldset/div[1]/input/@value')[0]
    
    payload = {
        'username' : username,
        'password' : password,
        'csrfmiddlewaretoken' : token,
        'Submit' : 'Login'
    }

    result = session.post(login_url, data = payload, headers = dict(referer=login_url))
    workpls = session.get(testbank_url, headers=dict(referer=testbank_url))
    tree = html.fromstring(workpls.content)


    classes_path = '/html/body/div[2]/div/div/table/tbody/tr'
    classes_list = tree.xpath(classes_path + '/th/text()')

    course_name = ''

    for i in range(2025):
        test_details_path = classes_path + '[' + str(i) + ']/td'
        test_details_list = tree.xpath(test_details_path + '/text()')
        pdf_link_path = test_details_path + '[5]'
        pdf_link_list = tree.xpath(pdf_link_path + '/a/@href')

        test_type = tree.xpath(test_details_path + '[1]/text()')
        test_num = tree.xpath(test_details_path + '[2]/text()')
        test_date = tree.xpath(test_details_path + '[3]/text()')
        test_prof = tree.xpath(test_details_path + '[4]/text()')
        class_name = tree.xpath(classes_path + '[' + str(i) + ']/th/text()')

        filename = 'booty' + str(i) + '.pdf'

        if (test_prof == ['N/A']):
            test_prof[0] = "NA"
        if (test_prof == ['Jansma/Burns']):
            test_prof[0] = 'Jansma-Burns'

        if (class_name):
            course_name = class_name
            if not os.path.exists(str(course_name[0])):
                try:
                    os.mkdir(str(course_name[0]))
                except UnicodeEncodeError:
                    os.mkdir(str(['Flavien Leger']))
                print ("Directory " + str(course_name[0]) + " created")
            else:
                print("Directory " + str(course_name[0]) + " already exists")
        if (pdf_link_list):
            
            pdf_url = 'https://upe.seas.ucla.edu' + str(pdf_link_list[0])
        
            try:
                str(test_prof[0]).encode('ascii')
            except UnicodeEncodeError:
                test_prof[0] = ['Flavien Leger']
            if not os.path.exists(str(course_name[0]) +'/' + str(test_prof[0])):
                try:
                    os.mkdir(str(course_name[0]) + '/' + str(test_prof[0]))
                except UnicodeEncodeError:
                    os.mkdir(str(['Flavien Leger']))
                print ("Directory " + str(course_name[0]) + '/' + str(test_prof[0]) + " created")
            else:
                print ("Directory " + str(course_name[0]) + '/' + str(test_prof[0]) + " already exists")

            filename = str(test_prof[0]) + '_' + test_type[0] + '_' + test_num[0] + '_' + test_date[0] + '.pdf'

            final_path = str(course_name[0]) + '/' + str(test_prof[0]) + '/' + filename
            if not os.path.exists(str(course_name[0]) + '/' + str(test_prof[0]) + '/' + str(filename)):
                r = session.get(pdf_url, headers=dict(referer=pdf_url))
                with open(final_path, 'wb') as f:
                    f.write(r.content)
                print("File with path " + final_path + " created")
            else:
                print("File with path " + final_path + " already exists")
