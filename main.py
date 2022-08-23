import imaplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import smtplib
import datetime
from time import sleep
from widgets import sleep_time_until_checkpoint, easy_read, clear_console, easy_write, Style, config
import socket
from setup_wizard import SetupWizard


def imap_operation(search_str, criteria_field='from', logic_operator='or', previous_operation=''):
    """
    Layers IMAP logic operators.
    For example, you want to search for emails FROM 'grandma' OR FROM 'grandpa@example.com', do this:
    
    
    x = imap_operation('grandma', 'from', 'or')

    x = imap_operation('grandpa@example.com', 'from', 'or', x)
    
    :param search_str: A string of criteria to search for.
    :param criteria_field: Can be an IMAP search criteria field such as 'from', 'to', 'subject', etc.
    :param logic_operator: Can be 'or' or 'and'.
    :param previous_operation: Use to chain multiple criteria.
    :return: A string of IMAP search criteria.
    """
    
    if logic_operator.upper() not in ['OR', 'AND']:
        print('Invalid logic operator')
        raise ValueError
    
    if previous_operation != '':
        previous_operation += ' '
    
    return previous_operation + logic_operator.upper() + ' ' + criteria_field.upper() + ' ' + search_str


def decode_email_str(email_input: str):
    """
    Emails are an encoded mess, especially when they contain special characters. Unfortunately, simply .decode() doesn't
     work.
    This function attempts to decode them into a simple string that resembles the original.
    
    :param email_input:
    :return:
    """
    decoded_email = ''
    i = 0
    while i < len(email_input) - 1:
        
        hex_code = ''
        while i < len(email_input) - 2 and email_input[i] == '=' and \
                email_input[i + 1].isalnum() and email_input[i + 2].isalnum():
            hex_code += (email_input[i + 1] + email_input[i + 2])
            i += 3
        
        if hex_code != '':
            decoded_email += bytes.fromhex(hex_code).decode("utf-8", "ignore")
            if i < len(email_input) - 1 and email_input[i] == '=':
                i += 1
        
        if i < len(email_input) - 1:
            decoded_email += email_input[i]
            i += 1
    
    return decoded_email


