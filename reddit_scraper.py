#! usr/bin/env python3
import praw
import pandas as pd
from reddit_api_info import client_id, client_secret, user_agent, username, password
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from os import path, remove
from email_info import sender, receiver, subject, email_password, email_server, port

file_name = 'NintendoSwitch_subreddit_scraper.csv'
def scrape_reddit():
    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,
                         user_agent=user_agent,
                         username=username, password=password,
                         )
    switch_bundle_mentions = []
    for submission in reddit.subreddit("NintendoSwitch").hot(limit=25):
        if "switch" in submission.title.lower():
            switch_bundle_mentions.append(submission)
    for submission in reddit.subreddit("NintendoSwitchDeals").hot(limit=25):
        if "switch bundle" in submission.title.lower():
            switch_bundle_mentions.append(submission)
    return switch_bundle_mentions


def create_csv(switch_bundle_list):
    thread_dict = {
        "title": [],
        "score": [],
        "id": [],
        "url": [],
        "comms_num": [],
        "created": [],
        "body": []
    }
    for reddit_thread in switch_bundle_list:
        thread_dict["title"].append(reddit_thread.title)
        thread_dict["score"].append(reddit_thread.score)
        thread_dict["id"].append(reddit_thread.id)
        thread_dict["url"].append(reddit_thread.url)
        thread_dict["comms_num"].append(reddit_thread.num_comments)
        thread_dict["created"].append(reddit_thread.created)
        thread_dict["body"].append(reddit_thread.selftext)
    thread_data = pd.DataFrame(thread_dict)
    convert_created_to_datetime = thread_data["created"].apply(get_date)
    thread_data = thread_data.assign(created=convert_created_to_datetime)
    thread_data.to_csv(file_name, index=False)
    return thread_data


def get_date(created_var):
    return datetime.datetime.fromtimestamp(created_var)


def send_email():
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    with open(file_name, "rb") as attached_file:
        part = MIMEApplication(attached_file.read(), Name=path.basename(file_name))
    part['Content-Disposition'] = 'attachment; filename="%s"' % path.basename(file_name)
    msg.attach(part)
    msg.attach(MIMEText("", "html"))
    server = smtplib.SMTP(email_server, port)
    server.starttls()
    server.login(sender, email_password)
    text = msg.as_string()
    server.sendmail(sender, [receiver], text)
    server.quit()


list_of_switch_bundles = scrape_reddit()
create_csv(list_of_switch_bundles)
send_email()