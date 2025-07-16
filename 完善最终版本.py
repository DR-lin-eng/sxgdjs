import requests
import smtplib
from email.mime.text import MIMEText
import time
import random
from bs4 import BeautifulSoup

# 获取ASP.NET_SessionId
def get_session_id():
    url = "https://jw.gdcvi.edu.cn/sx/DL/Index"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        cookies = response.cookies
        session_id = cookies.get('ASP.NET_SessionId')
        return session_id
    else:
        print(f"请求失败，状态码: {response.status_code}")
        return None

# 获取验证码内容包含在返回的cookie的r中
def get_verification_code(session_id):
    url = "https://jw.gdcvi.edu.cn/sx/N/N1"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}",
        "Host": "jw.gdcvi.edu.cn",
        "Referer": "https://jw.gdcvi.edu.cn/sx/DL/Index",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        set_cookie = response.headers.get("Set-Cookie")
        r = set_cookie.split('r=')[1].split(';')[0]
        return r
    else:
        print(f"请求失败，状态码: {response.status_code}")
        return None

# 获取.ASPXAUTH
def get_aspxauth(session_id, r):
    url = "https://jw.gdcvi.edu.cn/sx/M/Sh"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"ASP.NET_SessionId={session_id}; r={r}",
        "Dnt": "1",
        "Host": "jw.gdcvi.edu.cn",
        "Origin": "https://jw.gdcvi.edu.cn",
        "Referer": "https://jw.gdcvi.edu.cn/sx/DL/Index",
        "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    data = {
        "yhm": "123456",
        "mm": "123456",
        "Nzm": r,
        "btnLogin": "登录"
    }
    response = requests.post(url, headers=headers, data=data, allow_redirects=False)
    cookies = response.cookies.get_dict()
    aspxauth_cookie = cookies.get('.ASPXAUTH')
    return aspxauth_cookie

# 提取Xtcs和Xtdm
def get_xtcs_and_xtdm(session_id, r, aspxauth):
    url = 'https://jw.gdcvi.edu.cn/sx/ZhuJMB010306/ByJwb/'
    headers = {
        'authority': 'jw.gdcvi.edu.cn',
        'method': 'GET',
        'path': '/sx/ZhuJMB010306/ByJwb/',
        'cookie': f'ASP.NET_SessionId={session_id}; r={r}; .ASPXAUTH={aspxauth}',
        'referer': 'https://jw.gdcvi.edu.cn/sx/DL/Index/0/1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        xtcs = soup.find('input', {'id': 'Xtcs'})['value']
        xtdm = soup.find('input', {'id': 'Xtdm'})['value']
        return xtcs, xtdm
    else:
        print(f'请求失败，状态代码: {response.status_code}')
        return None, None

# 执行签到
def sign_in(aspxauth, xtcs, xtdm):
    url = "https://jw.gdcvi.edu.cn/sx/XsDkl/BcCz/"
    cookies = {
        '.ASPXAUTH': aspxauth
    }
    headers = {
        'Referer': 'https://jw.gdcvi.edu.cn/sx/ZhuJMB010306/ByJwb/',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'Xtcs': xtcs,
        'Xtu': '123456',
        'Xtdm': xtdm,
        'latitude': '230.160000',
        'longitude': '153.230000',
        'sf': '省份',
        'shi': '市',
        'xian': '区',
        'xxdz': '详细地址'
    }

    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    return response.text

# 发送邮件
def send_email(subject, content, smtp_server, smtp_port, smtp_user, smtp_pass, recipient):
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = recipient

    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, recipient, msg.as_string())
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print("邮件发送失败:", e)

# 配置邮件信息
smtp_server = "smtp.example.com"  # 替换为你的SMTP服务器
smtp_port = 465  # 一般为465
smtp_user = "your_email@example.com"  # 替换为你的邮箱
smtp_pass = "your_email_password"  # 替换为你的邮箱密码
recipient = "recipient_email@example.com"  # 替换为接收者的邮箱

# 执行完整流程
session_id = get_session_id()
if session_id:
    r = get_verification_code(session_id)
    if r:
        aspxauth = get_aspxauth(session_id, r)
        if aspxauth:
            xtcs, xtdm = get_xtcs_and_xtdm(session_id, r, aspxauth)
            if xtcs and xtdm:
                random_delay = random.randint(0, 180)  # 在0到180秒之间随机延迟
                print(f"将在 {random_delay} 秒后执行签到")
                time.sleep(random_delay)
                result = sign_in(aspxauth, xtcs, xtdm)
                send_email("Sign-in Result", result, smtp_server, smtp_port, smtp_user, smtp_pass, recipient)
                print(result)
            else:
                print("获取 Xtcs 和 Xtdm 失败")
        else:
            print("获取 .ASPXAUTH 失败")
    else:
        print("获取验证码失败")
else:
    print("获取 ASP.NET_SessionId 失败")
