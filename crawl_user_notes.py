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
            success, msg, all_note_info = self.xhs_apis.get_user_all_notes(user_url, 200, cookies_str, proxies)
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
    cookies_str = "abRequestId=a9ac639c-07fe-5ca9-915e-b3ba128ced9e; a1=1972aaedecewwpiunuby9v2xpe1jvo55nzgbuinwn30000393812; webId=0207111d377f6f19a886ec15da29a115; gid=yjWJ00ddf4IjyjWJ00dfdu3ISdEEU37I7DvjkEIhJCUdyDq8Vhl227888qjqYyJ8qDSdW2DW; web_session=0400698c9f7a5056709b02910b3a4b70984845; webBuild=4.67.0; websectiga=634d3ad75ffb42a2ade2c5e1705a73c845837578aeb31ba0e442d75c648da36a; sec_poison_id=1a73fb82-548e-4108-aa15-d8aa2b039bad; xsecappid=xhs-pc-web; loadts=1749091586881; acw_tc=0a0bb12f17490915873463643ec479a4d69217c68f12ba5a1bbc8c4187fd5c; unread={%22ub%22:%226840f2fd00000000210007b3%22%2C%22ue%22:%226840dec60000000022034100%22%2C%22uc%22:25}"

    user_ids=['5f19b943000000000101f2a6','56fe74561c07df6b3f13ac38'
             ,'5c8efc4c000000001102ff42','5e9909620000000001008dce']

    for user_id in user_ids:
        user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
        print(f"\n开始爬取用户 {user_id} 的笔记...")
        
        # 调用爬虫函数
        note_list, success, msg = spider_user_notes(user_url, cookies_str)

        # 打印结果
        print(f"是否成功：{success}")
        print(f"信息：{msg}")
        if note_list:
            print(f"获取到 {len(note_list)} 条笔记")
        else:
            print("未获取到任何笔记")

