from domain import Domain_Handler
import argparse


def main():
    PERSPECTIVE_ACTIONS = ['DOMAIN', 'EMAILADDRESS']
    TRANSPORT_ACTIONS = ['QUEUE', 'FILE']

    parser = argparse.ArgumentParser(prog="")

    parser.add_argument('-p', '--perspective', required=True,
                        choices=PERSPECTIVE_ACTIONS)
    parser.add_argument('-s', '--sections', required=True, default='')
    parser.add_argument('-t', '--transport', required=True,
                        choices=TRANSPORT_ACTIONS)
    parser.add_argument('-qs', '--queue_server', required=False, help='')
    parser.add_argument('-qn', '--queue_name', required=False, help='')
    parser.add_argument('-o', '--file_store_path', required=False)
    args = parser.parse_args()

    if (args.transport == 'QUEUE' and not args.queue_server and not args.queue_name):
        parser.error('The --transport QUEUE requires --queue_name and --queue_server')
    elif(args.transport == 'FILE' and not args.file_store_path):
        parser.error('The --transport FILE requires --file_store_path')

    if (args.perspective == 'DOMAIN'):
        domain_handler = Domain_Handler()
        domain_handler.process()

if __name__ == '__main__':
    main()
