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

    def get_players(self, all_players):
        """对球队下的所有运动员进行解析"""
        status = all_players[0].xpath('./text()')[-1].extract().strip()
        all_players = all_players[1:]
        all_players = all_players[:5] + all_players[6:]
        lineup_players = []
        injure_players = []
        for data in all_players[:5]:
            player = self.parse_player(data)
            lineup_players.append(player)
        for data in all_players[5:]:
            player = self.parse_player(data)
            injure_players.append(player)
        result = {'lineup_players': lineup_players, 'injure_players': injure_players, 'status': status}
        return result

    def parse_time(self, time):
        """解析时间"""
        if not time:
            return None
        time = time.strip()
        time_lists = time.split(' ')
        if time_lists[1] == 'PM':
            new_time = str(int(time_lists[0][0]) + 12) + time_lists[0][1:]
            utc_time = time_lists[-1] + new_time
            return utc_time

    def parse_team_one(self, all_result, utc_date, date):
        """解析第一个球队"""
        result = []
        for data in all_result:
            match_time = data.xpath('./div/div/text()').extract_first()
            match_time = utc_date + self.parse_time(match_time)
            match_time_old_style = date + ' ' + match_time
            team_name = data.xpath('./div[2]/div/div/a/div/text()').extract_first()
            rival_team_name = data.xpath('./div[2]/div/div/a[2]/div/text()').extract_first()
            all_player = data.xpath('./div[2]/div[3]/ul[1]/li')
            player_data = self.get_players(all_player)
            lineup_players, injure_players, status = player_data['lineup_players'], player_data['injure_players'], player_data['status']
            result.append({'match_time': match_time, 'match_time_old_style': match_time_old_style,
                           'team_name': team_name, 'status': status, 'lineup_players': lineup_players,
                           'injure_players': injure_players, 'rival_team_name': rival_team_name})
        return result

    def parse_team_two(self, all_result, utc_date, date):
        """解析第二个球队"""
        result = []
        for data in all_result:
            match_time = data.xpath('./div/div/text()').extract_first()
            match_time = utc_date + self.parse_time(match_time)
            match_time_old_style = date + ' ' + match_time
            team_name = data.xpath('./div[2]/div/div/a[2]/div/text()').extract_first()
            rival_team_name = data.xpath('./div[2]/div/div/a/div/text()').extract_first()
            all_player = data.xpath('./div[2]/div[3]/ul[2]/li')
            lineup_players, injure_players, status = self.get_players(all_player)
            result.append({'match_time': match_time, 'match_time_old_style': match_time_old_style,
                           'team_name': team_name, 'status': status, 'lineup_players': lineup_players,
                           'injure_players': injure_players, 'rival_team_name': rival_team_name})
        return result

    def parse_date(self, date):
        """解析月份"""
        month_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05',
                 'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10',
                 'Nov': '11', 'Dec': '12'}
        if date:
            date = date.replace(',', '')
            date_list = date.split(' ')
            month = month_dict[date_list[0][:3]]
            utc_date = date_list[-1] + '-' + month + '-' + date_list[1]
            return utc_date, date

    def parse(self, response):
        date = response.selector.xpath('//*[@class="page-title__secondary"]/text()').extract_first().split('for')[-1].strip()
        utc_date, date = self.parse_date(date)
        all_result = response.xpath('//*[@class="lineup is-nba has-started"]')
        if not all_result:
            all_result = response.xpath('//*[@class="lineup is-nba"]')
        result_1 = self.parse_team_one(all_result, utc_date, date)
        result_2 = self.parse_team_two(all_result, utc_date, date)
        result = result_1 + result_2
        for team_players in result:
            item = NbaTeamItem()
            item['match_time'] = team_players['match_time']
            item['match_time_old_style'] = team_players['match_time_old_style']
            item['team_name'] = team_players['team_name']
            item['status'] = team_players['status']
            item['lineup_players'] = team_players['lineup_players']
            item['injure_players'] = team_players['injure_players']
            item['rival'] = team_players['rival_team_name']
            yield item

