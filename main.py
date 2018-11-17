# coding: utf-8
"""
    main module
    Author: Ina Bankova
    Software for an interactive installation 
"""

from instance import Instance

def main():
    # initialize instance for the installation
    inst = Instance()
    while inst.is_running:
        #inst.create_user()
        inst.run_session()

if __name__ == "__main__":
    main()

