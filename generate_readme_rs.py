import pypandoc

with open('README.rst', 'w') as fout:
    fout.write(pypandoc.convert('README.md', 'rst'))
