import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime, date, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

mail_sender = '<mailaddress>'
mail_receiver = '<mailaddress>'
mail_password = '<password mailservice>'

feedbin_user = "<username feedbin>"
feedbin_password = "<password feedbin>"

today = date.today()
yesterday = today - timedelta(days=1)

def get(url):
    response = requests.get(url, auth=HTTPBasicAuth(feedbin_user, feedbin_password))
    if response.status_code == 200:
        return response.json()
    else:
        return None
        
def mark_as_read(entries):
    url = 'https://api.feedbin.com/v2/unread_entries.json'
    response = requests.delete(url,auth=HTTPBasicAuth(feedbin_user,feedbin_password),json={'unread_entries': entries})
    if response.status_code == 200:
        return True
    else:
        print(response.status_code) 
        return False

sub = get("https://api.feedbin.com/v2/subscriptions.json")
data = get("https://api.feedbin.com/v2/entries.json")

out_txt = ''
out_html = ''
e = []

for d in data:
    date = datetime.fromisoformat(d['created_at'].replace('Z', '+00:00')).date()
    diff_days = (today-date).days
    if diff_days == 1:
        for s in sub:
            if s['feed_id'] == d['feed_id']:
                feed_title = s['title']
        out_txt += d['title'] + '\n' + d['url'] + '\n\r'
        out_html += '<a href="' + d['url'] +'" style="color:black">' + d['title'] + '</a><br>'+d['summary']+'<br><small style="color:gray"><i>'+feed_title.replace('.',chr(183))+'</i></small><br><br>'
        e.append(d['id'])

msg = MIMEMultipart("alternative")
msg["Subject"] = 'News ' + yesterday.strftime('%Y-%m-%d')
part1 = MIMEText(out_txt, "plain", "utf-8")
part2 = MIMEText('<html><head></head><body>'+ out_html +'</body></html>', "html")
msg.attach(part1)
msg.attach(part2)

if out_txt != '':
    print(len(e),'articles')
    print('mail sent')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as srv:
        srv.login(mail_sender, mail_password)
        srv.sendmail(mail_sender,mail_receiver, msg.as_string())
    if mark_as_read(e):
        print("articles marked as read")
else:
    print('no mail sent')
