import threading
from repo_feature_crawler import start_crawler


tokens = [
    "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", # AndyLuo1029
    "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", # Doppelganger_Luo
    "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"  # small yxy
]

# comp = ['linkedin', 'facebook', 'google', 'amzn', 'youtube', 'pinterest', 'apple', 'oracle', 'intel', 'IBM', 'vmware', 'Netflix', 'salesforce', 'dell', 'Medium', 'tripadvisor', 'dropbox', 'JetBrains', 'pivotal', 'github', 'redhat-developer', 'square', 'groupon', 'Yelp', 'zynga', 'Juniper', 'docker', 'tenable', 'okta', 'cisco', 'paypal', 'eBay', 'yahoo', 'twitter', 'NVIDIA', 'Mastercard', 'HewlettPackard', 'nutanix', 'aol', 'docusign', 'Mirantis', 'alibaba', 'Tencent', 'baidu', 'bilibili', 'ctripcorp', 'qunarcorp', 'douban', 'NetEase', 'jobbole', 'vipshop', 'zhihu', 'Qihoo360', 'weibocom', 'HujiangTechnology', 'meitu', 'iuap-design', 'yued-fe', 'baixing', 'anjuke', 'lingochamp', 'Coding', 'haiwen', 'jpush', 'bytedance', 'meili', 'easemob', 'yyued', 'qiniu', 'linuxdeepin', 'xitu', 'iqiyi', 'FacePlusPlus', 'CodisLabs', 'citrix', 'airbnb', 'Instagram', 'uber', 'youzan', 'Meituan-Dianping', 'eleme', 'XiaoMi', 'Huawei', 'didi']
comp = [ 'google', 'amzn', 'youtube', 'pinterest', 'apple', 'oracle', 'intel', 'IBM', 'vmware', 'Netflix', 'salesforce', 'dell', 'Medium', 'tripadvisor', 'dropbox', 'JetBrains', 'pivotal', 'github', 'eBay', 'yahoo', 'twitter', 'NVIDIA', 'Mastercard', 'HewlettPackard', 'nutanix', 'aol', 'docusign', 'alibaba', 'Tencent', 'baidu', 'bilibili', 'ctripcorp', 'qunarcorp', 'douban', 'NetEase', 'jobbole', 'vipshop', 'zhihu', 'Qihoo360', 'weibocom', 'HujiangTechnology', 'meitu', 'iuap-design', 'yued-fe', 'baixing', 'anjuke', 'lingochamp', 'Coding', 'haiwen', 'jpush', 'bytedance', 'meili', 'easemob', 'yyued', 'qiniu', 'linuxdeepin', 'xitu', 'iqiyi', 'FacePlusPlus', 'CodisLabs', 'citrix', 'airbnb', 'Instagram', 'uber', 'youzan', 'Meituan-Dianping', 'eleme', 'XiaoMi', 'Huawei', 'didi']
comps = []
# print(len(comp)) 84
comps.append(comp[7:10])
comps.append(['Netflix'])
comps.append(['vmware'])



if __name__ == "__main__":
    # threads = []
    # for i in range(1,2):
    #     tempThread = threading.Thread(target=start_crawler, args=[comps[i],tokens[i]])
    #     threads.append(tempThread)
    # for t in threads:
    #     t.start()
    #     print("【Thread:】"+str(t.ident))

    # start_crawler(comps[0],tokens[0], 290792892)
    # start_crawler(comps[1],tokens[1], None)
    start_crawler(comps[2],tokens[2], 212820752)


    # print(comps[0][0],comps[0][-1])
    # print(comps[1][0],comps[1][-1])
    # print(comps[2][0],comps[2][-1])
