from scrapy import Spider, Request

from nba.items import NbaTeamItem


class NbaSpider(Spider):
    name = 'nba'

    def start_requests(self):
        url = 'https://www.rotowire.com/basketball/nba-lineups.php'
        yield Request(url=url, callback=self.parse)

    def parse_player(self, data):
        """解析单个运动员信息"""
        player_name = data.xpath('./a/text()').extract_first()
        position = data.xpath('./div/text()').extract_first()
        if data.xpath('./span/text()').extract_first():
            reason = data.xpath('./span/text()').extract_first()
        else:
            reason = ''
        player = {'player_name': player_name, 'position': position,
                               'reason': reason}
        return player
        # yield player

    def get_players(self, all_players):
        """对球队下的所有运动员进行解析"""
        status = all_players[0].xpath('./text()')[-1].extract().strip()
        # print(status)
        all_players = all_players[1:]
        all_players = all_players[:5] + all_players[6:]
        lineup_players = []
        injure_players = []
        for data in all_players[:5]:
            player = self.parse_player(data)
            lineup_players.append(player)
        for data in all_players[5:]:
            player = self.parse_player(data)
            # print(player)
            injure_players.append(player)
        # print('lineup_player', lineup_players)
        # print('injurie_player', injurie_players)
        return lineup_players, injure_players, status
        # yield lineup_players, injure_players, status

    def save_data(self, match_time, team_name, status, lineup_players, injure_players, rival_team_name):
        item = NbaTeamItem()
        item['match_time'] = match_time
        item['team_name'] = team_name
        item['status'] = status
        item['lineup_players'] = lineup_players
        item['injure_players'] = injure_players
        item['rival'] = rival_team_name
        yield item

    def parse_team_one(self, all_result, date):
        """解析第一个球队"""
        for data in all_result:
            match_time = data.xpath('./div/div/text()').extract_first()
            match_time = date + ' ' + match_time
            team_name = data.xpath('./div[2]/div/div/a/div/text()').extract_first()
            rival_team_name = data.xpath('./div[2]/div/div/a[2]/div/text()').extract_first()
            all_player = data.xpath('./div[2]/div[3]/ul[1]/li')
            lineup_players, injure_players, status = self.get_players(all_player)
            print(match_time, team_name, status, lineup_players, injure_players)
            self.save_data(match_time, team_name, status, lineup_players, injure_players, rival_team_name)
            # return match_time, team_name, status, lineup_players, injure_players, rival_team_name

    def parse_team_two(self, all_result, date):
        """解析第二个球队"""
        for data in all_result:
            match_time = data.xpath('./div/div/text()').extract_first()
            team_name = data.xpath('./div[2]/div/div/a[2]/div/text()').extract_first()
            rival_team_name = data.xpath('./div[2]/div/div/a/div/text()').extract_first()
            all_player = data.xpath('./div[2]/div[3]/ul[2]/li')
            lineup_players, injure_players, status = self.get_players(all_player)
            self.save_data(match_time, team_name, status, lineup_players, injure_players, rival_team_name)
            # return match_time, team_name, status, lineup_players, injure_players, rival_team_name

    def parse(self, response):
        date = response.selector.xpath('//*[@class="page-title__secondary"]/text()').extract_first().split('for')[-1]
        all_result = response.xpath('//*[@class="lineup is-nba has-started"]')
        if not all_result:
            all_result = response.xpath('//*[@class="lineup is-nba"]')
        # print(date)
        # print(all_result)
        self.parse_team_one(all_result, date)
        self.parse_team_two(all_result, date)
        # self.save_data(self.parse_team_one(all_result, date))
        # self.save_data(self.parse_team_two(all_result, date))
