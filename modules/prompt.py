import json
import os
from collections import defaultdict
from gmail_api import get_gmail_service, fetch_emails, mark_important, fetch_important_emails
from utils import save_to_markdown, calculate_cost
from openai_api import summarize_text, categorize_text
from emails import Email

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def get_profile_name():
    profile_name = input('Please enter a profile name: ')
    print()
    return profile_name

def create_profile():
    profile_name = get_profile_name()
    profile_path = 'profiles/' + profile_name
    
    if not os.path.exists(profile_path):
        get_gmail_service(profile_name)
    else:
        print(f'{profile_name} already exists! Please enter a new profile name.')
    print()
    return profile_name

def select_profile():
    valid = False
    while not valid:
        print('Available profiles:')
        profiles = 'profiles'
        for profile in os.listdir(profiles):
            print(profile)
            
        profile_name = get_profile_name()
        path = os.getenv('PROFILES_PATH')
        profile_path = path + '/' + profile_name
        if not os.path.exists(profile_path):
            print(f'{profile_name} does not exist! Select an existing one.')
        else:
            valid = True            
    print()
    return profile_name


def categorize_important(profile_name):
    if len(profile_name) != 0:
            print('Fetching emails...')
            service = get_gmail_service(profile_name)
            emails = fetch_emails(service)
            important_emails = []
            total = ''
            for subject in emails:
                    for text in emails[subject]:
                        total += text.body
            cost = calculate_cost(total)
            response = input(f'Total will cost: ${cost}, proceed? ').lower()
            if response == 'y' or response == 'yes':
                try:
                    print('Categorizing...')        
                    for subject in emails:
                        for email in emails[subject]:
                            try:
                                if 'IMPORTANT' not in email.labels:
                                    category = categorize_text(email.body)
                                    if category == True:
                                        important_emails.append(email)
                            except Exception as e:
                                print(e)
                                continue
                except Exception as e:
                    print('Error parsing', e)
                mark_important(service, important_emails)
                print()
                if len(important_emails) > 0:
                    print(f'Categorizing complete! Email(s):')
                    for email in important_emails:
                        print(f'{Colors.CYAN}{email.subject}{Colors.RESET}')
                    print()
                    print(f'{len(important_emails)} emails have been marked as important.')
                else:
                    print('All relevant emails have already been marked as important.')
    else:
        print('Profile name not selected, please select a profile.')
    print()

def summarize_important_emails(profile_name):
    if len(profile_name) != 0:
        print('Fetching emails...')
        count = 0
        service = get_gmail_service(profile_name)
        emails = fetch_important_emails(service)
        summaries = defaultdict(list)
        total = ''
        for subject in emails:
                for text in emails[subject]:
                    total += text.body
        cost = calculate_cost(total)
        response = input(f'Total will cost: ${cost}, proceed? ').lower()
        if response == 'y' or response == 'yes':
            try:
                print('Summarizing...')
                for subject in emails:
                    for text in emails[subject]:
                        try:
                            summary = summarize_text(text.body)['choices'][0]['message']['content']
                            summaries[subject].append(summary)
                            count +=1
                        except Exception as e:
                            print(e)
                            continue
            except Exception as e:
                print('Error parsing', e)
            #save_to_markdown(summaries, 'output/'+profile_name+'_'+'emails.md')
            print()
            print(f'Total important emails today: {count}')
            for number, subject in enumerate(summaries, start=1):
                print(f'{Colors.BLUE}{number}. {subject}:{Colors.RESET}')
                for text in summaries[subject]:
                    print(text)
                print()
            print()
            #print(f'Summarizing complete! Please check: {profile_name}_emails.md')
    else:
        print('Profile name not selected, please select a profile.')
    print()

def summarize_emails(profile_name):
    if len(profile_name) != 0:
        print('Fetching emails...')
        count = 0
        service = get_gmail_service(profile_name)
        emails = fetch_emails(service)
        summaries = defaultdict(list)
        total = ''
        for subject in emails:
                for text in emails[subject]:
                    total += text.body
        cost = calculate_cost(total)
        response = input(f'Total will cost: ${cost}, proceed? ').lower()
        if response == 'y' or response == 'yes':
            try:
                print('Summarizing...')
                for subject in emails:
                    for text in emails[subject]:
                        try:
                            summary = summarize_text(text.body)
                            summaries[subject].append(summary)
                            count +=1
                        except Exception as e:
                            print(e)
                            continue
            except Exception as e:
                print('Error parsing', e)
            #save_to_markdown(summaries, 'output/'+profile_name+'_'+'emails.md')
            print()
            print(f'Total emails today: {count}')
            for number, subject in enumerate(summaries, start=1):
                print(f'{Colors.BLUE}{number}. {subject}:{Colors.RESET}')
                for text in summaries[subject]:
                    print(text)
                print()
            print()
            #print(f'Summarizing complete! Please check: {profile_name}_emails.md')
    else:
        print('Profile name not selected, please select a profile.')
    print()
    
def logic():
    running = True 
    profile_name = ''
    if os.path.exists('state.json'):
        with open('state.json', 'r') as file:
            # Load the data from the JSON file
            state = json.load(file)
            profile_name = state['currentProfile']
    else:
        state = {}
    prompt = """1. Create a profile
2. Select a profile
3. Summarize today's emails
4. Summarize today's important emails
5. Categorize today's emails
6. Exit
Please select an option: """
    while running:
        if len(profile_name) != 0:
            print(f'Current profile: {profile_name}')
        option = input(prompt)
        print()
        if option == '1':
            profile_name = create_profile()
        elif option == '2':
            profile_name = select_profile()
        elif option == '3':
            summarize_emails(profile_name)
        elif option == '4':
            summarize_important_emails(profile_name)
        elif option == '5':
            categorize_important(profile_name)
        elif option == '6':
            running = False
        state['currentProfile'] = profile_name
        with open('state.json', 'w') as file:
            json.dump(state, file, indent=4)          
