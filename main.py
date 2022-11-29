import argparse
import time

from Application import Application


def main():
    args = get_args()
    app = Application(args.port, args.rows, args.cols)
    app.file = "file.csv"
    app.start()
    time.sleep(2.4)

    app.write_to_csv()
    time.sleep(2.4)

    # app.plot()
    app.shutdown()

    # while True:
    #     user_input = input('sensor command>>>')
    #
    #     if user_input == 'start':
    #         print("starting application")
    #         app.start()
    #     elif user_input == 'quit':
    #         print('quitting')
    #         app.shutdown()
    #         break
    #     elif user_input == 'plot':
    #         print("plotting")
    #         app.plot()
    #     elif user_input == 'plot stop':
    #         print("stopping plot")
    #         app.stop_plot()
    #     elif user_input == 'write':
    #         print("writing to CSV")
    #         app.write_to_csv()
    #     elif user_input == 'stop write':
    #         print("stopping write to csv")
    #         app.stop_write_to_csv()
    #     elif user_input.startswith("filename"):
    #         words = user_input.split()
    #         app.file = words[-1]
    #     elif user_input.startswith("obs"):
    #         words = user_input.split()
    #         app.file = int(words[-1])
    #     else:
    #         print("invalid command")

def get_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("port", type=str, help="serial port name")
    argparser.add_argument("rows", type=int, help="number of rows the sensor has")
    argparser.add_argument("cols", type=int, help="number of columns the sensor has")
    return argparser.parse_args()


if __name__ == "__main__":
    main()
