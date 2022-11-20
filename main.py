import argparse

from Application import Application


def main():
    args = get_args()
    app = Application(args.port, args.rows, args.cols)
    run_application(app)

    # while(True):
    #     can create a command line interface


def get_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("port", type=str, help="serial port name")
    argparser.add_argument("rows", type=int, help="number of rows the sensor has")
    argparser.add_argument("cols", type=int, help="number of columns the sensor has")
    return argparser.parse_args()


def run_application(app: Application):
    app.get_baseline()
    app.plot()
    app.write_to_csv("filename")    # this needs to be prompted


if __name__ == "__main__":
    main()
