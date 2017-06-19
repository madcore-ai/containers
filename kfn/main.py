from flanker import mime
import os
import f2n


def main():
    emails_path = os.getenv('PATH_DATA', "/opt/offlineimap")
    f2n_instance = f2n.F2n(['map01', 'url01'])

    for root, dirs, files in os.walk(emails_path):
        for file in files:
            filename = root.split("/")[-1] + "/" + file
            filefullname = os.path.join(root, file)

            message_string = open(filefullname, "rb").read()
            msg = mime.from_string(message_string)
            f2n_instance.process(msg)

if __name__ == '__main__':
    main()
