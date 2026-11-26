# All rights reserved by LauChakSing
# It helps students to check the perfect answers in GoChinese

import os
import json
import pyperclip
import requests
from time import sleep
import keyboard as k

def clear():
    os.system("cls" if os.name=="nt" else "clear")
    
def tab():
    k.press_and_release("tab")


def main():
    while True:
        try:
            os.system("title GoChinese Helper ^| LauChakSing")
            clear()
            
            print("Welcome to Lingnan GoChinese Helper!")
            print("Last update: 26/11/2026")
            
            print("\nPlease input number to choose the course:")
            courses = ["LCC1010", "LCC2010"]
            for course in courses:
                print(f"\033[94;1m[{courses.index(course)+1}] \033[0m{course}")
            course = int(input("\n\033[90m>>> \033[0m"))
            # if course not in range(1,len(courses)+1):
            #     continue
            if course == 2:
                print("\033[41mLCC2010 is coming soon...\033[0m")
                input()
                continue
            if course != 1:
                continue
            
            while True:
                try:
                    clear()
                    os.system(f"title GoChinese Helper ^| {courses[course-1]}")
                    
                    answers = json.loads(requests.get(f"https://lauchaksing.github.io/GoChinese-Helper/answers/{courses[course-1]}.json").text)
                    print("Please input number to choose the chapter:")
                    
                    for i in list(answers.keys()):
                        print(f"\033[94;1m[{i}] \033[0mChapter {i}")
                    chapter = int(input("\n\033[90m>>> \033[0m"))
                    
                    if (str(chapter) not in list(answers.keys())):
                        continue
                    
                    while True:
                        try:
                            os.system(f"title GoChinese Helper ^| Chapter {str(chapter)}")
                            clear()
                            
                            print(f"Chapter {chapter}:")
                            for i in range(1,len(list(answers[str(chapter)]))+1):
                                print(f"\033[94;1m[{i}] \033[0m{list(answers[str(chapter)])[i-1]}")
                                
                            usrInput = int(input("\n\033[90m>>> \033[0m"))
                            if usrInput not in range(1,len(list(answers[str(chapter)]))+1):
                                continue
                            exercise = list(answers[str(chapter)])[usrInput-1]
                            clear()
                            type = answers[str(chapter)][exercise]["type"]
                            print(f"{exercise} ({type})")
                            os.system(f"title GoChinese Helper ^| {exercise}")
                            
                            if type == "input":
                                print("\nThe answers will be inputted in 5s.\nPlease click on the page and DO NOT select anything!\n")
                                sleep(5)
                                for i in range(len(answers[str(chapter)][exercise]["questions"])):
                                    tab()
                                    print(f"[{answers[str(chapter)][exercise]["questions"][i]}] {answers[str(chapter)][exercise]["answers"][i]}")
                                    k.write(str(answers[str(chapter)][exercise]["answers"][i]))
                                tab()
                                tab()
                                input("\nFinish.")
                                continue
                            
                            if type == "pmc":
                                print("\nThe answers will be inputted in 5s. Please click on the page and DO NOT select any option!\n")
                                sleep(5)
                                for i in range(len(answers[str(chapter)][exercise]["questions"])):
                                    tab()
                                    k.press_and_release("space")
                                    for j in range(answers[str(chapter)][exercise]["answers"][i]-1):
                                        k.press_and_release("down")
                                    k.press_and_release("space")
                                    print(f"[{answers[str(chapter)][exercise]["questions"][i]}]", end=" ")
                                    if answers[str(chapter)][exercise]["answers"][i]==1:
                                        print("A")
                                    elif answers[str(chapter)][exercise]["answers"][i]==2:
                                        print("B")
                                    elif answers[str(chapter)][exercise]["answers"][i]==3:
                                        print("C")
                                    elif answers[str(chapter)][exercise]["answers"][i]==4:
                                        print("D")
                                tab()
                                tab()
                                input("\nFinish.")
                                continue
                            
                            if type == "mc":
                                input("\n\033[93m[Enter] \033[0mPlease enter to run a javascript to get the questions in console")
                                print("The script will be run in 5s. Please click on the page and DO NOT select anything!\n")
                                sleep(5)
                                k.press_and_release("ctrl+shift+j")
                                sleep(3)
                                k.write("""const questions=[];document.querySelectorAll('table[width="666"]').forEach(e=>{let o=e.querySelector("td.goChineseUserInputFontFamily");if(!o)return;let t=o.innerText.trim().split("\\n").map(e=>e.trim()).filter(e=>e);if(t.length>=2){t[0].replace(".","").trim();let e=t[1];questions.push(e)}});const result=JSON.stringify(questions);copy(result);console.log("Done! Please continue in GoChinese Helper.");""")
                                k.press_and_release("enter")
                                sleep(5)
                                k.press_and_release("ctrl+shift+j")
                                input("\n\033[93m[Enter] \033[0mPlease enter to continue after running the script.")
                                questions = json.loads(pyperclip.paste())
                                
                                
                                print("The answers will be inputted in 5s. Please click on the page and DO NOT select any option!\n")
                                sleep(5)
                                for question in questions:
                                    tab()
                                    k.press_and_release("space")
                                    for i in range(answers[str(chapter)][exercise]["answers"][question]-1):
                                        k.press_and_release("down")
                                    k.press_and_release("space")
                                    
                                    print(f"[{question}]", end=" ")
                                    if answers[str(chapter)][exercise]["answers"][question]==1:
                                        print("A")
                                    elif answers[str(chapter)][exercise]["answers"][question]==2:
                                        print("B")
                                    elif answers[str(chapter)][exercise]["answers"][question]==3:
                                        print("C")
                                    elif answers[str(chapter)][exercise]["answers"][question]==4:
                                        print("D")
                                tab()
                                tab()
                                if "comment" in list(answers[str(chapter)][exercise]):
                                    print(f"\n\033[93m[Comment]{answers[str(chapter)][exercise]["comment"]}\033[0m")
                                input("\nFinish.")
                                continue
                            
                            if type == "mc+input":
                                print("\nThe answers will be inputted in 5s. Please click on the page!\n")
                                sleep(5)
                                for i in range(len(answers[str(chapter)][exercise]["questions"])):
                                    tab()
                                    k.press_and_release("space")
                                    for j in range(answers[str(chapter)][exercise]["answers"][i][0]-1):
                                        k.press_and_release("down")
                                    k.press_and_release("space")
                                    print(f"[{answers[str(chapter)][exercise]["questions"][i]}]", end=" ")
                                    print("[正確]" if answers[str(chapter)][exercise]["answers"][i][0]==1 else "[錯誤]", end=" ")
                                    tab()
                                    print(f"{answers[str(chapter)][exercise]["answers"][i][1]}")
                                    k.write(str(answers[str(chapter)][exercise]["answers"][i][1]))
                                tab()
                                tab()
                                input("\nFinish.")
                                continue
                                
                            if type == "answer":
                                for answer in answers[str(chapter)][exercise]["answers"]:
                                    print(f"[{answer}]")
                                    
                                print(f"\n\033[93m[Comment] {answers[str(chapter)][exercise]["comment"]}\033[0m")
                                input("\nFinish.")
                                continue
                            
                        except KeyboardInterrupt:
                            break
                        except ValueError:
                            continue
                        
                        
                except KeyboardInterrupt:
                    break
                    
                except ValueError:
                    continue
                
        except KeyboardInterrupt:
            print("\n\033[93mThanks you for using!\033[0m")
            exit()
            
        except ValueError:
            continue

if __name__=="__main__":
    main()