from urllib.parse import urlencode
import httpx
import ujson
from datetime import datetime, timedelta
from collections import defaultdict


class YClientsAPI():
    def __init__(self, partner_token: str, salon_id: int):
        self.headers = {
            "Accept": "application/vnd.yclients.v2+json",
            "Authorization": f"Bearer {partner_token}",
            "Content-Type": "application/json",
        }
        self.salon_id = salon_id
        # if __show_debugging==True code will show debugging process
        self.__show_debugging = False

    def show_debugging(self):
        print("Debugging prints turned on")
        self.__show_debugging = True

    def hide_debugging(self):
        print("Debugging prints turned off")
        self.__show_debugging = False

    def get_user_token(self, login: str, password: str) -> str:
        """
        To read clients data you need to obtain user token
        :param login: yclients user login
        :param password: yclients user login
        :return: user token
        """
        url = "https://api.yclients.com/api/v1/auth"
        # url = 'https://webhook.site/96376a07-8af0-4439-8af0-2112662290af'
        querystring = {
            "login": login,
            "password": password
        }
        response = httpx.post(url, headers=self.headers, json=querystring)
        response_json = ujson.loads(response.text)
        if self.__show_debugging:
            print(f"response /auth {response_json}")
        user_token = response_json['data']['user_token']
        if self.__show_debugging:
            print(f"Obtained user token {user_token}")
        return user_token

    def update_user_token(self, user_token: str) -> None:
        """
        After user token was obtained you need to include it in
        header of requests that you are sending
        :param user_token: user token
        :return:
        """
        self.headers['Authorization'] = \
            self.headers['Authorization'] + f", User {user_token}"
        if self.__show_debugging:
            print(f"Updated autorisation parameters:"
                  f" {self.headers['Authorization']}")

    def get_staff(self, staff_id: int = None) -> dict:
        """ Return dict of staff for specific salon """
        staff_id = '' if staff_id is None else staff_id
        url = f'https://api.yclients.com/api/v1/company/{self.salon_id}/staff/{staff_id}'
        response = httpx.get(url, headers=self.headers)
        return ujson.loads(response.text)

    @staticmethod
    def get_active_staff_id(staff: dict, positions_titles: list = None) -> list:
        """ 
        Get a list of employees for whom an account is open. 
        Employees can be filtered by position name.
        """
        active_staff_id = []
        for employee in staff['data']:
            if (not employee['hidden']):
                if positions_titles is None:
                    active_staff_id.append(employee['id'])
                    continue
                if employee['position']['title'] in positions_titles:
                    active_staff_id.append(employee['id'])
        return active_staff_id

    def get_staff_schedule(self, staff_ids: list):
        url = f'https://api.yclients.com/api/v1/company/{self.salon_id}/staff/schedule'
        # url = 'https://webhook.site/96376a07-8af0-4439-8af0-2112662290af'
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=2)
        query_string = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
        }
        query_string.update({
            f'staff_ids[{i}]': staff_ids[i] for i in range(len(staff_ids))
        })
        query_string.update({
            'include[0]': 'busy_intervals',
            'include[1]': 'off_day_type'
        })
        response = httpx.get(url, headers=self.headers, params=query_string)
        if self.__show_debugging:
            print(f"/staff/schedule query_string - {query_string}")
            print(f"/staff/schedule Status code - {response.status_code}")
        return ujson.loads(response.text)

    def get_book_staff_seances(self, staff_id, service_ids: list = None):
        ''' Поиск ближайших сеансов для конкретного мастера (диапазоны поиска не известны) '''
        url = f'https://api.yclients.com/api/v1/book_staff_seances/{self.salon_id}/{staff_id}/'
        # TODO: Сделать фильтр по зонам по service_ids
        query_string = {}
        response = httpx.get(url, headers=self.headers, params=query_string)
        return ujson.loads(response.text)

    def get_book_times(self, date: str, staff_id: int = 0, service_ids: list = None):
        ''' Поиск всех окошек на конкретную дату (нет ID мастера, для которго найдены окошки)'''
        url = f'https://api.yclients.com/api/v1/book_times/{self.salon_id}/{staff_id}/{date}'
        # TODO: Сделать фильтр по зонам по service_ids
        query_string = {}
        response = httpx.get(url, headers=self.headers, params=query_string)
        return ujson.loads(response.text)

    @staticmethod
    def add_free_intervals(staff_schedule):
        for i in range(len(staff_schedule['data'])):
            busy_intervals = []
            for ii in range(len(staff_schedule['data'][i]['busy_intervals'])):
                start = datetime.strptime(
                    staff_schedule['data'][i]['busy_intervals'][ii]['from'], "%H:%M:%S")
                end = datetime.strptime(
                    staff_schedule['data'][i]['busy_intervals'][ii]['to'], "%H:%M:%S")
                busy_intervals.append((start, end))
                delta = end-start
                staff_schedule['data'][i]['busy_intervals'][ii]['seance_length'] = int(
                    delta.total_seconds())
            busy_intervals.sort()

            free_intervals = []
            for slot in staff_schedule['data'][i]['slots']:
                slot_start = datetime.strptime(slot['from'], "%H:%M")
                slot_end = datetime.strptime(slot['to'], "%H:%M")
                current = slot_start
                for busy_start, busy_end in busy_intervals:
                    # Если занятой интервал вне рабочего слота, пропускаем
                    if busy_end <= slot_start or busy_start >= slot_end:
                        continue
                    # Если между current и busy_start есть свободное время, добавляем
                    if current < busy_start:
                        free_from = current
                        free_to = min(busy_start, slot_end)
                        if free_from < free_to:
                            delta = free_to - free_from
                            free_intervals.append({
                                "from": free_from.strftime("%H:%M"),
                                "to": free_to.strftime("%H:%M"),
                                "free_length": int(delta.total_seconds()),
                            })
                    # Сдвигаем current на конец занятого интервала, если он в пределах слота
                    current = max(current, busy_end)
                    if current >= slot_end:
                        break
                # После последнего занятого интервала до конца рабочего слота
                if current < slot_end:
                    delta = free_to - free_from
                    free_intervals.append({
                        "from": current.strftime("%H:%M"),
                        "to": slot_end.strftime("%H:%M"),
                        "free_length": int(delta.total_seconds()),
                    })
            staff_schedule['data'][i]['free_intervals'] = free_intervals
        return staff_schedule

    @staticmethod
    def add_staff_names(staff, staff_schedule):
        staff_names = {}
        for employee in staff['data']:
            staff_names[employee['id']] = employee['name']
        for i in range(len(staff_schedule['data'])):
            staff_id = staff_schedule['data'][i]['staff_id']
            staff_schedule['data'][i]['name'] = staff_names[staff_id]
        return staff_schedule

    @staticmethod
    def get_free_windows(staff_schedule, seance_length, split_length):

        def filter_intervals(interval):
            return interval['free_length'] > seance_length

        def get_windows(free_intervals):
            windows = []
            for interval in free_intervals:
                start_time_str = interval['from']
                free_length = interval['free_length']

                # Переводим секунды в минуты
                total_minutes = free_length // 60

                # Рассчитываем количество часов
                full_hours = total_minutes // 60
                remainder = total_minutes % 60
                if remainder >= 45:
                    full_hours += 1

                # Парсим начальное время
                start_time = datetime.strptime(start_time_str, "%H:%M")

                # Генерируем стартовые времена окон
                for hour in range(full_hours):
                    window_time = start_time + timedelta(hours=hour)
                    windows.append(window_time.strftime("%H:%M"))

            return windows
        
        def format_date(date: str):
            dt = datetime.strptime(date, '%Y-%m-%d')
            weekdays = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
            new_date = dt.strftime('%d.%m') + ' ' + weekdays[dt.weekday()]
            return new_date


        # Группировка по staff_id
        staff_schedule_grouped = defaultdict(list)
        for entry in staff_schedule['data']:
            staff_id = entry['staff_id']
            staff_schedule_grouped[staff_id].append(entry)
        staff_schedule_grouped = dict(staff_schedule_grouped)

        # Формирование окошек
        staff_schedule_windows = {}
        for id, working_days in staff_schedule_grouped.items():
            staff_schedule_windows[id] = {}
            filtred_working_days = []
            for working_day in working_days:
                staff_schedule_windows[id]['name'] = working_day['name']
                working_day['free_intervals'] = list(
                    filter(filter_intervals, working_day['free_intervals']))
                if len(working_day['free_intervals']) > 0:
                    filtred_working_days.append({
                        'date': format_date(working_day['date']),
                        'free_intervals': working_day['free_intervals'],
                        'windows': get_windows(working_day['free_intervals'])
                    })
            staff_schedule_windows[id]['working_days'] = filtred_working_days
        return staff_schedule_windows
