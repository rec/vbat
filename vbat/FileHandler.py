__author__ = 'testcaseone'


def loadconfig(word):
    data = ''
    fobj = open('vbat.config')
    for line in fobj:
        if line[0] != '#' and line != '':
            line = line.replace('\n', '')
            line = line.split(';')
            if line[0] == word:
                data = line[1]

    fobj.close()
    return data
