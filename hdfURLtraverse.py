from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException,TimeoutException
import psycopg2
import time

conn = psycopg2._connect("dbname=postgres user=postgres password=")
cur = conn.cursor()

urlTraverse = {
        'link':''
    }

#防止主页每次启动重复插入
cur.execute(
        "select * from hdfurltraverse where link = 'http://www.haodf.com'"
        )
if len(cur.fetchall()) == 0:
    cur.execute(
            "insert into hdfurltraverse VALUES ('http://www.haodf.com','False')"
            )
    conn.commit()

t = 0
while(t<5):
    cur.execute(
            "select * from hdfurltraverse where visit = 'False'"
            )
    if len(cur.fetchall()) > 0 :
        flag=True
    else :
        flag=False
        break
    while(flag):
        cur.execute(
            "select * from hdfurltraverse"
        )
        for tuple in cur.fetchall():
            if tuple[1] is False:
                try:
                    driver = webdriver.Chrome()
                    driver.set_page_load_timeout(300)
                    driver.get(tuple[0])
                    for link in driver.find_elements_by_tag_name("a"):
                        urlTraverse['link'] = link.get_attribute("href")
                        if urlTraverse['link'] == None:
                            print(link.get_attribute("href"))
                        elif "haodf" in urlTraverse['link']:
                            cur.execute(
                                "select * from hdfurltraverse where link = (%s)", [urlTraverse['link']]
                            )
                            if len(cur.fetchall()) == 0:
                                cur.execute(
                                    "insert into hdfurltraverse VALUES (%s,%s)", [urlTraverse['link'], 'False']
                                )
                    cur.execute(
                        "update hdfurltraverse set visit = 'True' where link = (%s)", [tuple[0]]
                    )
                    print('访问完一条URL')
                except TimeoutException:
                    t=t+1
                    time.sleep(60)
                    break
                except NoSuchElementException:
                    cur.execute(
                        "update hdfurltraverse set visit = 'True' where link = (%s)", [tuple[0]]
                    )
                    print('访问完一条URL')
                finally:
                    conn.commit()
                    driver.close()
                t = 0
        break

print('断网了')

cur.close()
conn.close()
