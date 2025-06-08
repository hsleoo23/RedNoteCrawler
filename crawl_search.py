import os
from loguru import logger
from apis.pc_apis import XHS_Apis
from xhs_utils.data_util import handle_note_info, download_note, save_to_xlsx
from xhs_utils.common_utils import init
import traceback
import time

class Data_Spider():
    def __init__(self):
        self.xhs_apis = XHS_Apis()

    def spider_note(self, note_url: str, cookies_str: str, proxies=None):
        """
        爬取一个笔记的信息
        :param note_url:
        :param cookies_str:
        :return:
        """
        note_info = None
        try:
            success, msg, note_info = self.xhs_apis.get_note_info(note_url, cookies_str, proxies)
            if success:
                note_info = note_info['data']['items'][0]
                note_info['url'] = note_url
                note_info = handle_note_info(note_info)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'爬取笔记信息 {note_url}: {success}, msg: {msg}')
        return success, msg, note_info

    def spider_some_note(self, notes: list, cookies_str: str, base_path: dict, save_choice: str, excel_name: str = '', proxies=None):
        """
        爬取一些笔记的信息
        :param notes:
        :param cookies_str:
        :param base_path:
        :return:
        """
        if (save_choice == 'all' or save_choice == 'excel') and excel_name == '':
            raise ValueError('excel_name 不能为空')
        note_list = []
        for note_url in notes:
            success, msg, note_info = self.spider_note(note_url, cookies_str, proxies)
            time.sleep(1)
            if note_info is not None and success:
                note_list.append(note_info)
        for note_info in note_list:
            if save_choice == 'all' or save_choice == 'media':
                download_note(note_info, base_path['media'])
        if save_choice == 'all' or save_choice == 'excel':
            file_path = os.path.abspath(os.path.join(base_path['excel'], f'{excel_name}.xlsx'))
            save_to_xlsx(note_list, file_path)


    def spider_some_search_note(self, query: str, require_num: int, cookies_str: str, base_path: dict, save_choice: str, sort="general", note_type=0,  excel_name: str = '', proxies=None):
        """
            指定数量搜索笔记，设置排序方式和笔记类型和笔记数量
            :param query 搜索的关键词
            :param require_num 搜索的数量
            :param cookies_str 你的cookies
            :param base_path 保存路径
            :param sort 排序方式 general:综合排序, time_descending:时间排序, popularity_descending:热度排序
            :param note_type 笔记类型 0:全部, 1:视频, 2:图文
            返回搜索的结果
        """
        note_list = []
        try:
            success, msg, notes = self.xhs_apis.search_some_note(query, require_num, cookies_str, sort, note_type, proxies)
            if success:
                notes = list(filter(lambda x: x['model_type'] == "note", notes))
                logger.info(f'搜索关键词 {query} 笔记数量: {len(notes)}')
                for note in notes:
                    note_url = f"https://www.xiaohongshu.com/explore/{note['id']}?xsec_token={note['xsec_token']}"
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = query
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'搜索关键词 {query} 笔记: {success}, msg: {msg}')
        return note_list, success, msg

def spider_user_notes(query: str, require_num: int,cookies_str: str, save_choice: str = 'excel'):
    """
    爬取用户的所有笔记
    :param user_url: 用户主页链接
    :param cookies_str: cookies字符串
    :param save_choice: 保存选项，可选值：'all'（保存所有信息）, 'media'（只保存媒体文件）, 'excel'（只保存到excel）
    :return: (note_list, success, msg)
    """
    try:
        # 初始化基础路径
        _, base_path = init()
        # 创建爬虫实例
        data_spider = Data_Spider()
        # 调用爬取用户所有笔记的方法
        note_list, success, msg = data_spider.spider_some_search_note(
            query=query,
            require_num=require_num,
            cookies_str=cookies_str,
            base_path=base_path,
            save_choice=save_choice
        )
        return note_list, success, msg
    except Exception as e:
        print("发生异常：", str(e))
        print("详细异常信息如下：")
        traceback.print_exc()
        return None, False, str(e)

if __name__ == "__main__":
    # 示例用户URL和cookies
    cookies_str = "abRequestId=a9ac639c-07fe-5ca9-915e-b3ba128ced9e; a1=1972aaedecewwpiunuby9v2xpe1jvo55nzgbuinwn30000393812; webId=0207111d377f6f19a886ec15da29a115; gid=yjWJ00ddf4IjyjWJ00dfdu3ISdEEU37I7DvjkEIhJCUdyDq8Vhl227888qjqYyJ8qDSdW2DW; webBuild=4.68.0; web_session=0400698c9f7a5056709b844f703a4bbd3a5850; unread={%22ub%22:%226835832e000000002101b202%22%2C%22ue%22:%226841c34d000000000c03a7de%22%2C%22uc%22:28}; websectiga=8886be45f388a1ee7bf611a69f3e174cae48f1ea02c0f8ec3256031b8be9c7ee; sec_poison_id=dccdf37a-6e0f-4026-8109-f6e5df23c4d8; xsecappid=ranchi; loadts=1749354781245"
    query="干敏肌"
    # 调用爬虫函数
    success, msg, note_count = spider_user_notes(query,200, cookies_str)

    # 打印结果
    print(f"是否成功： {success}")
    print(f"信息： {msg}")
    print(f"笔记数量： {note_count}")

