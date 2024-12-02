# Team:
* Yixuan Li (yl3803)
* Meng Gao (mg4774)

Please refer to 
- `tokenizer/README.md` for the regular expression of our language and 
- `parser/README.md` for the CFG grammar
- `generator/README.md` for the translation to low level language
- `executer/README.md` for code execution logic.

Programming HW2 - Youtube link: https://youtu.be/XvDBSk59CS8

Programming HW3 - Youtube link: https://youtu.be/f7sn0suRIRc

## Usage Guide

prerequisite 
    - Docker must already be installed on the system.

1. clone repository
```
git clone https://github.com/Yixli9811/COMS-4115-Numera.git 
cd COMS-4115-Numera
```

2. Build a Docker image
```
docker build -t coms-4115-numera .
```
3. Run the Docker container
    we provide 5 files to test our program and one error file to show error report  
    (test_file.txt,test_file2.txt,test_file3.txt,test_file4.txt,test_file5.txt) (test_file_error.txt)
Note: `test_file3.txt` requires an input from the user.
```
docker run -it -p 4000:80 coms-4115-numera python3 main.py test/test_file.txt
```
