import subprocess

class aspell:
    def __init__(self,Spell_program,Spell_options,Spell_coding):
        if Spell_program.strip() !='':
            if Spell_options == None:
                self.pipe = subprocess.Popen((Spell_program), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            else:
                self.pipe = subprocess.Popen((Spell_program,Spell_options), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.coding=Spell_coding
        
    def check(self, word):
        output = []
        self.pipe.stdin.write(word.encode(self.coding) + b'\n')
        self.pipe.stdin.flush()
        out = self.pipe.stdout.readline().decode(self.coding)
        if out.strip() != b''   :
            while self.pipe.stdout.readline().strip() != b'': pass
        if out[0] in {'*', '+'}:
            return (True, None)
        elif out[0] == '#':
            return(False, None)
        else:
            return (False, out.split(': ')[1])


