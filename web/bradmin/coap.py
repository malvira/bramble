import subprocess

def get(url):
    print subprocess.check_output(['coap-client', url])

if __name__ == "__main__":
    import sys
    get(sys.argv[1])
