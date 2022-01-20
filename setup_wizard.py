import getpass
import os
from widgets import Style, clear_console, wait_indicator, config


class SetupWizard:
    
    def __init__(self):
        clear_console()
        
        self.smtp_port = ''
        self.username = ''
        self.password = ''
        self.imap_address = ''
        self.smtp_address = ''
        self.blacklist = []
        
        self.default_config = {
            'search_mail_folder': 'inbox',
            'max_search_results': 20,
            'update_interval': 10,
            'also_reply_to_email': True,
            'save_archive': True,
            'block_emails': True,
        }
        
        self.config_explain = {
            'search_mail_folder': 'Where blacklist emails will arrive for this program to search.\n'
                                  'I recommend filtering blocked emails to a folder other than your inbox, such as the '
                                  '"Archive" folder.\n'
                                  'That way it will mark it as read and not give you notifications BEFORE it reaches '
                                  'your inbox.'
                                  'This setting can usually be found in your email account settings.',
            
            'max_search_results': 'How many of the most recent emails will be checked for blacklist emails.\n',
            
            'update_interval': 'The interval in minutes between each update of the search results.\n'
                               'Must be less than an hour.',
            
            'also_reply_to_email': 'If enabled, the email will be replied to with the template provided in the config '
                                   'files.\n'
                                   'Feel free to edit this template.',
            
            'save_archive': 'If enabled, the email will be saved in the emails archive after mailbox deletion as plain '
                            'text.',
            
            'block_emails': 'Any emails on the blacklist will be permanently and unrecoverable deleted from your mail '
                            'account.',
        }
        
        # check if in the correct directory
        current_folder = os.getcwd().split('/')[-1]
        if current_folder != 'emailBlockBot':
            print("It looks like your not running this from the correct directory!")
            print(
                'Make sure you "cd" into this file. It would look something like this but with the folder this program '
                'is'
                ' in:\n')
            print(Style.green + 'cd Users/<username>/blabla/setup_wizard.py' + Style.reset)
            
            print("\nThen run this command from this folder:\n")
            print(Style.green + 'python3 setup_wizard.py' + Style.reset)
            
            print('\n\n')
            exit()
        
        # check if the config directory exists
        if not os.path.isdir('config files'):
            os.mkdir('config files')
        
        # check if the config file exists
        if not os.path.isfile('config files/config.txt'):
            print('It looks like you\'re running this for the first time. Let\'s get started!')
        else:
            print('It looks like you\'re already setup. You can always run this program again to reset your settings,'
                  'or you can simply deletes the "config files" directory.')
            input('\n\nPress "enter" to continue.')
    
    def page_1(self):
        
        clear_console()
        
        # login
        print(Style.blue + Style.inverted + ' Step 1/3 - Login' + Style.reset)
        print('\nFirst you\'ll login to your account\n')
        self.username = input(Style.blue + Style.inverted + ' Email/username: ' + Style.reset)
        self.password = getpass.getpass(Style.blue + Style.inverted + ' Password: ' + Style.reset)
        
        print("\033[A                             \033[A")
        print(Style.blue + Style.inverted + ' Password: ' + Style.reset + ''.join(['*'] * len(self.password)))
        print('\n')
        
        self.imap_address = input(Style.blue + Style.inverted + ' Incoming Mail Server (IMAP): ' + Style.reset)
        self.smtp_address = input(Style.blue + Style.inverted + ' Outgoing Mail Server (SMTP): ' + Style.reset)
        
        self.smtp_port = input(Style.blue + Style.inverted + ' SMTP Port: ' + Style.reset)
        
        while not self.smtp_port.isdigit():
            print("\033[A                             \033[A")
            print('It has to be a number.')
            self.smtp_port = input(Style.red + Style.inverted + ' SMTP Port: ' + Style.reset)
        
        input('\n\nPress "enter" to go to the next step.')
    
    def page_2(self):
        # second page
        clear_console()
        print(Style.blue + Style.inverted + ' Step 2/3 - Block list' + Style.reset)
        print('Now you\'ll enter the addresses you want to block.')
        print('They can either be full addresses (johnny@gmail.com) or words in the address (@gmail, or johnny)')
        print('Just press enter when you\'re done.\n')
        
        self.blacklist = []
        blocked = 1
        while True:
            blacklist_addition = input(
                Style.blue + Style.inverted + ' Block #' + str(blocked) + ': ' + Style.reset)
            
            if blacklist_addition == '':
                print('\033[A                             \033[A')
                break
            else:
                blocked += 1
                self.blacklist.append(blacklist_addition)
    
    def page_3(self):
        last_input = ' '
        while last_input != '':
            clear_console()
            print(Style.blue + Style.inverted + ' Step 3/3 - Settings' + Style.reset)
            print(
                '\nHere are the default settings. Type the number you\'d like to view or press enter to apply settings.'
            )
            
            config_keys = list(self.default_config.keys())
            
            for i in range(len(self.default_config)):
                print('\n#' + str(i + 1) + ': ' + config_keys[i] + ': ' + str(list(self.default_config.values())[i]))
            
            print('\n')
            last_input = input(Style.blue + Style.inverted + ' Set item #:' + Style.reset + ' ')
            
            # check if last input was a number
            if last_input.isdigit():
                last_input = int(last_input)
                if 0 < last_input <= len(self.default_config):
                    clear_console()
                    print(Style.blue + Style.inverted + ' Setting "' + config_keys[
                        last_input - 1] + '" ' + Style.reset + '\n\n')
                    print(Style.yellow + 'Help:' + Style.reset)
                    print(self.config_explain[config_keys[last_input - 1]])
                    
                    print('\n(press enter to go back or enter a new value)')
                    new_value = input('-> ')
                    
                    if new_value != '':
                        # format the value
                        if new_value.isdigit():
                            new_value = int(new_value)
                        elif new_value.lower() == 'true':
                            new_value = True
                        elif new_value.lower() == 'false':
                            new_value = False
                        
                        self.default_config[config_keys[last_input - 1]] = new_value
                
                else:
                    print('\033[A                             \033[A')
                    print('It has to be a number between 1 and ' + str(len(self.default_config)) + '.')
                    last_input = ' '
        
        print('\n\nGreat! Saving everything now...')
        print('Note: you can always change these settings from "config files/config.yml", '
              'or simply delete "config files" to reset them.')
        wait_indicator(3)
        
        # save config
        self.default_config['username'] = self.username
        self.default_config['password'] = self.password
        self.default_config['imap_address'] = self.imap_address
        self.default_config['smtp_address'] = self.smtp_address
        self.default_config['smtp_port'] = self.smtp_port
        self.default_config['blacklist'] = self.blacklist
        
        config(self.default_config)
    
    def setup(self):
        clear_console()
        self.page_1()
        self.page_2()
        self.page_3()
        print('Great you are all setup now!')


if __name__ == '__main__':
    
    try:
        wizard = SetupWizard()
        wizard.setup()
    
    except KeyboardInterrupt:
        print('\nIt looks like you exited early. Everything cancelled.')
    
    print('You can now start the server by entering:')
    print(Style.green + 'python3 main.py' + Style.reset)
    print('\n\n')
