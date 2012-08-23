import subprocess

class aspell:
    def __init__(self):
        self.pipe = subprocess.Popen(('aspell', '-a'), stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def check(self, word):
        output = []
        out = self.pipe.stdout.readline() #skip hello-line
        self.pipe.stdin.write(word.encode('utf-8') + b'\n')
        self.pipe.stdin.flush()
        out = self.pipe.stdout.readline().decode('utf-8')
        if out[0] in {'*', '+'}:
            return (True, None)
        elif out[0] == '#':
            return(False, None)
        else:
            return (False, out.split(': ')[1])