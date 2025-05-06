from src import settings
from src.yclients import YClientsAPI
from src.data import staff, staff_schedule


def get_free_windows():
    api = YClientsAPI(settings.PARTNER_TOKEN, settings.SALON_ID)
    api.update_user_token(settings.USER_TOKEN)
    staff = api.get_staff()
    # print(staff)
    staff_schedule = api.get_staff_schedule(staff, {"weeks": 2, "months": 0})
    # print(staff_schedule)
    seance_length = 45*60
    free_windows = YClientsAPI.get_free_windows(staff_schedule, seance_length)
    # print(free_windows)
    return free_windows


def get_free_intervals(seance_length, delta={"weeks": 2, "months": 0}):
    api = YClientsAPI(settings.PARTNER_TOKEN, settings.SALON_ID)
    api.update_user_token(settings.USER_TOKEN)
    staff = api.get_staff()
    staff_schedule = api.get_staff_schedule(staff, delta)
    free_intervals = YClientsAPI.get_free_intervals(
        staff_schedule, seance_length)
    # print(free_windows)
    return free_intervals
