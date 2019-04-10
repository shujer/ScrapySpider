#### 项目概要
论文数据爬取并清洗，存储到数据库
#### 爬取内容
1. 爬取万方数据的关键信息，包括：
- 标题(中/英)
- 作者(中/英)
- 关键词(中/英)
- 摘要(中/英)
- 出版日期
- doi
- 文章链接
- 搜索关键词

2. 爬取知网数据的关键信息，包括：
- 标题(中or英)
- 作者(中or英)
- 关键词(中or英)
- 摘要(中or英)
- 出版日期
- 论文类型
- 文章链接
- 搜索关键词

3. 运行命令
```
$ cd ScrapySpider/myspider
$ python run.py --help
$ python run.py cnki -k "地理" -m 10 #知网
$ python run.py cnki -k "地理" -m 10 #万方
$ python run.py wapcnki -k "地理" -m 10 #手机知网
```

补充：技术博客见[爬取中国知网CNKI的遇到的坑与技术总结](https://www.ephemeron.top/2018/12/03/pa-qu-zhong-guo-zhi-wang-cnki-de-yu-dao-de-keng-yu-ji-zhu-zong-jie/)
