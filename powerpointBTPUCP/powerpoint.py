import argparse
from ppxtools.supportPP import generatePPTx
from ppxtools.supportPP import generateMultiPPTx

def main():
    parser = argparse.ArgumentParser(description="Generate reports for BTPUCP")
    parser.add_argument('--carrer', action='store', type=str, dest='carrer',
                        default="", required=False, help="Name of the carrer ")
    args = parser.parse_args()
    # If the carrer is not empty
    if not args.carrer:
        generateMultiPPTx()
    else:
        generatePPTx(args.carrer)

if __name__ == '__main__':
    main()
