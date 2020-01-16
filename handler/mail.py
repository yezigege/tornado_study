import logging

import smtplib
import os
import pathlib
from email import encoders
from email.header import Header
from email.utils import formataddr
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

from control import ctrl
from handler.base import BaseHandler
from email.mime.multipart import MIMEMultipart  # 带多个部分的邮件
from app import scheduler  # 获取定时任务对象
from settings import JOB_IDS


# 扫描路径是否包含有指定文件
async def scan_file(path):
    """扫描指定路径 path 是否存在"""
    path_obj = pathlib.Path(path)
    is_exists = path_obj.exists()
    if is_exists:
        context = '已找到指定文件'
    else:
        context = '指定文件未找到'
    return is_exists, context


# 自定义发收信昵称
async def make_nickname(name, addr):
    return formataddr((Header(name, 'utf-8').encode(), addr))


# 邮件任务集合
# 发送纯文字邮件
async def make_text_email(msg, content, from_name, from_addr, to_name, to_addr, subject):
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    msg['From'] = await make_nickname(from_name, from_addr)  # 邮件发送者昵称
    msg['To'] = await make_nickname(to_name, to_addr)  # 邮件接收者昵称
    msg['Subject'] = Header(subject, 'utf-8').encode()  # 邮件标题
    return msg


# 发送HTML邮件
async def make_html_email(msg, content, from_name, from_addr, to_name, to_addr, subject):
    msg.attach(MIMEText(content, 'html', 'utf-8'))  # 发送html格式邮件
    msg['From'] = await make_nickname(from_name, from_addr)  # 邮件发送者昵称
    msg['To'] = await make_nickname(to_name, to_addr)  # 邮件接收者昵称
    msg['Subject'] = Header(subject, 'utf-8').encode()  # 邮件标题
    return msg


# 附件添加
async def _add_enclosure(msg, path):
    """添加附件"""
    num = ctrl.mredis.get_record_mail_times_ctl()
    while True:
        is_exists, context = await scan_file(path)
        if is_exists:
            with open(path, 'rb') as f:
                filename = os.path.basename(path)
                # 设置Content-Type,详见源码 和 https://www.cnblogs.com/zzr-stdio/p/10692497.html
                mime = MIMEBase('application', 'octet-stream')
                # 加上必要的头信息  https://www.jianshu.com/p/4c52cb691f54:
                mime.add_header('Content-Disposition', 'attachment', filename=filename)
                mime.add_header('Content-ID', '<' + str(num) + '>')
                mime.add_header('X-Attachment-Id', str(num))
                # 把附件的内容读进来:
                mime.set_payload(f.read())
                # 用Base64编码:
                encoders.encode_base64(mime)

                # 添加到MIMEMultipart:
                msg.attach(mime)
            return msg


async def send_mail(server, msg, from_addr, content, from_name, to_addr, to_name, subject, enclosure=None, type='1'):
    """整合邮件并发送邮件"""
    if type == '2':
        email_msg = await make_html_email(msg, content, from_name, from_addr, to_name, to_addr, subject)
    else:
        email_msg = await make_text_email(msg, content, from_name, from_addr, to_name, to_addr, subject)

    if enclosure:  # 如果有附件，就给加上
        email_msg = await _add_enclosure(email_msg, enclosure)

    try:
        server.sendmail(from_addr, [to_addr], email_msg.as_string())
    except Exception as e:
        raise e
    finally:
        server.quit()


async def _make_server(smtp_server, from_addr, password):
    """创建 msg 对象和 server 服务"""
    msg = MIMEMultipart()
    server = smtplib.SMTP(smtp_server, port=25)  # 默认端口是25
    server.set_debuglevel(1)  # 开启debug模式
    server.login(user=from_addr, password=password)
    return msg, server


async def make_scheduler_job(smtp_server, password, job_id, from_addr, to_addr, content, from_name,
                       to_name, subject, enclosure, email_type):
    """制作一个定时任务"""
    if job_id not in JOB_IDS:
        JOB_IDS.append(job_id)
    msg, server = await _make_server(smtp_server, from_addr, password)
    return scheduler.add_job(send_mail, 'date', run_date='2019-12-16 18:46:00', id=job_id,
                             args=(server, msg, from_addr, content, from_name,
                                   to_addr, to_name, subject, enclosure, email_type))


class SendMailHandler(BaseHandler):

    async def get(self):
        """制作一个页面模板"""
        total_mail_times = ctrl.mredis.get_record_mail_times_ctl()  # 邮件发送总次数
        total_mail_success_times = ctrl.mredis.get_record_mail_srccess_times_ctl()  # 发送成功总次数
        await self.render('sendmail.html',
                          total_mails_times=total_mail_times,
                          total_mail_success_times=total_mail_success_times)

    async def post(self):
        try:
            from_name = self.get_argument('from_name')
            from_addr = self.get_argument('from_addr')
            to_name = self.get_argument('to_name')
            to_addr = self.get_argument('to_addr')
            password = self.get_argument('password')  # 授权码
            smtp_server = self.get_argument('smtp_server')  # SMTP服务器地址
            content = self.get_argument('content')
            subject = self.get_argument('subject')  # 邮件主题
            email_type = self.get_argument('type', '1')  # 1:text 2:html
            enclosure = self.get_argument('enclosure', '')  # 附件
        except Exception as e:
            logging.error("邮件获取参数错误: {}".format(e))
            raise self.send_json(errcode=10001)

        # 记录发邮件总次数
        ctrl.mredis.record_mail_times_ctl()

        job_id = ctrl.mredis.get_record_mail_times_ctl().decode()


        try:
            # 发送邮件
            await make_scheduler_job(smtp_server, password, job_id, from_addr, to_addr, content, from_name,
                                     to_name, subject, enclosure, email_type)
            ctrl.mredis.record_mail_success_times_ctl()  # 记录邮件发送成功次数
            logging.info('email send success!')
            self.send_json()
        except smtplib.SMTPConnectError as e:
            logging.error('邮件发送失败，连接失败==>{}, {}'.format(e.smtp_code, e.smtp_error))
            self.send_json(errcode=13001)
        except smtplib.SMTPAuthenticationError as e:
            logging.error('邮件发送失败，认证错误==>{}, {}'.format(e.smtp_code, e.smtp_error))
            self.send_json(errcode=13002)
        except smtplib.SMTPSenderRefused as e:
            logging.error('邮件发送失败，发件人被拒绝==>{}, {}'.format(e.smtp_code, e.smtp_error))
            self.send_json(errcode=13003)
        except smtplib.SMTPRecipientsRefused as e:
            logging.error('邮件发送失败，收件人被拒绝=={}'.format(e))
            self.send_json(errcode=13004)
        except smtplib.SMTPDataError as e:
            logging.error('邮件发送失败，数据接收拒绝==>{}, {}'.format(e.smtp_code, e.smtp_error))
            self.send_json(errcode=13005)
        except smtplib.SMTPException as e:
            logging.error('邮件发送失败==>{}'.format(e))
            self.send_json(errcode=13006)
        except Exception as e:
            logging.error('邮件发送异常==>{}'.format(e))
            self.send_json(errcode=13007)

