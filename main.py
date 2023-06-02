from aiohttp import ClientSession,TCPConnector
from asyncio import run,gather
from prettytable import PrettyTable
from sys import argv
from re import findall
async def get_course_status(session:ClientSession,course:str):
    data = {"Semester": '1121',"CourseNo": course,"Language": "zh"}
    api = 'https://querycourse.ntust.edu.tw/querycourse/api/courses'
    async with session.post(api,data=data) as resp:
        return (await resp.json())[0]

async def main(course_list:list[str]):
    async with ClientSession(connector=TCPConnector(ssl=False)) as session:
        tasks = map(lambda x:get_course_status(session,x),course_list)
        courses = await gather(*tasks)
    for x in courses:
        x['choice_rate'] = round(x['AllStudent']/int(x['Restrict2']),2)
    courses.sort(key=lambda x:x['choice_rate'],reverse=True)
    tag = [
        'CourseNo',
        'AllStudent',
        'Restrict2',
        'choice_rate',
        'CourseTeacher',
        'CourseName']
    table = PrettyTable()
    table.field_names = [
        '索引',
        '課程代碼',
        '選課人數',
        '人數上限',
        '選取率',
        '授課老師',
        '課程名稱'
    ]
    for row, x in enumerate(courses):
        table.add_row([row+1, *(x[y] for y in tag)])
    print(table)

if __name__ == '__main__':
    try:
        argc = len(argv)
        if (not argv[0].startswith('python') and argc > 1) or (argc > 2):
            with open(argv[-1],'r',encoding='utf-8') as f:
                s = f.read()
        else:
            print('將志願清單複製到網址貼上後，再複製貼上到這個程式，即可自動分析課表:')
            s = input()
        pattern = '[A-Z]{2}[G|1-9]{1}[A|0-9]{3}[0|1|3|5|7]{1}[0-9]{2}'
        CourseNo_list = list(set(findall(pattern,s)))
        CourseNo_list.sort()
        print(CourseNo_list)
        run(main(CourseNo_list))
    except FileNotFoundError:
        print('請檢查檔案路徑是否正確')
    except Exception as e:
        print('發生錯誤',e.args,'請回報給開發者',sep='\n')
    input("按下enter結束執行")

# python -m nuitka --assume-yes-for-downloads --onefile --standalone --output-dir=build  --static-libpython=no ttes