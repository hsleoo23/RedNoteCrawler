from main import Data_Spider
from xhs_utils.common_utils import init
import traceback

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
    # 示例使用
    user_url = "https://www.xiaohongshu.com/user/profile/67d3a7a6000000000e01d708"
    cookies_str = (
        "abRequestId=a9ac639c-07fe-5ca9-915e-b3ba128ced9e; "
        "a1=1972aaedecewwpiunuby9v2xpe1jvo55nzgbuinwn30000393812; "
        "webId=0207111d377f6f19a886ec15da29a115; "
        "gid=yjWJ00ddf4IjyjWJ00dfdu3ISdEEU37I7DvjkEIhJCUdyDq8Vhl227888qjqYyJ8qDSdW2DW; "
        "webBuild=4.67.0; "
        "acw_tc=0ad59a0017489488706477956e7e9392cacf3169c9eafb997cea6e8c48726d; "
        "websectiga=10f9a40ba454a07755a08f27ef8194c53637eba4551cf9751c009d9afb564467; "
        "sec_poison_id=99a00f41-d902-4b2b-bc67-28808637f3de; "
        "web_session=0400698c9f7a5056709b02910b3a4b70984845; "
        "unread={\"ub\":\"683da151000000001101d0f5\",\"ue\":\"683e5d2a000000000f0304fb\",\"uc\":32}; "
        "xsecappid=xhs-pc-web; "
        "loadts=1748949377984"
    )
    
    note_list, success, msg = spider_user_notes(user_url, cookies_str)
    print("是否成功：", success)
    print("信息：", msg)
    print("笔记数量：", len(note_list) if note_list else 0) 