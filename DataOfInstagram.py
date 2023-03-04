import json
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import re

from selenium.common.exceptions import NoSuchElementException


class DataOfInstagram:

    def __init__(self):
        self.driver_loc = 'chromedriver.exe'
        self.driver = webdriver.Chrome(self.driver_loc)

    def close_chromedriver(self):
        self.driver.close()

    def instagram_login(self):
        self.driver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        sleep(3)

        check_field = self.driver.find_element_by_class_name('aOOlW.bIiDR')
        sleep(0.5)
        check_field.click()
        sleep(1)

        username = self.driver.find_element_by_name("username")
        username.click()  # click on username button
        username.send_keys("kristinahashtags")

        password = self.driver.find_element_by_name("password")
        password.click()
        password.send_keys("bakalarka202144")
        sleep(0.5)

        button_login = self.driver.find_element_by_class_name("Igw0E.IwRSH.eGOV_._4EzTm")
        button_login.click()
        sleep(3)

        not_now_notification = self.driver.find_element_by_class_name('sqdOP.yWX7d.y3zKF')
        not_now_notification.click()
        sleep(2)

        not_window = self.driver.find_element_by_class_name("aOOlW.HoLwm")
        not_window.click()
        sleep(2)

    def set_profile_name(self):
        profile = input('Enter profile name for analysis: ')

        self.profile = profile
        self.profile_url = 'https://www.instagram.com/' + self.profile

    def scroll_element(self, number_of_users):
        user_field = self.driver.find_element_by_css_selector("div.isgrP")
        user_list_length = len(user_field.find_elements_by_css_selector('li'))

        last_part = None
        last_part_count = 0
        while user_list_length < number_of_users:
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", user_field)
            user_list_length = len(user_field.find_elements_by_css_selector('li.wo9IH'))

            if last_part == user_list_length:
                last_part_count += 1
            else:
                last_part_count = 0

            if last_part_count > 15:
                break

            last_part = user_list_length
            sleep(0.2)

        followers = []
        sleep(1.0)

        try:
            for user in user_field.find_elements_by_css_selector('li.wo9IH'):
                user_name = user.find_element_by_css_selector('a.FPmhX.notranslate._0imsa').get_attribute("title")
                followers.append(user_name)

                if len(followers) == number_of_users:
                    break
        except NoSuchElementException:
            pass

        return followers

    # TODO: FOLLOWERS PART
    def find_followers(self, profile):
        url = 'https://www.instagram.com/' + profile
        self.driver.get(url)
        sleep(3)
        followers = set()

        try:
            number_of_followers_string = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div'
                                                                           '/header/section/ul/li['
                                                                           '2]/a/span').get_attribute("title")
        except NoSuchElementException:
            return followers

        followers_div = self.driver.find_element_by_css_selector("a.-nal3")
        followers_div.click()
        sleep(2)

        number_of_followers = int(number_of_followers_string.replace('\u00A0', ""))
        followers = set(self.scroll_element(number_of_followers))

        return followers

    def create_followers_data(self):
        self.profile_followers = self.find_followers(self.profile)
        self.profile_followers_data = dict()
        self.profile_followers_data[self.profile] = self.profile_followers

        for profile in self.profile_followers:
            profile_followers = self.find_followers(profile)
            mutual_followers = self.profile_followers.intersection(profile_followers)
            if len(mutual_followers) > 0:
                self.profile_followers_data[profile] = mutual_followers

    # TODO: FOLLOWINGS PART
    def find_followings(self, profile):
        url = 'https://www.instagram.com/' + profile
        self.driver.get(url)
        sleep(3)

        followings = set()
        try:
            number_of_followings_string = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div'
                                                                            '/header/section/ul '
                                                                            '/li[3]/a/span').text
        except NoSuchElementException:
            return followings

        followings = self.driver.find_elements_by_css_selector('a.-nal3')
        followings[1].click()
        sleep(2)

        number_of_followers = int(number_of_followings_string.replace(" ", ""))
        followings = set(self.scroll_element(number_of_followers))

        return followings

    def create_followings_data(self):
        self.profile_followings = self.find_followings(self.profile)
        self.profile_followings_data = dict()
        self.profile_followings_data[self.profile] = self.profile_followings

        for profile in self.profile_followings:
            profile_followings = self.find_followings(profile)
            mutual_followings = self.profile_followings.intersection(profile_followings)
            if len(mutual_followings) > 0:
                self.profile_followings_data[profile] = mutual_followings

    # TODO: ACTIVE FOLLOWERS
    def find_active_users(self, profile):
        followers = self.find_followers(profile)
        followings = self.find_followings(profile)
        users = followers.intersection(followings)
        if users == 0:
            return set()
        posts_users = self.find_posts_users(profile)
        result = posts_users.intersection(users)
        return result

    def create_active_users_data(self):
        self.profile_active_users = self.find_active_users(self.profile)
        with open("active_users.json", "w") as user_data:
            json.dump({ self.profile : list(self.profile_active_users)},user_data)

        for profile in self.profile_active_users:
            profile_active_users = self.find_active_users(profile)
            mutual_active_users = self.profile_active_users.intersection(profile_active_users)
            if len(mutual_active_users) > 0:
                with open("active_users.json", "r+") as user_data:
                    data = json.load(user_data)
                    data.update({ profile : list(mutual_active_users)})
                    user_data.seek(0)
                    json.dump(data,user_data)


    def find_links(self,profile):
        url = 'https://www.instagram.com/' + profile
        self.driver.get(url)

        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        links_n = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul'
                                                    '/li[1]/span/span').text
        number_of_links = int(links_n.replace(" ", ""))

        links = []
        while True:
            page_source = BeautifulSoup(self.driver.page_source, 'html.parser')
            body = page_source.find('body')
            all_links = body.findAll('a')

            for link in all_links:
                if re.match("/p", link.get('href')):
                    links.append('https://www.instagram.com' + link.get('href'))
                else:
                    continue

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(3)
            actual_height = self.driver.execute_script("return document.body.scrollHeight")

            if actual_height == scroll_height:
                break
            if len(set(links)) >= number_of_links:
                break

            scroll_height = actual_height

        return list(set(links))

    def find_likes_users(self):
        try:
            likes_element = self.driver.find_element_by_css_selector('a.zV_Nj')
            sleep(0.5)
            likes_element.click()
            sleep(0.9)

            likes_scroll = self.driver.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/div")

            number_of_likes_string = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div['
                                                                       '1]/article/div[3]/section[2]/div/div/a/span').text
            number_of_likes = int(number_of_likes_string.replace(" ", ''))

            likes_users = set()
            last_part = None
            last_part_count = 0

            while len(likes_users) < number_of_likes:
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop - 70", likes_scroll)
                sleep(0.5)

                data = BeautifulSoup(self.driver.page_source, 'html.parser')
                likes_users_field = data.findAll('a', {'class': 'FPmhX notranslate MBL3Z'})

                if last_part == likes_users_field:
                    last_part_count += 1
                if last_part_count > 5:
                    break

                last_part = likes_users_field

                for user in likes_users_field:
                    if user.get_text() != self.profile:
                        likes_users.add(user.get_text())

                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 910", likes_scroll)
                sleep(0.6)

                return likes_users
        except:
            return set()

    def find_posts_users(self,profile):
        links = self.find_links(profile)
        posts_users = set()

        for i in range(len(links)):
            self.driver.get(links[i])
            data = BeautifulSoup(self.driver.page_source, 'html.parser')

            comments_users_field = data.findAll('a', {'class': 'sqdOP yWX7d _8A5w5 ZIAjV'})
            for user in comments_users_field:
                if user.get_text() != self.profile:
                    posts_users.add(user.get_text())

            likes_users = self.find_likes_users()
            posts_users = posts_users.union(likes_users)

        return posts_users


if __name__ == '__main__':
    instagram = DataOfInstagram()
    instagram.instagram_login()
    instagram.set_profile_name()
    instagram.create_active_users_data()
