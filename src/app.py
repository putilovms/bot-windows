import settings
from yclients import YClientsAPI

# from data import staff, staff_schedule

api = YClientsAPI(settings.PARTNER_TOKEN, settings.SALON_ID)

api.show_debugging()

# user_token = api.get_user_token(settings.LOGIN, settings.PASSWORD)
# print(user_token)

api.update_user_token(settings.USER_TOKEN)

staff = api.get_staff()

active_masters_id = YClientsAPI.get_active_staff_id(staff)

staff_schedule = api.get_staff_schedule(active_masters_id)

YClientsAPI.add_free_intervals(staff_schedule)
# print(staff_schedule)

YClientsAPI.add_staff_names(staff, staff_schedule)
# print(staff_schedule)

seance_length = 45*60
split_length = 60*60
free_windows = YClientsAPI.get_free_windows(
    staff_schedule,
    seance_length,
    split_length
)
print(free_windows)