class EmailBlocker:
    
    def __init__(self):
        
        # Load config file or prompt user to set up config
        try:
            self.config = config()
        except FileNotFoundError:
            print('It seems like you haven\'t run the setup wizard yet.\nLet\'s do that now!')
            input('Press enter to continue...')
            self.setupWizard = SetupWizard()
            self.setupWizard.setup()
            self.config = config()
        
        # make sure the blacklist contains items
        if len(self.config['blacklist']) == 0:
            print('There\'s nothing in the blacklist.\nYou need to use the "setup_wizard.py" to add some.')
            exit()
        
        # read the fancy email template
        try:
            self.email_reply_html = easy_read('templates/fancy_template.html')
        except FileNotFoundError:
            self.email_reply_html = None
            self.reply_fancy_email = False
        
        # read the plain text email template
        try:
            self.email_reply_plain_text = easy_read('templates/plain_template.txt')
        except FileNotFoundError:
            self.email_reply_plain_text = 'Email could not be delivered.'
            easy_write('templates/plain_template.txt', self.email_reply_plain_text)
    
    def send_email(self, receiver_email, message, subject='No Subject', html=None):
        """
        Sends an email to the specified receiver.
        
        :param receiver_email: The email address of the receiver.
        :param message: The message to send.
        :param subject: The subject of the email.
        :param html: The HTML version of the email.
        """
        
        # login to the email server
        port = int(self.config['smtp_port'])
        smtp_server = self.config['smtp_address']
        
        sender_email = self.config['username']
        password = self.config['password']
        
        msg = MIMEMultipart("alternative")
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email
        
        part1 = MIMEText(message)
        msg.attach(part1)
        if html:
            part2 = MIMEText(html, 'html')
            msg.attach(part2)
        
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls(context=context)
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
        except socket.gaierror:
            print('Sending email failed! You probably gave a wrong SMTP server.\n'
                  'Delete the "config files/" directory and run again to set up the correct credentials or edit the '
                  'config file manually.')
            exit()
    
    def bot_pass(self):
        # connect to the server and go to its inbox
        try:
            imap = imaplib.IMAP4_SSL(self.config['imap_address'])
            # noinspection PyBroadException
        except socket.gaierror:
            print('Looks like you gave a wrong IMAP server.\n'
                  'Delete the "config files/" directory and run again to set up the correct credentials or edit the'
                  ' config file manually.')
            imap = None
            exit()

        # noinspection PyBroadException
        try:
            imap.login(self.config['username'], self.config['password'])
            
        except imaplib.IMAP4.error:
            # error occurs when there is incorrect login information
            print('Login failed! Either the email, password, or IMAP server is wrong. \n'
                  'If you have 2FA enabled, you will have to generate an app-specific password from your account '
                  'settings.'
                  '\n'
                  ''
                  'Delete the "config files/" directory and run again to set up the correct credentials or edit the '
                  'config file manually.')
            exit()
        
        # format a logical string to search for the email
        imap_operation_str = ''
        for blocked_server in self.config['blacklist']:
            imap_operation_str = imap_operation(blocked_server, previous_operation=imap_operation_str)
        
        print('\n' + Style.blue + Style.inverted + ' -> ' + datetime.datetime.now().strftime('%H:%M') +
              ' Checking emails in "' + self.config['search_mail_folder'] + '" ' + Style.reset)
        
        # apply a search criteria to the mailbox (like OR, AND, etc.)
        while True:
            # noinspection PyBroadException
            try:
                imap.select(self.config['search_mail_folder'])
                _, data = imap.search(None, imap_operation_str)
                mail_ids = []
                break
            except imaplib.IMAP4.error:
                print('The mailbox "' + self.config['search_mail_folder'] + '" does not exist.')
                self.config['search_mail_folder'] = input('Please enter a valid mailbox: ')
                config(self.config)
        
        # parse the message ids
        for block in data:
            # b'1 2 3'.split() => [b'1', b'2', b'3']
            if block:
                mail_ids += block.split()
            else:
                print(' No new emails')
                break
        
        # make the latest email id the first one
        mail_ids.reverse()
        
        # now check though each email
        for email_id in mail_ids[:self.config['max_search_results']]:
            _, sender_raw = imap.fetch(email_id, "BODY.PEEK[HEADER.FIELDS (From)]")
            
            # noinspection PyUnresolvedReferences
            email_sender = sender_raw[0][1].decode('utf-8').replace('From: ', '').strip()
            
            print(email_id.decode('utf-8') + ': ' + email_sender)
            for blocked_email in self.config['blacklist']:
                if blocked_email in email_sender.lower():
                    print(Style.red + Style.inverted + ' -> Blocked email found. ' + Style.reset)
                    _, raw_content = imap.fetch(email_id, "BODY[1]")
                    _, raw_subject = imap.fetch(email_id, "BODY.PEEK[HEADER.FIELDS (SUBJECT)]")
                    _, raw_date = imap.fetch(email_id, "BODY.PEEK[HEADER.FIELDS (Date)]")
                    
                    # noinspection PyUnresolvedReferences
                    date_str = raw_date[0][1].decode('utf-8').replace('Date: ', '').strip().replace(' (UTC)', '')
                    
                    # convert date to datetime object
                    date_obj = datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                    
                    # decode the email
                    # noinspection PyUnresolvedReferences
                    email_content = raw_content[0][1].decode("UTF-8")
                    decode_email_content = decode_email_str(email_content)
                    # noinspection PyUnresolvedReferences
                    subject = decode_email_str(raw_subject[0][1].decode("UTF-8").replace('SUBJECT: ', ''))
                    
                    # save the email to a file so it follows the format 'subject-date.txt'
                    if self.config['save_archive']:
                        archived_email_content = date_obj.strftime('%Y-%m-%d %H:%M:%S') + '\nFrom: ' + email_sender + \
                                                 '\nSubject: ' + subject + '\n\n' + decode_email_content
                        try:
                            easy_write(
                                f'emails/email-{date_obj.strftime("%Y-%m-%d %H.%M.%S")}.txt',
                                archived_email_content
                            )
                        
                        except FileNotFoundError:
                            os.mkdir('emails')
                            easy_write(
                                f'emails/email-{date_obj.strftime("%Y-%m-%d %H.%M.%S")}.txt',
                                archived_email_content
                            )
                    
                    # format header
                    if self.config['also_reply_to_email']:
                        reply_email_header = 'On ' + date_obj.strftime(
                            '%b %d, %Y, at %I:%M %p') + ', ' + email_sender + ' wrote:'
                        
                        # format a reply email
                        indented_email_content = '> ' + reply_email_header + '\n> \n'
                        for i in decode_email_content.splitlines(keepends=False):
                            indented_email_content += '> ' + i + '\n'
                        
                        # join the header and the email content
                        email_reply_full_content = self.email_reply_plain_text + '\n\n\n' + indented_email_content
                        
                        # send the reply email
                        self.send_email(
                            receiver_email=email_sender,
                            message=email_reply_full_content,
                            subject='Re: ' + subject,
                            html=self.email_reply_html
                        )
                        print(' Email replied to: ' + email_sender)
                    
                    if self.config['block_emails']:
                        # mark email for deletion
                        imap.store(email_id, "+FLAGS", "\\Deleted")
                        print(' Original email deleted')
                        
                        # finish removing email
                        imap.expunge()
        
        # close the mailbox
        imap.close()
        # logout from the account
        imap.logout()
    
    def run_forever(self):
        # check emails every x minutes forever
        while True:
            self.config = config()
            
            try:
                bot.bot_pass()
            except TimeoutError:
                print(Style.red + 'Network disconnected.' + Style.reset)
            
            # get time interval from the config and print wait time
            sleep_time = sleep_time_until_checkpoint(self.config['update_interval'])
            print('\nSleeping for ' + str(sleep_time // 60) + ' minutes and ' + str(sleep_time % 60) + ' seconds')
            sleep(sleep_time)


if __name__ == '__main__':
    
    clear_console()
    bot = EmailBlocker()
    try:
        # runs scheduled function on this line forever
        bot.run_forever()
    except KeyboardInterrupt:
        # when control-c is pressed
        print('\n\nProgram has exited')
