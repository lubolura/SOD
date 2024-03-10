#!/usr/bin/env python3

import smtplib
import sod_utils
import io
import cv2
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


def send_email_smtp(st, email_subj, email_body, picture):
    recipients = st.email_addresses

    msg = MIMEMultipart()
    msg['Subject'] = email_subj
    msg['From'] = st.smtp_usr
    msg['To'] = recipients

    txt_data = email_body
    text = MIMEText(txt_data, _charset="utf-8")
    msg.attach(text)

    if picture is not None:
        try:
            is_success, buffer = cv2.imencode(".jpg", picture)
            if is_success:
                io_buf = io.BytesIO(buffer)
                mime_image = MIMEImage(io_buf.getvalue())
                msg.attach(mime_image)
        except Exception:
            sod_utils.debug("Cannot attach image.", "stderr")
            return False
    try:
        with smtplib.SMTP_SSL(host=st.smtp_server, timeout=10) as server:
            if st.smtp_debug_log:
                server.set_debuglevel(1)
            server.login(st.smtp_usr, st.smtp_pwd)
            server.sendmail(msg['From'], recipients.split(','), msg.as_string())
            sod_utils.debug("Email was sent to {}.".format(recipients.split(',')), "stdout")
    except TimeoutError:
        sod_utils.debug("Cannot send email - TIMEOUT !", "stderr")
        return False
    except Exception as e:
        sod_utils.debug("Cannot send email: {}.".format(e), "stderr")
        return False
    return True


def send_emails(st, email_subj,email_body, picture):
    if len(st.email_addresses) > 0:
        # Send emails
        if st.email_client == "smtp":
            if not send_email_smtp(st, email_subj, email_body, picture):
                return False

        # for addr in st.email_addresses:
            # start_time = time.time()
            # if st.email_client == "mutt":
            #    if not sendEmail_mutt(addr, picture):
            #        return False

    return True
