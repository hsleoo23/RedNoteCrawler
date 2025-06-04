import os
from loguru import logger
from apis.pc_apis import XHS_Apis
from xhs_utils.data_util import handle_note_info, download_note, save_to_xlsx
from xhs_utils.common_utils import init
import traceback

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
            if note_info is not None and success:
                note_list.append(note_info)
        for note_info in note_list:
            if save_choice == 'all' or save_choice == 'media':
                download_note(note_info, base_path['media'])
        if save_choice == 'all' or save_choice == 'excel':
            file_path = os.path.abspath(os.path.join(base_path['excel'], f'{excel_name}.xlsx'))
            save_to_xlsx(note_list, file_path)


    def spider_user_all_note(self, user_url: str, cookies_str: str, base_path: dict, save_choice: str, excel_name: str = '', proxies=None):
        """
        爬取一个用户的所有笔记
        :param user_url:
        :param cookies_str:
        :param base_path:
        :return:
        """
        note_list = []
        try:
            success, msg, all_note_info = self.xhs_apis.get_user_all_notes(user_url, cookies_str, proxies)
            if success:
                logger.info(f'用户 {user_url} 作品数量: {len(all_note_info)}')
                for simple_note_info in all_note_info:
                    note_url = f"https://www.xiaohongshu.com/explore/{simple_note_info['note_id']}?xsec_token={simple_note_info['xsec_token']}"
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = user_url.split('/')[-1].split('?')[0]
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'爬取用户所有视频 {user_url}: {success}, msg: {msg}')
        return note_list, success, msg

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

def spider_user_notes(user_url: str, cookies_str: str, save_choice: str = 'all'):
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
        note_list, success, msg = data_spider.spider_user_all_note(
            user_url=user_url,
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
    user_url = "https://www.xiaohongshu.com/user/profile/67d3a7a6000000000e01d708"
    cookies_str = "abRequestId=a9ac639c-07fe-5ca9-915e-b3ba128ced9e; a1=1972aaedecewwpiunuby9v2xpe1jvo55nzgbuinwn30000393812; webId=0207111d377f6f19a886ec15da29a115; gid=yjWJ00ddf4IjyjWJ00dfdu3ISdEEU37I7DvjkEIhJCUdyDq8Vhl227888qjqYyJ8qDSdW2DW; web_session=0400698c9f7a5056709b02910b3a4b70984845; xsecappid=xhs-pc-web; webBuild=4.67.0; loadts=1749003902290; acw_tc=0a0b118317490039027267564e7bf6f076797ff345fa476651b195f1e44576; websectiga=10f9a40ba454a07755a08f27ef8194c53637eba4551cf9751c009d9afb564467; sec_poison_id=7fd6b0cf-0cb3-4ebc-ab18-ce6bba9046da; unread={\"ub\":\"6838c0d3000000002001eee5\",\"ue\":\"681b459d0000000022007e19\",\"uc\":25}"
    
    # 调用爬虫函数
    success, msg, note_count = spider_user_notes(user_url, cookies_str)
    
    # 打印结果
    print(f"是否成功： {success}")
    print(f"信息： {msg}")
    print(f"笔记数量： {note_count}") 