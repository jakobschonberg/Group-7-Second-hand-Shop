menu = {
    1:("Quit", "my_quit"),
    2:("Example", "example_function")
}

def my_quit():
    pass

def example_function():
    print("Hello world")    

def main():
    choice = None
    while (choice != 1):
        for key, value in sorted(menu.items()):
            print(f'{key} {value[0]}')
        try:
            choice = int(input())
            if not choice in menu.keys():
                print("invalid menu number")
                choice = None
        except Exception as e:
            print(e)
            choice = None
        if choice:
            chosen = menu[choice][1]
            globals()[chosen]()

main()