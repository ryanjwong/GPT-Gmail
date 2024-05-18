import os
from collections import defaultdict
from gmail_api import get_gmail_service, fetch_emails
from utils import save_to_markdown, calculate_cost
from summarizer import summarize_text

def get_profile_name():
    profile_name = input('Please enter a profile name: ')
    print()
    return profile_name

def create_profile():
    profile_name = get_profile_name()
    path = os.getenv('PROFILES_PATH')
    profile_path = path + '/' + profile_name + '.json'
    
    if not os.path.exists(profile_path):
        get_gmail_service(profile_name)
    else:
        print(f'{profile_name} already exists! Please enter a new profile name.')
    print()
    return profile_name

def select_profile():
    print('Available profiles:')
    profiles = 'profiles'
    for profile in os.listdir(profiles):
        print(profile.replace('.json', ''))
    profile_name = get_profile_name()
    print()
    return profile_name

def summarize_emails(profile_name):
    if len(profile_name) != 0:
        print('Fetching emails...')
        service = get_gmail_service(profile_name)
        emails = fetch_emails(service)
        summaries = defaultdict(list)
        total = ''
        for subject in emails:
                for text in emails[subject]:
                    total += text
        cost = calculate_cost(total)
        response = input(f'Total will cost: ${cost}, proceed? ').lower()
        if response == 'y' or response == 'yes':
            try:
                print('Summarizing...')
                for subject in emails:
                    for text in emails[subject]:
                        try:
                            summary = summarize_text(text)['choices'][0]['message']['content']
                            summaries[subject].append(summary)
                        except Exception as e:
                            print(e)
                            continue
            except Exception as e:
                print('Error parsing', e)
            save_to_markdown(summaries, 'output/'+profile_name+'_'+'emails.md')
            print(f'Summarizing complete! Please check: {profile_name}_emails.md')
    else:
        print('Profile name not selected, please select a profile.')
    print()
    
def logic():
    running = True 
    profile_name = ''
    prompt = """1. Create a profile
2. Select a profile
3. Summarize emails
4. Exit
Please select an option: """
    while running:
        if len(profile_name) != 0:
            print(f'Current profile: {profile_name}')
        option = input(prompt)
        
        if option == '1':
            create_profile()
        elif option == '2':
            profile_name = select_profile()
        elif option == '3':
            summarize_emails(profile_name)
        elif option == '4':
            running = False         
