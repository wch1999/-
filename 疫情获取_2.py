import requests
import re
from urllib.request import urlretrieve
import shutil
import os

#请求头信息
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    }



#获取每个json地址
def get_json_url_list(base_url):  # 定义函数，需要传入丁香医生首页url
    resp = requests.get(base_url, headers=headers) #向丁香医生发送get请求得到网页内容，并且用变量resp存储
    text = resp.content.decode('utf-8') #将网页内容转码为'utf-8'格式

    #对内容进行正则化，获得大洲名称，国家名称，每个国家疫情的json链接
    json_url_lists = re.findall(r"""
    continents.+?"(.+?)".+? # 获取大洲名称
    provinceName.+?"(.+?)".+? # 获取国家名称
    (https.+?json) # 获取疫情的json链接

    """, text, re.VERBOSE | re.DOTALL)
    # print(json_url_lists)
    return json_url_lists #返回一个列表，列表包含多个数组，每个数组包含三个元素，第一个是大洲名称，第二个是国家名称，第三个是该国家疫情json链接


def storeAndParse_json(json_url_lists):  # 获取所有的json文件并且储存

    with open('各国疫情数据.csv', 'w', encoding='utf-8') as f_all: #创建一个名为各国疫情.csv的文件
        f_all.write('{},{},{},{}\n'.format('name', 'type', 'value', 'date'))#先向csv文件内部写入四个值（首行）

        # 循环获取每个存储疫情信息的数组，并且用urlretrieve保存每个国家的疫情json文件，并用"大洲-国家.json"在指定位置存储存储
        for json_url_list in json_url_lists:
            urlretrieve(json_url_list[2], filename="json文件储存/"+json_url_list[0] + "-" + json_url_list[1] + ".json")  # 0:大洲，1：国家，2：json的url

            #向csv写入该国家的信息
            with open("json文件储存/"+json_url_list[0] + "-" + json_url_list[1] + ".json", encoding='utf-8') as f:
                contents = f.read()
                infos = re.findall(r"""

                .+?confirmedCount.+?:(\d+) # 获取该国家确诊人数
                .+?dateId.+?:(\d+) # 获取日期字符串

                """, contents, re.VERBOSE | re.DOTALL)

                for info in infos:#循环读取该国家疫情信息（三个属性：国家，确诊人数，日期）其中，日期格式为"00000000"形式

                    # 提取字符串日期，将"00000000"形式转化为"0000-00-00"的形式,并且用变量time储存
                    time_all = re.findall(r'(....)(..)(..)', info[1])
                    time = time_all[0][0] + "-" + time_all[0][1] + "-" + time_all[0][2]
                    # print("日期:" + time + "累计确诊:" + info[0])

                    #写入数据
                    f_all.write('{},{},{},{}\n'.format(json_url_list[1], json_url_list[0], info[0], time))


def main():
    os.mkdir('json文件储存')
    base_url = "https://ncov.dxy.cn/ncovh5/view/pneumonia?source="
    json_url_lists = get_json_url_list(base_url)
    storeAndParse_json(json_url_lists)
    shutil.rmtree("json文件储存")


if __name__ == '__main__':
    main()