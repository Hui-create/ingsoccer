from scrapy.cmdline import execute


# execute(['scrapy', 'crawl', 'nba'])
execute(['scrapy', 'crawl', 'nba', '-o', 'ingsoccer.json'])
