import sys
sys.path.append('modules')

from dotenv import load_dotenv
load_dotenv()


from modules.prompt import logic

def main():
    logic()

if __name__ == '__main__':
    main()