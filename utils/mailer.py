from django.core.mail import send_mail

FROM_EMAIL = 'hhs44test.com'

MAIL_FOOT = '''<br/><br/><br/>
Tmitter开发小组.<br/>
<a href="http://www.tmitter.com">tmitter.com</a>'''


def send(subject, body, recipient_list):
    body += MAIL_FOOT
    send_mail(subject, body, FROM_EMAIL, recipient_list, fail_silently=True)


def send_regist_success_mail(userinfo):
    subject = u'注册成功'
    body = u'''你好！<b>%s</b><br />
    你已经成功注册成为Tmitter用户<br />
    以下是您的信息：<br />
    <ul>
        <li>用户名：%s </li>
        <li>密码:%s</li>
    </ul>''' % (userinfo['realname'], userinfo['username'], userinfo['password'])
    recipient_list = [userinfo['email']]
    send(subject, body, recipient_list)
