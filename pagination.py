from selenium import webdriver
import unittest
import time
import praw
import json
import sqlite3
from webdriver_manager.chrome import ChromeDriverManager



class demo(unittest.TestCase):
    def setUp(self):
        self.create_table()
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.reddit = praw.Reddit(
            client_id='CLIENT_ID',
            client_secret='CLIENT_SECRET',
            username='USERNAME',
            password='PASSWORD',
            user_agent='USER_AGENT'
        )
        self.driver.get('https://old.reddit.com/')
        self.counter = 3

    def test_first(self):
        posts = self.driver.find_elements_by_class_name('thing')
        if self.counter < 3:
            self.driver.find_element_by_class_name('next-button').click()
            time.sleep(3)
            self.counter += 1
            self.test_first()
        else:
            for post in posts:
                links = post.find_element_by_css_selector('a').get_attribute('href')
                if links.find('https://old.reddit.com/') != -1:
                    print(links)
                    submission = self.reddit.submission(
                        url='{}'.format(links))
                    submission.comments.replace_more()
                    for comments in submission.comments.list():
                        try:
                            if not self.check_if_comment_exists(comments.id):
                                if self.acceptable(comments.body):
                                    if comments.score > 2:
                                        if comments.parent().author != submission.author:
                                                score = self.check_if_score_exists(comments.parent_id)
                                                post_title = submission.title
                                                parent_id = parent_id=comments.parent_id
                                                comment_id = comments.id
                                                comment = self.format_data(comments.body)
                                                subreddit = str(comments.subreddit)
                                                created_utc = comments.created_utc
                                                if score is not None:
                                                    if score < comments.score:
                                                        score = comments.score
                                                        self.update_row(parent_id=parent_id,
                                                                        comment_id=comment_id,
                                                                        comment=comment,
                                                                        subreddit=subreddit,
                                                                        time=comments.created_utc,
                                                                        score=score)
                                                else:
                                                    score = comments.score
                                                    parent = self.reddit.comment(id='{}'.format(comments.parent())).body
                                                    self.insert_new_row(post_title=post_title,
                                                                        parent_id=comments.parent_id,
                                                                        comment_id=comment_id,
                                                                        parent=parent,
                                                                        comment=comments.body,
                                                                        subreddit=subreddit,
                                                                        time=created_utc,
                                                                        score=score
                                                                        )

                        except praw.exceptions.PRAWException:
                            print('Exception')
                            continue
                else:
                    continue
            self.driver.find_element_by_class_name('next-button').click()
            time.sleep(10)
            self.test_first()


    def tearDown(self):
        time.sleep(5)
        self.driver.close()

    def create_table(self):
        conn = sqlite3.connect('redditdata.db')
        cursor = conn.cursor()
        cursor.execute("""Create Table if not exists reddit(
            post_title,
            parent_id TEXT PRIMARY KEY,
            comment_id TEXT UNIQUE,
            parent TEXT,
            comment TEXT,
            subreddit TEXT,
            unix INT,
            score INT
        )""")
        conn.commit()
        conn.close()

    def check_if_score_exists(self,parent_id):
        try:
            sql = "Select score from reddit where parent_id = '{}'".format(parent_id)
            with sqlite3.connect('redditData.db') as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                return cursor.fetchone()[0]
        except:
            return None

    def check_if_comment_exists(self,commentid):
        try:
            sql = "Select * from reddit where comment_id ='{}'".format(commentid)
            with sqlite3.connect('redditData.db') as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                if cursor.fetchone() is not None:
                    print('already exists')
                    return True
                else: return False
        except:
            return False
    def update_row(self,parent_id,comment_id,comment,subreddit , time,score):
        try:
            sql = """UPDATE reddit SET comment_id = ?, comment = ? ,
                        subreddit = ?,unix = ?,score = ? WHERE parent_id = ?"""
            with sqlite3.connect('redditData.db') as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (
                    comment_id, comment, subreddit, int(time), score, parent_id
                ))
                conn.commit()
                print('updated')
        except:
            pass

    def insert_new_row(self,post_title,parent_id,comment_id,parent,comment,subreddit,time,score):
        try:
            sql = """Insert into reddit (post_title,parent_id,comment_id,parent,comment,
                        subreddit,unix,score) values (?,?,?,?,?,?,?,?)"""
            with sqlite3.connect('redditData.db') as conn:
                cursor = conn.cursor()
                cursor.execute(sql,(
                    post_title, parent_id, comment_id, parent, comment, subreddit, time, score
                ))
                conn.commit()
                print('inserted')
        except:
            pass

    def acceptable(self,data):
        if len(data) < 4:
            return False
        elif len(data) > 1000:
            return False
        elif data == '[deleted]' or data == '[removed]':
            return False
        else:
            return True

    def format_data(self,data):
        data = data.replace('\n', ' newlinechar ').replace('\r', ' newlinechar ').replace('"', "'")
        return data


if __name__ == '__main__':
    unittest.main()
